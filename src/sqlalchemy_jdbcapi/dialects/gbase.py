"""
GBase 8s JDBC dialect for SQLAlchemy.

Provides support for GBase 8s (South Technology Group) database,
which is compatible with Informix and supports PostgreSQL-like features.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from sqlalchemy import exc, sql
from sqlalchemy.engine import Connection, Dialect

from .base import BaseJDBCDialect, JDBCDriverConfig

logger = logging.getLogger(__name__)


class GBase8sDialect(BaseJDBCDialect, Dialect):  # type: ignore
    """
    GBase 8s dialect using JDBC driver.

    GBase 8s is an enterprise-grade database system from South Technology Group,
    based on Informix architecture with PostgreSQL-compatible features.

    Supports GBase 8s-specific features including:
    - Sequences
    - Identity columns
    - Stored procedures
    - Full-text search
    - JSON support (GBase 8s 8.8+)
    - Spatial data types

    Connection URL format:
        jdbcapi+gbase8s://user:password@host:9088/database
        jdbcapi+gbase://user:password@host:9088/database (alias)
    """

    name = "gbase8s"
    driver = "jdbcapi"

    # GBase 8s capabilities
    supports_native_boolean = False  # Uses SMALLINT for boolean
    supports_sequences = True
    supports_identity_columns = True
    supports_native_enum = False
    supports_multivalues_insert = True
    supports_statement_cache = True

    # Isolation levels supported by GBase 8s
    _isolation_lookup = {
        "SERIALIZABLE": "SERIALIZABLE",
        "READ_UNCOMMITTED": "READ UNCOMMITTED",
        "READ_COMMITTED": "READ COMMITTED",
        "REPEATABLE_READ": "REPEATABLE READ",
    }

    @classmethod
    def get_driver_config(cls) -> JDBCDriverConfig:
        """Get GBase 8s JDBC driver configuration."""
        return JDBCDriverConfig(
            driver_class="com.gbasedbt.jdbc.Driver",
            jdbc_url_template="jdbc:gbasedbt-sqli://{host}:{port}/{database}",
            default_port=9088,
            supports_transactions=True,
            supports_schemas=True,
            supports_sequences=True,
        )

    def initialize(self, connection: Connection) -> None:
        """Initialize GBase 8s connection."""
        if not hasattr(self, "_server_version_info"):
            self._server_version_info = self._get_server_version_info(connection)
        logger.debug("Initialized GBase 8s JDBC dialect")

    def _get_server_version_info(self, connection: Connection) -> tuple[int, ...]:
        """
        Get GBase 8s server version.

        Returns:
            Tuple of version numbers (e.g., (8, 8, 1))
        """
        try:
            # GBase 8s version query
            result = connection.execute(
                sql.text("SELECT DBINFO('version', 'full') FROM systables WHERE tabid = 1")
            ).scalar()

            if result:
                # Parse version from string like:
                # "GBase 8s Server Version 8.8.1.0"
                match = re.search(r"(\d+)\.(\d+)\.(\d+)", str(result))
                if match:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    patch = int(match.group(3))
                    return (major, minor, patch)

        except exc.DBAPIError as e:
            logger.warning(f"Failed to get GBase 8s server version: {e}")

            # Fallback: try alternative query
            try:
                result = connection.execute(
                    sql.text("SELECT FIRST 1 DBINFO('version', 'major') || '.' || DBINFO('version', 'minor') FROM systables")
                ).scalar()

                if result:
                    match = re.search(r"(\d+)\.(\d+)", str(result))
                    if match:
                        return (int(match.group(1)), int(match.group(2)), 0)

            except exc.DBAPIError:
                pass

        # Default fallback
        return (8, 8, 0)

    def do_ping(self, dbapi_connection: Any) -> bool:
        """Check if GBase 8s connection is alive."""
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("SELECT 1 FROM systables WHERE tabid = 1")
            cursor.close()
            return True
        except Exception as e:
            logger.debug(f"GBase 8s ping failed: {e}")
            return False

    def get_isolation_level(self, dbapi_connection: Any) -> str:
        """Get current transaction isolation level."""
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("SELECT DBINFO('isolation') FROM systables WHERE tabid = 1")
            result = cursor.fetchone()
            cursor.close()
            if result:
                return str(result[0])
        except Exception as e:
            logger.debug(f"Failed to get isolation level: {e}")
        return "READ COMMITTED"

    def set_isolation_level(self, dbapi_connection: Any, level: str) -> None:
        """Set transaction isolation level."""
        if level in self._isolation_lookup:
            level = self._isolation_lookup[level]

        # Validate isolation level to prevent SQL injection
        valid_levels = {"SERIALIZABLE", "READ UNCOMMITTED", "READ COMMITTED", "REPEATABLE READ"}
        if level.upper() not in valid_levels:
            logger.warning(f"Invalid isolation level: {level}")
            return

        try:
            cursor = dbapi_connection.cursor()
            # Use validated level - safe from SQL injection
            cursor.execute(f"SET ISOLATION TO {level}")
            cursor.close()
        except Exception as e:
            logger.warning(f"Failed to set isolation level: {e}")


class GBaseDialect(GBase8sDialect):
    """Alias for GBase8sDialect for convenience."""

    name = "gbase"


# Export the dialect
dialect = GBase8sDialect
