"""
ODBC connection wrapper.

Provides a thin wrapper around pyodbc connections for consistency with
the JDBC bridge interface.
"""

from __future__ import annotations

import logging
from typing import Any

from .exceptions import (
    DatabaseError,
    InterfaceError,
)

logger = logging.getLogger(__name__)


class Connection:
    """
    ODBC connection wrapper.

    Wraps pyodbc.Connection to provide a consistent interface with the JDBC bridge.
    """

    def __init__(self, pyodbc_connection: Any) -> None:
        """
        Initialize ODBC connection wrapper.

        Args:
            pyodbc_connection: Underlying pyodbc connection object.
        """
        self._connection = pyodbc_connection
        self._closed = False

    def cursor(self) -> Any:
        """
        Create a new cursor.

        Returns:
            Cursor object.
        """
        if self._closed:
            raise InterfaceError("Connection is closed")
        return self._connection.cursor()

    def commit(self) -> None:
        """Commit the current transaction."""
        if self._closed:
            raise InterfaceError("Connection is closed")
        try:
            self._connection.commit()
        except Exception as e:
            raise DatabaseError(f"Failed to commit transaction: {e}") from e

    def rollback(self) -> None:
        """Roll back the current transaction."""
        if self._closed:
            raise InterfaceError("Connection is closed")
        try:
            self._connection.rollback()
        except Exception as e:
            raise DatabaseError(f"Failed to rollback transaction: {e}") from e

    def close(self) -> None:
        """Close the connection."""
        if not self._closed:
            self._connection.close()
            self._closed = True

    def __enter__(self) -> Connection:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.close()

    @property
    def closed(self) -> bool:
        """Check if connection is closed."""
        return self._closed


def connect(
    connection_string: str,
    autocommit: bool = False,
    timeout: int | None = None,
    **kwargs: Any,
) -> Connection:
    """
    Create an ODBC connection.

    Args:
        connection_string: ODBC connection string.
        autocommit: Enable autocommit mode.
        timeout: Connection timeout in seconds.
        **kwargs: Additional connection parameters.

    Returns:
        ODBC Connection object.

    Raises:
        InterfaceError: If pyodbc is not installed.
        DatabaseError: If connection fails.
    """
    try:
        import pyodbc
    except ImportError as e:
        raise InterfaceError(
            "pyodbc is not installed. Install with: pip install pyodbc"
        ) from e

    try:
        # Build connection string with parameters
        params = dict(kwargs)
        if timeout is not None:
            params["timeout"] = timeout
        if autocommit:
            params["autocommit"] = True

        # Create connection
        conn = pyodbc.connect(connection_string, **params)

        logger.info("ODBC connection established")
        return Connection(conn)

    except pyodbc.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        raise DatabaseError(f"Failed to connect: {e}") from e
