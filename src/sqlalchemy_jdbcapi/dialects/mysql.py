"""
MySQL and MariaDB JDBC dialects for SQLAlchemy.

Provides support for MySQL and MariaDB through JDBC.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from sqlalchemy import exc, sql
from sqlalchemy.dialects.mysql.base import MySQLDialect as BaseMySQLDialect
from sqlalchemy.engine import Connection

from .base import BaseJDBCDialect, JDBCDriverConfig

logger = logging.getLogger(__name__)


class MySQLDialect(BaseJDBCDialect, BaseMySQLDialect):
    """
    MySQL dialect using JDBC driver.

    Supports MySQL-specific features including:
    - AUTO_INCREMENT
    - Full-text indexes
    - JSON columns (MySQL 5.7+)
    - Spatial types

    Connection URL format:
        jdbcapi+mysql://user:password@host:3306/database
    """

    name = "mysql"
    driver = "jdbcapi"

    # MySQL capabilities
    supports_native_boolean = False  # MySQL uses TINYINT(1)
    supports_native_enum = True
    supports_sequences = False  # MySQL < 8.0 doesn't support sequences

    @classmethod
    def get_driver_config(cls) -> JDBCDriverConfig:
        """Get MySQL JDBC driver configuration."""
        return JDBCDriverConfig(
            driver_class="com.mysql.cj.jdbc.Driver",  # MySQL Connector/J 8.0+
            jdbc_url_template="jdbc:mysql://{host}:{port}/{database}",
            default_port=3306,
            supports_transactions=True,
            supports_schemas=True,
            supports_sequences=False,
        )

    def initialize(self, connection: Connection) -> None:
        """Initialize MySQL connection."""
        super().initialize(connection)
        logger.debug("Initialized MySQL JDBC dialect")

    def _get_server_version_info(self, connection: Connection) -> tuple[int, ...]:
        """
        Get MySQL server version.

        Returns:
            Tuple of version numbers (e.g., (8, 0, 32))
        """
        try:
            result = connection.execute(sql.text("SELECT VERSION()")).scalar()

            if result:
                # Parse version from string like:
                # "8.0.32" or "5.7.40-log"
                match = re.search(r"(\d+)\.(\d+)\.(\d+)", result)
                if match:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    patch = int(match.group(3))
                    return (major, minor, patch)

        except exc.DBAPIError as e:
            logger.warning(f"Failed to get MySQL server version: {e}")

        # Default fallback
        return (5, 7, 0)

    def do_ping(self, dbapi_connection: Any) -> bool:
        """Check if MySQL connection is alive."""
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.debug(f"MySQL ping failed: {e}")
            return False


class MariaDBDialect(MySQLDialect):
    """
    MariaDB dialect using JDBC driver.

    MariaDB is a MySQL fork with additional features.
    This dialect extends MySQL with MariaDB-specific capabilities.

    Connection URL format:
        jdbcapi+mariadb://user:password@host:3306/database
    """

    name = "mariadb"

    @classmethod
    def get_driver_config(cls) -> JDBCDriverConfig:
        """Get MariaDB JDBC driver configuration."""
        return JDBCDriverConfig(
            driver_class="org.mariadb.jdbc.Driver",
            jdbc_url_template="jdbc:mariadb://{host}:{port}/{database}",
            default_port=3306,
            supports_transactions=True,
            supports_schemas=True,
            supports_sequences=True,  # MariaDB 10.3+ supports sequences
        )

    def _get_server_version_info(self, connection: Connection) -> tuple[int, ...]:
        """
        Get MariaDB server version.

        Returns:
            Tuple of version numbers (e.g., (10, 11, 2))
        """
        try:
            result = connection.execute(sql.text("SELECT VERSION()")).scalar()

            if result:
                # Parse version from string like:
                # "10.11.2-MariaDB" or "10.6.12-MariaDB-log"
                match = re.search(r"(\d+)\.(\d+)\.(\d+)", result)
                if match:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    patch = int(match.group(3))
                    return (major, minor, patch)

        except exc.DBAPIError as e:
            logger.warning(f"Failed to get MariaDB server version: {e}")

        # Default fallback
        return (10, 6, 0)


# Export dialects
dialect = MySQLDialect
