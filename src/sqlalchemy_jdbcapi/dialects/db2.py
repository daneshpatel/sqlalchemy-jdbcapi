"""
IBM DB2 JDBC dialect for SQLAlchemy.

Provides support for IBM DB2 for Linux, Unix, Windows, and z/OS.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from sqlalchemy import exc, sql
from sqlalchemy.engine import Connection, Dialect

from .base import BaseJDBCDialect, JDBCDriverConfig

logger = logging.getLogger(__name__)

# Try to import DB2 dialect if available
try:
    from sqlalchemy.dialects.db2.base import DB2Dialect as BaseDB2Dialect

    HAS_DB2_DIALECT = True
except ImportError:
    # Fallback to generic dialect
    BaseDB2Dialect = Dialect  # type: ignore
    HAS_DB2_DIALECT = False
    logger.debug("IBM DB2 dialect not available, using generic implementation")


class DB2Dialect(BaseJDBCDialect, BaseDB2Dialect):  # type: ignore
    """
    IBM DB2 dialect using JDBC driver.

    Supports DB2-specific features including:
    - Sequences
    - Identity columns
    - Generated columns
    - Temporal tables (DB2 10+)
    - JSON support (DB2 11+)

    Connection URL format:
        jdbcapi+db2://user:password@host:50000/database
    """

    name = "db2"
    driver = "jdbcapi"

    # DB2 capabilities
    supports_native_boolean = False  # DB2 < 11.1 doesn't support BOOLEAN
    supports_sequences = True
    supports_identity_columns = True
    supports_native_enum = False

    @classmethod
    def get_driver_config(cls) -> JDBCDriverConfig:
        """Get DB2 JDBC driver configuration."""
        return JDBCDriverConfig(
            driver_class="com.ibm.db2.jcc.DB2Driver",
            jdbc_url_template="jdbc:db2://{host}:{port}/{database}",
            default_port=50000,
            supports_transactions=True,
            supports_schemas=True,
            supports_sequences=True,
        )

    def initialize(self, connection: Connection) -> None:
        """Initialize DB2 connection."""
        if HAS_DB2_DIALECT:
            super().initialize(connection)
        # Basic initialization
        elif not hasattr(self, "_server_version_info"):
            self._server_version_info = self._get_server_version_info(connection)

        logger.debug("Initialized DB2 JDBC dialect")

    def _get_server_version_info(self, connection: Connection) -> tuple[int, ...]:
        """
        Get DB2 server version.

        Returns:
            Tuple of version numbers (e.g., (11, 5, 8))
        """
        try:
            # Try DB2-specific version query
            result = connection.execute(
                sql.text("SELECT SERVICE_LEVEL FROM SYSIBMADM.ENV_INST_INFO")
            ).scalar()

            if result:
                # Parse version from string like:
                # "DB2 v11.5.8.0"
                match = re.search(r"v(\d+)\.(\d+)\.(\d+)", result)
                if match:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    patch = int(match.group(3))
                    return (major, minor, patch)

        except exc.DBAPIError as e:
            logger.warning(f"Failed to get DB2 server version: {e}")

            # Fallback: try alternative query
            try:
                result = connection.execute(
                    sql.text("VALUES (SYSPROC.VERSION())")
                ).scalar()

                if result:
                    match = re.search(r"(\d+)\.(\d+)\.(\d+)", result)
                    if match:
                        return tuple(int(match.group(i)) for i in range(1, 4))

            except exc.DBAPIError:
                pass

        # Default fallback
        return (11, 1, 0)

    def do_ping(self, dbapi_connection: Any) -> bool:
        """Check if DB2 connection is alive."""
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("SELECT 1 FROM SYSIBM.SYSDUMMY1")
            cursor.close()
            return True
        except Exception as e:
            logger.debug(f"DB2 ping failed: {e}")
            return False


# Export the dialect
dialect = DB2Dialect
