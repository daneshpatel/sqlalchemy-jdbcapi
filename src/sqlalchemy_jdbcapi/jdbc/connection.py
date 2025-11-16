"""
JDBC Connection implementation following DB-API 2.0 specification.
"""

from __future__ import annotations

import logging
from typing import Any

from .cursor import Cursor
from .exceptions import DatabaseError, InterfaceError
from .jvm import start_jvm

logger = logging.getLogger(__name__)


class Connection:
    """
    DB-API 2.0 compliant connection to a JDBC database.

    This class wraps a JDBC Connection object from JPype.
    """

    def __init__(
        self,
        jclassname: str,
        url: str,
        driver_args: dict[str, Any] | list[Any] | None = None,
        jars: list[str] | None = None,
        libs: list[str] | None = None,
    ) -> None:
        """
        Create a JDBC connection.

        Args:
            jclassname: Fully qualified Java class name of JDBC driver
            url: JDBC connection URL
            driver_args: Connection properties (dict) or [user, password] (list)
            jars: List of JAR file paths (for classpath)
            libs: Additional native library paths

        Raises:
            InterfaceError: If JVM or driver cannot be loaded
            DatabaseError: If connection fails
        """
        self._jclassname = jclassname
        self._url = url
        self._jdbc_connection: Any = None
        self._closed = False

        # Start JVM if not already running
        # Note: JVM can only be started once per Python process
        try:
            start_jvm(classpath=list(jars or []), jvm_args=None)
        except Exception as e:
            raise InterfaceError(f"Failed to start JVM: {e}") from e

        # Load driver and establish connection
        try:
            import jpype

            # Load the JDBC driver class - this registers it with DriverManager
            # Even though we don't use the returned class, loading it has side effects
            jpype.JClass(jclassname)
            logger.debug(f"Loaded JDBC driver: {jclassname}")

            # Get DriverManager - this is the main entry point for JDBC connections
            dm = jpype.JClass("java.sql.DriverManager")

            # Create connection based on driver_args format
            # We support multiple formats for flexibility
            if driver_args is None:
                # Simple connection without credentials
                self._jdbc_connection = dm.getConnection(url)

            elif isinstance(driver_args, dict):
                # Dict format - convert to Java Properties
                # This allows passing custom JDBC properties like SSL settings
                props = jpype.JClass("java.util.Properties")()
                for k, v in driver_args.items():
                    props.setProperty(str(k), str(v))
                self._jdbc_connection = dm.getConnection(url, props)

            elif isinstance(driver_args, (list, tuple)) and len(driver_args) == 2:
                # List format for simple user/password auth
                usr, pwd = driver_args
                self._jdbc_connection = dm.getConnection(url, str(usr), str(pwd))

            else:
                # TODO: Maybe support more argument formats in the future?
                raise ValueError("driver_args must be dict, [user, password], or None")

            logger.info(f"Connected to database: {url}")

        except Exception as e:
            logger.exception(f"Connection failed: {e}")
            raise DatabaseError(f"Failed to connect to database: {e}") from e

    def close(self) -> None:
        """Close the connection."""
        if self._closed:
            return

        try:
            if self._jdbc_connection is not None:
                self._jdbc_connection.close()
                logger.debug("Connection closed")
        except Exception as e:
            logger.warning(f"Error closing connection: {e}")
        finally:
            self._jdbc_connection = None
            self._closed = True

    def commit(self) -> None:
        """Commit current transaction."""
        if self._closed:
            raise InterfaceError("Connection is closed")

        try:
            if self._jdbc_connection is not None:
                self._jdbc_connection.commit()
                logger.debug("Transaction committed")
        except Exception as e:
            raise DatabaseError(f"Commit failed: {e}") from e

    def rollback(self) -> None:
        """Rollback current transaction."""
        if self._closed:
            raise InterfaceError("Connection is closed")

        try:
            if self._jdbc_connection is not None:
                self._jdbc_connection.rollback()
                logger.debug("Transaction rolled back")
        except Exception as e:
            raise DatabaseError(f"Rollback failed: {e}") from e

    def cursor(self) -> Cursor:
        """
        Create a new cursor.

        Returns:
            Cursor object

        Raises:
            InterfaceError: If connection is closed
        """
        if self._closed:
            raise InterfaceError("Connection is closed")

        return Cursor(self, self._jdbc_connection)

    def set_auto_commit(self, auto_commit: bool) -> None:
        """
        Set auto-commit mode.

        Args:
            auto_commit: True to enable auto-commit, False to disable
        """
        if self._closed:
            raise InterfaceError("Connection is closed")

        try:
            self._jdbc_connection.setAutoCommit(auto_commit)
            logger.debug(f"Auto-commit set to {auto_commit}")
        except Exception as e:
            raise DatabaseError(f"Failed to set auto-commit: {e}") from e

    def get_auto_commit(self) -> bool:
        """Get current auto-commit mode."""
        if self._closed:
            raise InterfaceError("Connection is closed")

        try:
            return self._jdbc_connection.getAutoCommit()
        except Exception as e:
            raise DatabaseError(f"Failed to get auto-commit: {e}") from e

    @property
    def closed(self) -> bool:
        """Check if connection is closed."""
        return self._closed

    def __enter__(self) -> Connection:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()

    def __del__(self) -> None:
        """Destructor to ensure connection is closed."""
        if not self._closed:
            try:
                self.close()
            except Exception:
                pass


def connect(
    jclassname: str,
    url: str,
    driver_args: dict[str, Any] | list[Any] | None = None,
    jars: list[str] | None = None,
    libs: list[str] | None = None,
) -> Connection:
    """
    Create a JDBC database connection.

    This is the main entry point for creating connections, following DB-API 2.0.

    Args:
        jclassname: Fully qualified Java class name of JDBC driver
        url: JDBC connection URL
        driver_args: Connection properties (dict) or [user, password] (list)
        jars: List of JAR file paths for classpath
        libs: Additional native library paths

    Returns:
        Connection object

    Example:
        >>> conn = connect(
        ...     'org.postgresql.Driver',
        ...     'jdbc:postgresql://localhost:5432/mydb',
        ...     {'user': 'myuser', 'password': 'mypass'}
        ... )
        >>> cursor = conn.cursor()
        >>> cursor.execute('SELECT * FROM users')
        >>> rows = cursor.fetchall()
        >>> conn.close()
    """
    return Connection(
        jclassname=jclassname,
        url=url,
        driver_args=driver_args,
        jars=jars,
        libs=libs,
    )
