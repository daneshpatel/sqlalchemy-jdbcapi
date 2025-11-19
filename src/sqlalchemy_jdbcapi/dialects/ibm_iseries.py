"""
IBM iSeries (AS/400) JDBC dialect for SQLAlchemy.

Provides support for IBM iSeries (formerly AS/400, now IBM i)
using the IBM Toolbox for Java JDBC driver.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import exc, sql
from sqlalchemy.engine import Connection, Dialect

from .base import BaseJDBCDialect, JDBCDriverConfig

logger = logging.getLogger(__name__)


class IBMiSeriesDialect(BaseJDBCDialect, Dialect):  # type: ignore
    """
    IBM iSeries (AS/400) dialect using JDBC driver.

    IBM iSeries (IBM i) is an integrated operating system for IBM Power Systems
    with integrated DB2 for i database. This dialect uses the IBM Toolbox for Java
    (JTOpen) JDBC driver to connect to iSeries systems.

    Supports iSeries-specific features including:
    - Record-level locking
    - Commitment control
    - SQL schemas (libraries)
    - Journaling
    - System naming convention
    - DB2 for i SQL features

    Connection URL format:
        jdbcapi+iseries://user:password@host/library
        jdbcapi+as400://user:password@host/library (alias)
        jdbcapi+ibmi://user:password@host/library (alias)

    Special connection properties:
        - naming: 'sql' (default) or 'system' (for *LIBL resolution)
        - libraries: comma-separated list of libraries to add to library list
        - date format: iso, usa, eur, jis, mdy, dmy, ymd, jul
    """

    name = "iseries"
    driver = "jdbcapi"

    # iSeries/DB2 for i capabilities
    supports_native_boolean = False  # Uses SMALLINT for boolean
    supports_sequences = True
    supports_identity_columns = True
    supports_native_enum = False
    supports_multivalues_insert = True
    supports_statement_cache = True
    supports_default_values = True
    supports_empty_insert = False

    # iSeries uses schemas called "libraries"
    default_schema_name = "QGPL"

    @classmethod
    def get_driver_config(cls) -> JDBCDriverConfig:
        """Get IBM iSeries JDBC driver configuration."""
        return JDBCDriverConfig(
            driver_class="com.ibm.as400.access.AS400JDBCDriver",
            jdbc_url_template="jdbc:as400://{host}/{database}",
            default_port=446,  # DRDA port, but AS/400 uses host routing
            supports_transactions=True,
            supports_schemas=True,
            supports_sequences=True,
        )

    @classmethod
    def create_connect_args(cls, url):  # type: ignore
        """
        Create connection arguments from URL.

        IBM iSeries JDBC URLs have special requirements:
        - The "database" is actually the default library (schema)
        - Additional properties for naming convention and library lists
        """
        opts = url.translate_connect_args(
            username="user",
            database="database",
        )

        driver_config = cls.get_driver_config()

        # Get host, port, and database (library)
        host = opts.get("host", "localhost")
        database = opts.get("database", "")
        username = opts.get("user", "")
        password = opts.get("password", "")

        # Build JDBC URL - iSeries doesn't use port in URL typically
        if database:
            jdbc_url = f"jdbc:as400://{host}/{database}"
        else:
            jdbc_url = f"jdbc:as400://{host}"

        # Build driver arguments
        # AS/400 JDBC driver prefers Properties object
        driver_args = {}

        if username:
            driver_args["user"] = username
        if password:
            driver_args["password"] = password

        # Add common iSeries-specific properties
        query_params = dict(url.query)

        # Naming convention (sql or system)
        if "naming" in query_params:
            driver_args["naming"] = query_params.pop("naming")
        else:
            driver_args["naming"] = "sql"  # Default to SQL naming

        # Additional libraries
        if "libraries" in query_params:
            driver_args["libraries"] = query_params.pop("libraries")

        # Date/time format
        if "date format" in query_params:
            driver_args["date format"] = query_params.pop("date format")
        elif "dateformat" in query_params:
            driver_args["date format"] = query_params.pop("dateformat")

        # Transaction isolation
        if "transaction isolation" in query_params:
            driver_args["transaction isolation"] = query_params.pop(
                "transaction isolation"
            )

        # Add remaining query parameters as driver properties
        driver_args.update(query_params)

        return (
            driver_config.driver_class,
            jdbc_url,
            driver_args,
        )

    def initialize(self, connection: Connection) -> None:
        """Initialize IBM iSeries connection."""
        if not hasattr(self, "_server_version_info"):
            self._server_version_info = self._get_server_version_info(connection)
        logger.debug("Initialized IBM iSeries JDBC dialect")

    def _get_server_version_info(self, connection: Connection) -> tuple[int, ...]:
        """
        Get IBM iSeries server version (DB2 for i version).

        Returns:
            Tuple of version numbers (e.g., (7, 5, 0))
        """
        try:
            # Query DB2 for i version
            result = connection.execute(
                sql.text(
                    "SELECT OS_VERSION, OS_RELEASE "
                    "FROM SYSIBMADM.ENV_SYS_INFO "
                    "FETCH FIRST 1 ROWS ONLY"
                )
            ).fetchone()

            if result:
                version = int(result[0]) if result[0] else 7
                release = int(result[1]) if result[1] else 1
                return (version, release, 0)

        except exc.DBAPIError as e:
            logger.warning(f"Failed to get iSeries version via SYSIBMADM: {e}")

            # Fallback: try QSYS2 catalog
            try:
                result = connection.execute(
                    sql.text(
                        "SELECT PTF_GROUP_LEVEL "
                        "FROM QSYS2.GROUP_PTF_INFO "
                        "WHERE PTF_GROUP_NAME = 'SF99730' "
                        "FETCH FIRST 1 ROWS ONLY"
                    )
                ).scalar()

                if result:
                    # PTF level maps to releases
                    return (7, 5, 0)  # Approximate

            except exc.DBAPIError:
                pass

            # Fallback: try version scalar function
            try:
                result = connection.execute(
                    sql.text("VALUES (CURRENT SERVER)")
                ).scalar()

                if result:
                    # Parse system name or version info
                    return (7, 4, 0)  # Default assumption

            except exc.DBAPIError:
                pass

        # Default fallback for iSeries
        return (7, 4, 0)

    def do_ping(self, dbapi_connection: Any) -> bool:
        """Check if IBM iSeries connection is alive."""
        try:
            cursor = dbapi_connection.cursor()
            # Use VALUES clause which is efficient on iSeries
            cursor.execute("VALUES (1)")
            cursor.close()
            return True
        except Exception as e:
            logger.debug(f"IBM iSeries ping failed: {e}")
            return False

    def has_table(
        self, connection: Connection, table_name: str, schema: str | None = None
    ) -> bool:
        """Check if a table exists in the specified library/schema."""
        if schema is None:
            schema = self.default_schema_name

        try:
            result = connection.execute(
                sql.text(
                    "SELECT 1 FROM QSYS2.SYSTABLES "
                    "WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table"
                ),
                {"schema": schema.upper(), "table": table_name.upper()},
            ).fetchone()
            return result is not None
        except exc.DBAPIError as e:
            logger.debug(f"has_table check failed: {e}")
            return False


class AS400Dialect(IBMiSeriesDialect):
    """Alias for IBMiSeriesDialect (legacy name)."""

    name = "as400"


class IBMiDialect(IBMiSeriesDialect):
    """Alias for IBMiSeriesDialect (modern name)."""

    name = "ibmi"


# Export the dialect
dialect = IBMiSeriesDialect
