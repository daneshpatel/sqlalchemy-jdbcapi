"""
OceanBase JDBC dialect for SQLAlchemy.

OceanBase is an enterprise distributed relational database with Oracle compatibility mode.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any

from sqlalchemy import TIMESTAMP, TypeDecorator, exc, sql, util
from sqlalchemy.dialects.oracle.base import OracleDialect
from sqlalchemy.engine import Connection
from sqlalchemy.engine.url import URL, make_url

from .base import BaseJDBCDialect, JDBCDriverConfig

logger = logging.getLogger(__name__)


class ObTimestamp(TypeDecorator):
    """
    Custom timestamp type for OceanBase.

    Handles conversion between Python datetime and OceanBase Timestamp.
    """

    impl = TIMESTAMP
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        """Convert Python datetime to OceanBase timestamp."""
        if isinstance(value, datetime):
            try:
                # Try to use JPype to create Java Timestamp
                import jpype

                if jpype.isJVMStarted():
                    Timestamp = jpype.JClass("java.sql.Timestamp")
                    return Timestamp.valueOf(
                        value.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    )
            except Exception as e:
                logger.debug(f"Failed to create Java Timestamp: {e}")
                # Fall back to string representation
                return value
        return value

    def process_result_value(self, value: Any, dialect: Any) -> datetime | None:
        """Convert OceanBase timestamp to Python datetime."""
        if value is not None:
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                # Parse string timestamp
                try:
                    from dateutil import parser

                    return parser.parse(value)
                except Exception as e:
                    logger.warning(f"Failed to parse timestamp: {e}")
                    return None
        return None


class OceanBaseDialect(BaseJDBCDialect, OracleDialect):  # type: ignore
    """
    OceanBase dialect using JDBC driver (Oracle compatibility mode).

    OceanBase is a distributed database that supports both MySQL and Oracle
    compatibility modes. This dialect implements Oracle mode.

    Connection URL format:
        jdbcapi+oceanbase://user@tenant#cluster:password@host:2881/database
        jdbcapi+oceanbasejdbc://user:password@host:2881/database  # Alias

    Note: OceanBase uses a special user format: username@tenant#cluster
    """

    name = "oceanbase"
    driver = "jdbcapi"

    # OceanBase capabilities
    supports_native_decimal = True
    supports_sane_rowcount = False
    supports_sane_multi_rowcount = False
    supports_unicode_binds = True
    supports_statement_cache = True
    supports_sequences = True

    # Custom column specifications
    colspecs = util.update_copy(
        OracleDialect.colspecs,  # type: ignore
        {TIMESTAMP: ObTimestamp},
    )

    @classmethod
    def get_driver_config(cls) -> JDBCDriverConfig:
        """Get OceanBase JDBC driver configuration."""
        return JDBCDriverConfig(
            driver_class="com.oceanbase.jdbc.Driver",
            jdbc_url_template="jdbc:oceanbase://{host}:{port}/{database}",
            default_port=2881,
            supports_transactions=True,
            supports_schemas=True,
            supports_sequences=True,
        )

    def create_connect_args(self, url: URL | str) -> tuple[list[Any], dict[str, Any]]:
        """
        Create connection arguments for OceanBase.

        Handles special OceanBase user format and connection properties.
        """
        if isinstance(url, str):
            url = make_url(url)

        config = self.get_driver_config()

        # Build JDBC URL
        jdbc_url = config.format_jdbc_url(
            host=url.host or "localhost",
            port=url.port,
            database=url.database,
        )

        logger.debug(f"Creating OceanBase connection to: {jdbc_url}")

        # Build connection properties
        connect_args: dict[str, Any] = {}

        if url.username:
            connect_args["user"] = url.username
        if url.password:
            connect_args["password"] = url.password

        # Add query parameters as connection properties
        if url.query:
            connect_args.update(url.query)

        kwargs = {
            "jclassname": config.driver_class,
            "url": jdbc_url,
            "driver_args": connect_args,
        }

        return ([], kwargs)

    def initialize(self, connection: Connection) -> None:
        """Initialize OceanBase connection."""
        super().initialize(connection)
        logger.debug("Initialized OceanBase JDBC dialect")

    def _get_server_version_info(self, connection: Connection) -> tuple[int, ...]:
        """
        Get OceanBase server version.

        Returns:
            Tuple of version numbers (e.g., (4, 0, 0))
        """
        try:
            ver_sql = sql.text("SELECT BANNER FROM v$version")
            banner = connection.execute(ver_sql).scalar()

            if banner:
                # Parse version from string like:
                # "OceanBase 4.0.0.0 (r10100032022071511-36b8cb0cebc8c2662e8d0c252603c8f2281bb5cc)"
                match = re.search(r"OceanBase ([\d+\.]+\d+)", banner)
                if match:
                    version_str = match.group(1)
                    parts = version_str.split(".")
                    return tuple(int(p) for p in parts[:3])

        except exc.DBAPIError as e:
            logger.warning(f"Failed to get OceanBase server version: {e}")

        # Default fallback
        return (3, 0, 0)

    @property
    def _is_oracle_8(self) -> bool:
        """OceanBase is never Oracle 8."""
        return False

    def _check_max_identifier_length(self, connection: Connection) -> int | None:
        """OceanBase uses Oracle-compatible identifier lengths."""
        return 128

    def do_rollback(self, dbapi_connection: Any) -> None:
        """
        Perform rollback on OceanBase connection.

        OceanBase sometimes has issues with rollback, this provides
        error handling.
        """
        try:
            if dbapi_connection and not dbapi_connection.closed:
                dbapi_connection.rollback()
        except Exception as e:
            logger.warning(f"OceanBase rollback failed: {e}")

    def do_ping(self, dbapi_connection: Any) -> bool:
        """Check if OceanBase connection is alive."""
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("SELECT 1 FROM DUAL")
            cursor.close()
            return True
        except Exception as e:
            logger.debug(f"OceanBase ping failed: {e}")
            return False


# Export the dialect
dialect = OceanBaseDialect
