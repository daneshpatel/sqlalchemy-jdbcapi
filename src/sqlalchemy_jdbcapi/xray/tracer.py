"""
Query tracing for automatic performance monitoring.

Provides cursor wrappers that automatically trace query execution
and report metrics to the database monitor.
"""

from __future__ import annotations

import logging
import time
import traceback
from collections.abc import Sequence
from typing import Any

from .monitor import DatabaseMonitor, get_global_monitor

logger = logging.getLogger(__name__)


class TracedCursor:
    """
    Cursor wrapper that automatically traces query execution.

    Wraps a DB-API cursor and records metrics for all executed queries.

    Example:
        >>> from sqlalchemy_jdbcapi.xray import TracedCursor, DatabaseMonitor
        >>> monitor = DatabaseMonitor()
        >>> cursor = conn.cursor()
        >>> traced = TracedCursor(cursor, monitor)
        >>> traced.execute("SELECT * FROM users")
        >>> rows = traced.fetchall()
    """

    def __init__(
        self,
        cursor: Any,
        monitor: DatabaseMonitor | None = None,
        capture_stack: bool = False,
    ) -> None:
        """
        Create a traced cursor.

        Args:
            cursor: The underlying DB-API cursor to wrap
            monitor: DatabaseMonitor instance (uses global if None)
            capture_stack: Whether to capture stack traces
        """
        self._cursor = cursor
        self._monitor = monitor or get_global_monitor()
        self._capture_stack = capture_stack
        self._last_query: str | None = None
        self._last_params: tuple[Any, ...] | None = None

    def execute(
        self,
        operation: str,
        parameters: Sequence[Any] | None = None,
    ) -> TracedCursor:
        """
        Execute a query with automatic tracing.

        Args:
            operation: SQL query string
            parameters: Query parameters

        Returns:
            Self for method chaining
        """
        self._last_query = operation
        self._last_params = tuple(parameters) if parameters else None

        # Capture stack trace if enabled (for future diagnostic features)
        if self._capture_stack:
            _ = "".join(traceback.format_stack()[:-1])

        start_time = time.perf_counter()
        error_msg = None
        success = True

        try:
            self._cursor.execute(operation, parameters)
        except Exception as e:
            success = False
            error_msg = str(e)
            raise
        finally:
            execution_time = time.perf_counter() - start_time

            # Get rowcount if available
            rows_affected = getattr(self._cursor, "rowcount", -1)
            if rows_affected == -1:
                rows_affected = 0

            # Record the query
            self._monitor.record_query(
                query=operation,
                execution_time=execution_time,
                success=success,
                rows_affected=rows_affected,
                error=error_msg,
                parameters=self._last_params,
            )

        return self

    def executemany(
        self,
        operation: str,
        seq_of_parameters: Sequence[Sequence[Any]],
    ) -> TracedCursor:
        """
        Execute a query multiple times with tracing.

        Args:
            operation: SQL query string
            seq_of_parameters: Sequence of parameter sequences

        Returns:
            Self for method chaining
        """
        self._last_query = operation
        self._last_params = None

        start_time = time.perf_counter()
        error_msg = None
        success = True

        try:
            self._cursor.executemany(operation, seq_of_parameters)
        except Exception as e:
            success = False
            error_msg = str(e)
            raise
        finally:
            execution_time = time.perf_counter() - start_time

            rows_affected = getattr(self._cursor, "rowcount", -1)
            if rows_affected == -1:
                rows_affected = len(seq_of_parameters)

            # Record as a single batch operation
            self._monitor.record_query(
                query=f"BATCH({len(seq_of_parameters)}): {operation}",
                execution_time=execution_time,
                success=success,
                rows_affected=rows_affected,
                error=error_msg,
            )

        return self

    def fetchone(self) -> tuple[Any, ...] | None:
        """Fetch the next row."""
        return self._cursor.fetchone()

    def fetchmany(self, size: int | None = None) -> list[tuple[Any, ...]]:
        """Fetch the next set of rows."""
        if size is None:
            return self._cursor.fetchmany()
        return self._cursor.fetchmany(size)

    def fetchall(self) -> list[tuple[Any, ...]]:
        """Fetch all remaining rows."""
        return self._cursor.fetchall()

    def close(self) -> None:
        """Close the cursor."""
        self._cursor.close()

    @property
    def description(self) -> tuple[tuple[Any, ...], ...] | None:
        """Get column descriptions."""
        return self._cursor.description

    @property
    def rowcount(self) -> int:
        """Get number of rows affected."""
        return self._cursor.rowcount

    @property
    def arraysize(self) -> int:
        """Get default fetch size."""
        return self._cursor.arraysize

    @arraysize.setter
    def arraysize(self, value: int) -> None:
        """Set default fetch size."""
        self._cursor.arraysize = value

    @property
    def lastrowid(self) -> int | None:
        """Get last inserted row ID."""
        return getattr(self._cursor, "lastrowid", None)

    def setinputsizes(self, sizes: Sequence[Any]) -> None:
        """Set input sizes."""
        self._cursor.setinputsizes(sizes)

    def setoutputsize(self, size: int, column: int | None = None) -> None:
        """Set output size."""
        self._cursor.setoutputsize(size, column)

    def __iter__(self):
        """Iterate over results."""
        return iter(self._cursor)

    def __enter__(self) -> TracedCursor:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()


class QueryTracer:
    """
    Query tracer that can be attached to connections.

    Provides automatic tracing for all queries executed through
    traced connections.

    Example:
        >>> tracer = QueryTracer()
        >>> traced_conn = tracer.trace_connection(conn)
        >>> cursor = traced_conn.cursor()  # Returns TracedCursor
        >>> cursor.execute("SELECT 1")
        >>> print(tracer.monitor.get_summary())
    """

    def __init__(
        self,
        monitor: DatabaseMonitor | None = None,
        capture_stack: bool = False,
    ) -> None:
        """
        Create a query tracer.

        Args:
            monitor: DatabaseMonitor to use (creates new if None)
            capture_stack: Whether to capture stack traces
        """
        self.monitor = monitor or DatabaseMonitor()
        self.capture_stack = capture_stack

    def trace_cursor(self, cursor: Any) -> TracedCursor:
        """
        Wrap a cursor with tracing.

        Args:
            cursor: DB-API cursor to trace

        Returns:
            TracedCursor wrapper
        """
        return TracedCursor(cursor, self.monitor, self.capture_stack)

    def trace_connection(self, connection: Any) -> TracedConnection:
        """
        Wrap a connection with tracing.

        Args:
            connection: DB-API connection to trace

        Returns:
            TracedConnection wrapper
        """
        return TracedConnection(connection, self)


class TracedConnection:
    """
    Connection wrapper that returns traced cursors.

    All cursors created from this connection will automatically
    trace their queries.
    """

    def __init__(self, connection: Any, tracer: QueryTracer) -> None:
        """
        Create a traced connection.

        Args:
            connection: The underlying DB-API connection
            tracer: QueryTracer instance
        """
        self._connection = connection
        self._tracer = tracer
        self._tracer.monitor.record_connection_open()

    def cursor(self) -> TracedCursor:
        """Create a traced cursor."""
        cursor = self._connection.cursor()
        return self._tracer.trace_cursor(cursor)

    def commit(self) -> None:
        """Commit the transaction."""
        self._connection.commit()

    def rollback(self) -> None:
        """Rollback the transaction."""
        self._connection.rollback()

    def close(self) -> None:
        """Close the connection."""
        self._connection.close()
        self._tracer.monitor.record_connection_close()

    @property
    def closed(self) -> bool:
        """Check if connection is closed."""
        return getattr(self._connection, "closed", False)

    def __enter__(self) -> TracedConnection:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()
