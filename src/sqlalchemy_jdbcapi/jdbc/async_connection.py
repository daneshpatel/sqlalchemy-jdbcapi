"""
Async JDBC Connection implementation for SQLAlchemy asyncio support.

Wraps the synchronous JDBC connection with asyncio.to_thread() for
non-blocking database operations.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from .async_cursor import AsyncCursor
from .connection import Connection
from .exceptions import InterfaceError

logger = logging.getLogger(__name__)


class AsyncConnection:
    """
    Async DB-API 2.0 compliant connection to a JDBC database.

    This class wraps the synchronous Connection using asyncio.to_thread()
    to provide non-blocking database operations for use with SQLAlchemy's
    async engine and session.

    Usage:
        async with await async_connect(...) as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM users")
            rows = await cursor.fetchall()
    """

    def __init__(self, sync_connection: Connection) -> None:
        """
        Create an async connection wrapper.

        Args:
            sync_connection: The underlying synchronous Connection
        """
        self._sync_connection = sync_connection
        self._closed = False

    @classmethod
    async def create(
        cls,
        jclassname: str,
        url: str,
        driver_args: dict[str, Any] | list[Any] | None = None,
        jars: list[str] | None = None,
        libs: list[str] | None = None,
        timeout: float | None = None,
    ) -> AsyncConnection:
        """
        Create an async JDBC connection.

        This is a factory method that creates the underlying synchronous
        connection in a thread pool to avoid blocking the event loop.

        Args:
            jclassname: Fully qualified Java class name of JDBC driver
            url: JDBC connection URL
            driver_args: Connection properties (dict) or [user, password] (list)
            jars: List of JAR file paths (for classpath)
            libs: Additional native library paths
            timeout: Connection timeout in seconds (None = no timeout)

        Returns:
            AsyncConnection instance

        Raises:
            InterfaceError: If JVM or driver cannot be loaded
            DatabaseError: If connection fails
            asyncio.TimeoutError: If timeout is exceeded
        """
        coro = asyncio.to_thread(
            Connection,
            jclassname,
            url,
            driver_args,
            jars,
            libs,
        )

        if timeout is not None:
            sync_conn = await asyncio.wait_for(coro, timeout=timeout)
        else:
            sync_conn = await coro

        return cls(sync_conn)

    async def close(self) -> None:
        """Close the connection asynchronously."""
        if self._closed:
            return

        try:
            await asyncio.to_thread(self._sync_connection.close)
        finally:
            self._closed = True

    async def commit(self) -> None:
        """Commit current transaction asynchronously."""
        if self._closed:
            raise InterfaceError("Connection is closed")

        await asyncio.to_thread(self._sync_connection.commit)

    async def rollback(self) -> None:
        """Rollback current transaction asynchronously."""
        if self._closed:
            raise InterfaceError("Connection is closed")

        await asyncio.to_thread(self._sync_connection.rollback)

    async def cursor(self) -> AsyncCursor:
        """
        Create a new async cursor.

        Returns:
            AsyncCursor object

        Raises:
            InterfaceError: If connection is closed
        """
        if self._closed:
            raise InterfaceError("Connection is closed")

        # Run cursor creation in thread for thread safety
        # JDBC cursor creation may involve JVM calls
        sync_cursor = await asyncio.to_thread(self._sync_connection.cursor)
        return AsyncCursor(sync_cursor)

    async def set_auto_commit(self, auto_commit: bool) -> None:
        """
        Set auto-commit mode asynchronously.

        Args:
            auto_commit: True to enable auto-commit, False to disable
        """
        if self._closed:
            raise InterfaceError("Connection is closed")

        await asyncio.to_thread(self._sync_connection.set_auto_commit, auto_commit)

    async def get_auto_commit(self) -> bool:
        """Get current auto-commit mode asynchronously."""
        if self._closed:
            raise InterfaceError("Connection is closed")

        return await asyncio.to_thread(self._sync_connection.get_auto_commit)

    @property
    def closed(self) -> bool:
        """Check if connection is closed."""
        return self._closed

    @property
    def sync_connection(self) -> Connection:
        """Get the underlying synchronous connection."""
        return self._sync_connection

    # Expose the JDBC connection for SQLAlchemy dialect
    @property
    def jconn(self) -> Any:
        """Get the underlying JDBC connection object."""
        return self._sync_connection._jdbc_connection

    async def __aenter__(self) -> AsyncConnection:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self.close()


async def async_connect(
    jclassname: str,
    url: str,
    driver_args: dict[str, Any] | list[Any] | None = None,
    jars: list[str] | None = None,
    libs: list[str] | None = None,
    timeout: float | None = None,
) -> AsyncConnection:
    """
    Create an async JDBC database connection.

    This is the main entry point for creating async connections.

    Args:
        jclassname: Fully qualified Java class name of JDBC driver
        url: JDBC connection URL
        driver_args: Connection properties (dict) or [user, password] (list)
        jars: List of JAR file paths for classpath
        libs: Additional native library paths
        timeout: Connection timeout in seconds (None = no timeout)

    Returns:
        AsyncConnection object

    Raises:
        asyncio.TimeoutError: If timeout is exceeded

    Example:
        >>> conn = await async_connect(
        ...     'org.postgresql.Driver',
        ...     'jdbc:postgresql://localhost:5432/mydb',
        ...     {'user': 'myuser', 'password': 'mypass'},
        ...     timeout=30.0
        ... )
        >>> cursor = await conn.cursor()
        >>> await cursor.execute('SELECT * FROM users')
        >>> rows = await cursor.fetchall()
        >>> await conn.close()
    """
    return await AsyncConnection.create(
        jclassname=jclassname,
        url=url,
        driver_args=driver_args,
        jars=jars,
        libs=libs,
        timeout=timeout,
    )
