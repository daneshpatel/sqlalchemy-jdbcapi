"""
Oracle JDBC dialect for SQLAlchemy.

Provides full Oracle Database support through JDBC, compatible with SQLAlchemy 2.0+.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from sqlalchemy import exc, sql, util
from sqlalchemy.dialects.oracle.base import OracleDialect
from sqlalchemy.engine import Connection

from .base import BaseJDBCDialect, JDBCDriverConfig

logger = logging.getLogger(__name__)


class OracleDialect(BaseJDBCDialect, OracleDialect):  # type: ignore
    """
    Oracle Database dialect using JDBC driver.

    Supports Oracle-specific features including:
    - Sequences
    - Synonyms
    - Database links
    - Packages
    - Custom types

    Connection URL formats:
        jdbcapi+oracle://user:password@host:1521/database
        jdbcapi+oracle://user:password@host:1521/SID
        jdbcapi+oraclejdbc://user:password@host:1521/service_name  # Alias

    For TNS connections:
        jdbcapi+oracle://user:password@tnsname
    """

    name = "oracle"
    driver = "jdbcapi"

    # Oracle-specific capabilities
    supports_sequences = True
    supports_native_boolean = False  # Oracle < 23c doesn't have native boolean
    supports_identity_columns = True  # Oracle 12c+

    # Override column specifications for JDBC type handling
    colspecs = util.update_copy(
        OracleDialect.colspecs,  # type: ignore
        {
            # Add JDBC-specific type mappings here if needed
        },
    )

    @classmethod
    def get_driver_config(cls) -> JDBCDriverConfig:
        """Get Oracle JDBC driver configuration."""
        return JDBCDriverConfig(
            driver_class="oracle.jdbc.OracleDriver",
            jdbc_url_template="jdbc:oracle:thin:@{host}:{port}/{database}",
            default_port=1521,
            supports_transactions=True,
            supports_schemas=True,
            supports_sequences=True,
        )

    def create_connect_args(self, url: Any) -> tuple[list[Any], dict[str, Any]]:
        """
        Create connection arguments from SQLAlchemy URL.

        Handles various Oracle connection formats including TNS names.
        """
        config = self.get_driver_config()

        # Check if this is a TNS name (no port specified)
        if url.port is None and url.host and "/" not in url.host:
            # TNS name format
            jdbc_url = f"jdbc:oracle:thin:@{url.host}"
            if url.database:
                jdbc_url = f"{jdbc_url}/{url.database}"
        else:
            # Standard format
            jdbc_url = config.format_jdbc_url(
                host=url.host or "localhost",
                port=url.port,
                database=url.database,
                query_params=dict(url.query) if url.query else None,
            )

        logger.debug(f"Creating Oracle connection to: {jdbc_url}")

        # Build driver arguments
        driver_args: dict[str, Any] = {}

        if url.username:
            driver_args["user"] = url.username
        if url.password:
            driver_args["password"] = url.password

        # Add query parameters as connection properties
        if url.query:
            driver_args.update(url.query)

        kwargs = {
            "jclassname": config.driver_class,
            "url": jdbc_url,
            "driver_args": driver_args if driver_args else None,
        }

        return ([], kwargs)

    def initialize(self, connection: Connection) -> None:
        """Initialize Oracle connection."""
        super().initialize(connection)
        logger.debug("Initialized Oracle JDBC dialect")

    def _get_server_version_info(self, connection: Connection) -> tuple[int, ...]:
        """
        Get Oracle server version.

        Returns:
            Tuple of version numbers (e.g., (19, 3, 0))
        """
        try:
            banner = connection.execute(
                sql.text("SELECT BANNER FROM v$version")
            ).scalar()

            if banner:
                # Parse version from string like:
                # "Oracle Database 19c Enterprise Edition Release 19.0.0.0.0 - Production"
                match = re.search(r"Release ([\d\.]+)", banner)
                if match:
                    version_str = match.group(1)
                    parts = version_str.split(".")
                    return tuple(int(p) for p in parts[:3])

        except exc.DBAPIError as e:
            logger.warning(f"Failed to get Oracle server version: {e}")

        # Default fallback
        return (11, 0, 0)

    @property
    def _is_oracle_8(self) -> bool:
        """Check if connected to Oracle 8 (legacy support)."""
        return getattr(self, "_server_version_info", (11, 0, 0))[0] < 9

    def _check_max_identifier_length(self, connection: Connection) -> int | None:
        """
        Get maximum identifier length for this Oracle version.

        Oracle 12.2+ supports 128 characters, earlier versions support 30.
        """
        version = getattr(self, "_server_version_info", (11, 0, 0))
        if version >= (12, 2):
            return 128
        return 30

    def do_ping(self, dbapi_connection: Any) -> bool:
        """
        Check if Oracle connection is alive.

        Uses Oracle's dual table for efficiency.
        """
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("SELECT 1 FROM DUAL")
            cursor.close()
            return True
        except Exception as e:
            logger.debug(f"Oracle ping failed: {e}")
            return False


# Export the dialect
dialect = OracleDialect
