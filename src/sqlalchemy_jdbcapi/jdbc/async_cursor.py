"""
Async JDBC Cursor implementation for SQLAlchemy asyncio support.

Wraps the synchronous JDBC cursor with asyncio.to_thread() for
non-blocking database operations.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Sequence

from .cursor import Cursor
from .exceptions import InterfaceError

logger = logging.getLogger(__name__)


class AsyncCursor:
    """
    Async DB-API 2.0 compliant cursor for JDBC.

    This class wraps the synchronous Cursor using asyncio.to_thread()
    to provide non-blocking database operations.

    Usage:
        cursor = await conn.cursor()
        await cursor.execute("SELECT * FROM users WHERE id = ?", (1,))
        row = await cursor.fetchone()
        await cursor.close()
    """

    def __init__(self, sync_cursor: Cursor) -> None:
        """
        Create an async cursor wrapper.

        Args:
            sync_cursor: The underlying synchronous Cursor
        """
        self._sync_cursor = sync_cursor
        self._closed = False

    async def execute(
        self,
        operation: str,
        parameters: Sequence[Any] | None = None,
    ) -> AsyncCursor:
        """
        Execute a database operation asynchronously.

        Args:
            operation: SQL query string
            parameters: Query parameters

        Returns:
            Self for method chaining

        Raises:
            ProgrammingError: If query is invalid
            DatabaseError: If execution fails
        """
        if self._closed:
            raise InterfaceError("Cursor is closed")

        await asyncio.to_thread(self._sync_cursor.execute, operation, parameters)
        return self

    async def executemany(
        self,
        operation: str,
        seq_of_parameters: Sequence[Sequence[Any]],
    ) -> AsyncCursor:
        """
        Execute a database operation multiple times asynchronously.

        Args:
            operation: SQL query string
            seq_of_parameters: Sequence of parameter sequences

        Returns:
            Self for method chaining
        """
        if self._closed:
            raise InterfaceError("Cursor is closed")

        await asyncio.to_thread(
            self._sync_cursor.executemany, operation, seq_of_parameters
        )
        return self

    async def fetchone(self) -> tuple[Any, ...] | None:
        """
        Fetch the next row of a query result set asynchronously.

        Returns:
            Single row as tuple, or None if no more rows
        """
        if self._closed:
            raise InterfaceError("Cursor is closed")

        return await asyncio.to_thread(self._sync_cursor.fetchone)

    async def fetchmany(self, size: int | None = None) -> list[tuple[Any, ...]]:
        """
        Fetch the next set of rows asynchronously.

        Args:
            size: Number of rows to fetch (default: arraysize)

        Returns:
            List of rows as tuples
        """
        if self._closed:
            raise InterfaceError("Cursor is closed")

        if size is None:
            size = self._sync_cursor.arraysize

        return await asyncio.to_thread(self._sync_cursor.fetchmany, size)

    async def fetchall(self) -> list[tuple[Any, ...]]:
        """
        Fetch all remaining rows asynchronously.

        Returns:
            List of all remaining rows as tuples
        """
        if self._closed:
            raise InterfaceError("Cursor is closed")

        return await asyncio.to_thread(self._sync_cursor.fetchall)

    async def close(self) -> None:
        """Close the cursor asynchronously."""
        if self._closed:
            return

        try:
            await asyncio.to_thread(self._sync_cursor.close)
        finally:
            self._closed = True

    @property
    def description(self) -> tuple[tuple[Any, ...], ...] | None:
        """
        Get column descriptions.

        Returns sequence of 7-item tuples:
        (name, type_code, display_size, internal_size, precision, scale, null_ok)
        """
        return self._sync_cursor.description

    @property
    def rowcount(self) -> int:
        """
        Get number of rows affected by last operation.

        Returns -1 if unknown.
        """
        return self._sync_cursor.rowcount

    @property
    def arraysize(self) -> int:
        """Get default fetch size."""
        return self._sync_cursor.arraysize

    @arraysize.setter
    def arraysize(self, value: int) -> None:
        """Set default fetch size."""
        self._sync_cursor.arraysize = value

    @property
    def lastrowid(self) -> int | None:
        """Get last inserted row ID (if available)."""
        return self._sync_cursor.lastrowid

    @property
    def sync_cursor(self) -> Cursor:
        """Get the underlying synchronous cursor."""
        return self._sync_cursor

    def setinputsizes(self, sizes: Sequence[Any]) -> None:
        """Set input sizes (no-op for compatibility)."""
        self._sync_cursor.setinputsizes(sizes)

    def setoutputsize(self, size: int, column: int | None = None) -> None:
        """Set output size (no-op for compatibility)."""
        self._sync_cursor.setoutputsize(size, column)

    async def __aenter__(self) -> AsyncCursor:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def __aiter__(self) -> AsyncCursor:
        """Return iterator for async iteration over rows."""
        return self

    async def __anext__(self) -> tuple[Any, ...]:
        """Get next row in async iteration."""
        row = await self.fetchone()
        if row is None:
            raise StopAsyncIteration
        return row
