"""
PostgreSQL JDBC dialect for SQLAlchemy.

Provides full PostgreSQL support through JDBC, compatible with SQLAlchemy 2.0+.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from sqlalchemy import sql
from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.engine import Connection

from .base import BaseJDBCDialect, JDBCDriverConfig

logger = logging.getLogger(__name__)


class PostgreSQLDialect(BaseJDBCDialect, PGDialect):
    """
    PostgreSQL dialect using JDBC driver.

    Supports all PostgreSQL-specific features including:
    - Arrays
    - JSONB
    - UUID
    - Full-text search
    - Custom types

    Connection URL format:
        jdbcapi+postgresql://user:password@host:5432/database
        jdbcapi+pgjdbc://user:password@host:5432/database  # Alias
    """

    name = "postgresql"
    driver = "jdbcapi"

    # PostgreSQL-specific capabilities
    supports_native_enum = True
    supports_sequences = True
    supports_native_boolean = True
    supports_smallserial = True

    # Column specifications inherited from PGDialect
    # Can be extended in the future for JDBC-specific type mappings if needed

    @classmethod
    def get_driver_config(cls) -> JDBCDriverConfig:
        """Get PostgreSQL JDBC driver configuration."""
        return JDBCDriverConfig(
            driver_class="org.postgresql.Driver",
            jdbc_url_template="jdbc:postgresql://{host}:{port}/{database}",
            default_port=5432,
            supports_transactions=True,
            supports_schemas=True,
            supports_sequences=True,
        )

    def initialize(self, connection: Connection) -> None:
        """Initialize PostgreSQL connection."""
        super().initialize(connection)

        # Set up PostgreSQL-specific settings
        logger.debug("Initialized PostgreSQL JDBC dialect")

    def _get_server_version_info(self, connection: Connection) -> tuple[int, ...]:
        """
        Get PostgreSQL server version.

        Returns:
            Tuple of version numbers (e.g., (14, 5, 0))
        """
        try:
            result = connection.execute(sql.text("SELECT version()")).scalar()
            if result:
                # Parse version from string like:
                # "PostgreSQL 14.5 on x86_64-pc-linux-gnu..."
                match = re.search(r"PostgreSQL (\d+)\.(\d+)(?:\.(\d+))?", result)
                if match:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    patch = int(match.group(3)) if match.group(3) else 0
                    return (major, minor, patch)
        except Exception as e:
            logger.warning(f"Failed to get server version: {e}")

        # Default fallback
        return (9, 0, 0)

    def do_ping(self, dbapi_connection: Any) -> bool:
        """
        Check if PostgreSQL connection is alive.

        Uses a simple SELECT query for efficiency.
        """
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.debug(f"PostgreSQL ping failed: {e}")
            return False


# Export the dialect
dialect = PostgreSQLDialect
