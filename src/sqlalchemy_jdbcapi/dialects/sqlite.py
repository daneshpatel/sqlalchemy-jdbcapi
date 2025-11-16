"""
SQLite JDBC dialect for SQLAlchemy.

Provides SQLite support through JDBC (mainly for testing or Java interop).
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import exc, sql
from sqlalchemy.dialects.sqlite.base import SQLiteDialect as BaseSQLiteDialect
from sqlalchemy.engine import Connection

from .base import BaseJDBCDialect, JDBCDriverConfig

logger = logging.getLogger(__name__)


class SQLiteDialect(BaseJDBCDialect, BaseSQLiteDialect):
    """
    SQLite dialect using JDBC driver.

    Note: For production use, the native sqlite3 dialect is recommended.
    This JDBC dialect is primarily useful for:
    - Testing JDBC infrastructure
    - Java application integration
    - Environments where native sqlite3 is not available

    Connection URL format:
        jdbcapi+sqlite:///path/to/database.db
        jdbcapi+sqlite:///:memory:  # In-memory database
    """

    name = "sqlite"
    driver = "jdbcapi"

    # SQLite capabilities
    supports_native_boolean = False
    supports_sequences = False
    supports_native_enum = False
    supports_native_decimal = False

    @classmethod
    def import_dbapi(cls) -> Any:
        """
        Import JDBC module.

        SQLAlchemy's SQLite dialect expects sqlite_version_info attribute,
        so we add it as a wrapper.
        """
        from sqlalchemy_jdbcapi import jdbc

        # Add sqlite_version_info if not present (required by SQLAlchemy's SQLite dialect)
        if not hasattr(jdbc, "sqlite_version_info"):
            # Use a reasonable default version
            jdbc.sqlite_version_info = (3, 40, 0)

        return jdbc

    @classmethod
    def get_driver_config(cls) -> JDBCDriverConfig:
        """Get SQLite JDBC driver configuration."""
        return JDBCDriverConfig(
            driver_class="org.sqlite.JDBC",
            jdbc_url_template="jdbc:sqlite:{database}",
            default_port=0,  # Not applicable for SQLite
            supports_transactions=True,
            supports_schemas=False,  # SQLite has limited schema support
            supports_sequences=False,
        )

    def create_connect_args(self, url: Any) -> tuple[list[Any], dict[str, Any]]:
        """
        Create connection arguments for SQLite.

        Handles file paths and in-memory databases.
        """
        config = self.get_driver_config()

        # Build JDBC URL
        if url.database:
            if url.database == ":memory:":
                jdbc_url = "jdbc:sqlite::memory:"
            else:
                jdbc_url = f"jdbc:sqlite:{url.database}"
        else:
            # Default to in-memory
            jdbc_url = "jdbc:sqlite::memory:"

        logger.debug(f"Creating SQLite connection to: {jdbc_url}")

        kwargs = {
            "jclassname": config.driver_class,
            "url": jdbc_url,
            "driver_args": None,
        }

        return ([], kwargs)

    def initialize(self, connection: Connection) -> None:
        """Initialize SQLite connection."""
        super().initialize(connection)
        logger.debug("Initialized SQLite JDBC dialect")

    def _get_server_version_info(self, connection: Connection) -> tuple[int, ...]:
        """
        Get SQLite version.

        Returns:
            Tuple of version numbers (e.g., (3, 40, 1))
        """
        try:
            result = connection.execute(sql.text("SELECT sqlite_version()")).scalar()

            if result:
                # Parse version from string like: "3.40.1"
                parts = result.split(".")
                return tuple(int(p) for p in parts[:3])

        except exc.DBAPIError as e:
            logger.warning(f"Failed to get SQLite version: {e}")

        # Default fallback
        return (3, 30, 0)

    def do_ping(self, dbapi_connection: Any) -> bool:
        """Check if SQLite connection is alive."""
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.debug(f"SQLite ping failed: {e}")
            return False


# Export the dialect
dialect = SQLiteDialect
