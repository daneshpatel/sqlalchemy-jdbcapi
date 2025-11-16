"""
JDBC Cursor implementation following DB-API 2.0 specification.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

from .exceptions import (
    DataError,
    InterfaceError,
    ProgrammingError,
)
from .type_converter import TypeConverter

logger = logging.getLogger(__name__)


class Cursor:
    """
    DB-API 2.0 compliant cursor for JDBC connections.

    This class wraps a JDBC Statement/PreparedStatement and ResultSet.
    """

    def __init__(self, connection: Any, jdbc_connection: Any) -> None:
        """
        Initialize cursor.

        Args:
            connection: Parent Connection object
            jdbc_connection: JDBC Connection object from JPype
        """
        self._connection = connection
        self._jdbc_connection = jdbc_connection

        # These will be set when we execute queries
        self._jdbc_statement: Any = None
        self._jdbc_resultset: Any = None

        # DB-API 2.0 spec requires these attributes
        self._description: tuple[tuple[str, ...], ...] | None = None
        self._rowcount: int = -1  # -1 means "unknown" per DB-API spec
        self._arraysize: int = 1  # default fetch size

        # We handle type conversion ourselves since JDBC types don't map 1:1 to Python
        self._type_converter = TypeConverter()
        self._closed = False

    @property
    def description(
        self,
    ) -> tuple[tuple[str, Any, None, None, None, None, None], ...] | None:
        """
        Get column descriptions from last query.

        Returns 7-item tuples: (name, type_code, display_size, internal_size,
        precision, scale, null_ok). We only provide name and type_code.
        """
        return self._description

    @property
    def rowcount(self) -> int:
        """Get number of rows affected by last operation."""
        return self._rowcount

    @property
    def arraysize(self) -> int:
        """Get default number of rows to fetch."""
        return self._arraysize

    @arraysize.setter
    def arraysize(self, size: int) -> None:
        """Set default number of rows to fetch."""
        self._arraysize = size

    def close(self) -> None:
        """Close the cursor."""
        if self._closed:
            return

        try:
            if self._jdbc_resultset is not None:
                self._jdbc_resultset.close()
            if self._jdbc_statement is not None:
                self._jdbc_statement.close()
        except Exception as e:
            logger.warning(f"Error closing cursor: {e}")
        finally:
            self._jdbc_resultset = None
            self._jdbc_statement = None
            self._closed = True

    def execute(
        self, operation: str, parameters: Sequence[Any] | None = None
    ) -> Cursor:
        """
        Execute a database operation.

        Args:
            operation: SQL query or command
            parameters: Parameters for the query

        Returns:
            Self for chaining

        Raises:
            ProgrammingError: If cursor is closed or operation fails
        """
        if self._closed:
            raise InterfaceError("Cursor is closed")

        try:
            # Close previous statement and resultset
            if self._jdbc_statement is not None:
                self._jdbc_statement.close()
            if self._jdbc_resultset is not None:
                self._jdbc_resultset.close()

            self._description = None
            self._rowcount = -1

            # Prepare statement
            if parameters:
                self._jdbc_statement = self._jdbc_connection.prepareStatement(operation)
                self._bind_parameters(self._jdbc_statement, parameters)
                has_resultset = self._jdbc_statement.execute()
            else:
                self._jdbc_statement = self._jdbc_connection.createStatement()
                has_resultset = self._jdbc_statement.execute(operation)

            # Process results
            if has_resultset:
                self._jdbc_resultset = self._jdbc_statement.getResultSet()
                self._build_description()
            else:
                self._rowcount = self._jdbc_statement.getUpdateCount()

            return self

        except Exception as e:
            logger.exception(f"Execute failed: {e}")
            raise ProgrammingError(f"Failed to execute operation: {e}") from e

    def executemany(
        self, operation: str, seq_of_parameters: Sequence[Sequence[Any]]
    ) -> None:
        """
        Execute a database operation multiple times.

        Args:
            operation: SQL query or command
            seq_of_parameters: Sequence of parameter sequences

        Raises:
            ProgrammingError: If operation fails
        """
        if self._closed:
            raise InterfaceError("Cursor is closed")

        try:
            self._jdbc_statement = self._jdbc_connection.prepareStatement(operation)

            for parameters in seq_of_parameters:
                self._bind_parameters(self._jdbc_statement, parameters)
                self._jdbc_statement.addBatch()

            results = self._jdbc_statement.executeBatch()
            self._rowcount = sum(r for r in results if r >= 0)

        except Exception as e:
            logger.exception(f"ExecuteManyJDBC failed: {e}")
            raise ProgrammingError(f"Failed to execute batch: {e}") from e

    def fetchone(self) -> tuple[Any, ...] | None:
        """
        Fetch next row from query result.

        Returns:
            Tuple of column values or None if no more rows

        Raises:
            InterfaceError: If no query has been executed
        """
        if self._jdbc_resultset is None:
            raise InterfaceError("No query has been executed")

        try:
            if self._jdbc_resultset.next():
                return self._fetch_row()
            return None
        except Exception as e:
            raise DataError(f"Failed to fetch row: {e}") from e

    def fetchmany(self, size: int | None = None) -> list[tuple[Any, ...]]:
        """
        Fetch multiple rows from query result.

        Args:
            size: Number of rows to fetch (default: arraysize)

        Returns:
            List of row tuples

        Raises:
            InterfaceError: If no query has been executed
        """
        if self._jdbc_resultset is None:
            raise InterfaceError("No query has been executed")

        if size is None:
            size = self._arraysize

        rows = []
        try:
            for _ in range(size):
                if self._jdbc_resultset.next():
                    rows.append(self._fetch_row())
                else:
                    break
            return rows
        except Exception as e:
            raise DataError(f"Failed to fetch rows: {e}") from e

    def fetchall(self) -> list[tuple[Any, ...]]:
        """
        Fetch all remaining rows from query result.

        Returns:
            List of row tuples

        Raises:
            InterfaceError: If no query has been executed
        """
        if self._jdbc_resultset is None:
            raise InterfaceError("No query has been executed")

        rows = []
        try:
            while self._jdbc_resultset.next():
                rows.append(self._fetch_row())
            return rows
        except Exception as e:
            raise DataError(f"Failed to fetch all rows: {e}") from e

    def setinputsizes(self, sizes: Sequence[int | None]) -> None:
        """Does nothing, for DB-API 2.0 compliance."""
        # JDBC handles this automatically, so we just ignore it

    def setoutputsize(self, size: int, column: int | None = None) -> None:
        """Does nothing, for DB-API 2.0 compliance."""
        # Same as above - JDBC doesn't need this hint

    def _bind_parameters(self, statement: Any, parameters: Sequence[Any]) -> None:
        """Bind parameters to prepared statement."""
        # JDBC uses 1-based indexing for parameters (yeah, I know...)
        for i, param in enumerate(parameters, start=1):
            if param is None:
                # NULL values need special handling in JDBC
                statement.setNull(i, 0)  # 0 = java.sql.Types.NULL
            else:
                # setObject auto-converts Python types to Java
                statement.setObject(i, param)

    def _build_description(self) -> None:
        """Build column description from ResultSetMetaData."""
        if self._jdbc_resultset is None:
            return

        try:
            metadata = self._jdbc_resultset.getMetaData()
            column_count = metadata.getColumnCount()

            description = []
            for i in range(1, column_count + 1):
                name = metadata.getColumnName(i)
                type_code = metadata.getColumnType(i)
                description.append(
                    (
                        name,
                        type_code,
                        None,  # display_size
                        None,  # internal_size
                        None,  # precision
                        None,  # scale
                        None,  # null_ok
                    )
                )

            self._description = tuple(description)

        except Exception as e:
            logger.warning(f"Failed to build description: {e}")
            self._description = None

    def _fetch_row(self) -> tuple[Any, ...]:
        """Fetch a single row and convert types."""
        if self._jdbc_resultset is None or self._description is None:
            return ()

        row = []
        for i, (name, type_code, *_) in enumerate(self._description, start=1):
            value = self._type_converter.convert_from_jdbc(
                self._jdbc_resultset, i, type_code
            )
            row.append(value)

        return tuple(row)

    def __enter__(self) -> Cursor:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def __iter__(self) -> Cursor:
        """Make cursor iterable."""
        return self

    def __next__(self) -> tuple[Any, ...]:
        """Fetch next row for iteration."""
        row = self.fetchone()
        if row is None:
            raise StopIteration
        return row
