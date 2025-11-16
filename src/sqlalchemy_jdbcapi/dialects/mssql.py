"""
Microsoft SQL Server JDBC dialect for SQLAlchemy.

Provides full SQL Server support through JDBC.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from sqlalchemy import exc, sql
from sqlalchemy.dialects.mssql.base import MSDialect
from sqlalchemy.engine import Connection

from .base import BaseJDBCDialect, JDBCDriverConfig

logger = logging.getLogger(__name__)


class MSSQLDialect(BaseJDBCDialect, MSDialect):
    """
    Microsoft SQL Server dialect using JDBC driver.

    Supports SQL Server-specific features including:
    - T-SQL extensions
    - TOP clause
    - OUTPUT clause
    - Common Table Expressions (CTEs)
    - Window functions
    - JSON support (SQL Server 2016+)

    Connection URL formats:
        jdbcapi+mssql://user:password@host:1433/database
        jdbcapi+sqlserver://user:password@host:1433/database  # Alias
    """

    name = "mssql"
    driver = "jdbcapi"

    # SQL Server capabilities
    supports_native_boolean = False  # SQL Server uses BIT
    supports_sequences = True  # SQL Server 2012+
    supports_native_enum = False

    @classmethod
    def get_driver_config(cls) -> JDBCDriverConfig:
        """Get SQL Server JDBC driver configuration."""
        return JDBCDriverConfig(
            driver_class="com.microsoft.sqlserver.jdbc.SQLServerDriver",
            jdbc_url_template="jdbc:sqlserver://{host}:{port};databaseName={database}",
            default_port=1433,
            supports_transactions=True,
            supports_schemas=True,
            supports_sequences=True,
        )

    def initialize(self, connection: Connection) -> None:
        """Initialize SQL Server connection."""
        super().initialize(connection)
        logger.debug("Initialized SQL Server JDBC dialect")

    def _get_server_version_info(self, connection: Connection) -> tuple[int, ...]:
        """
        Get SQL Server version.

        Returns:
            Tuple of version numbers (e.g., (15, 0, 4236))
        """
        try:
            result = connection.execute(sql.text("SELECT @@VERSION")).scalar()

            if result:
                # Parse version from string like:
                # "Microsoft SQL Server 2019 (RTM-CU15) - 15.0.4236.7 ..."
                match = re.search(r"- (\d+)\.(\d+)\.(\d+)", result)
                if match:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    build = int(match.group(3))
                    return (major, minor, build)

                # Fallback: try to extract major version from name
                version_names = {
                    "2022": (16, 0, 0),
                    "2019": (15, 0, 0),
                    "2017": (14, 0, 0),
                    "2016": (13, 0, 0),
                    "2014": (12, 0, 0),
                    "2012": (11, 0, 0),
                }

                for name, version in version_names.items():
                    if name in result:
                        return version

        except exc.DBAPIError as e:
            logger.warning(f"Failed to get SQL Server version: {e}")

        # Default fallback
        return (13, 0, 0)

    def do_ping(self, dbapi_connection: Any) -> bool:
        """Check if SQL Server connection is alive."""
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.debug(f"SQL Server ping failed: {e}")
            return False


# Export the dialect
dialect = MSSQLDialect
