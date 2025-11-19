"""
Microsoft Access JDBC dialect for SQLAlchemy.

Provides support for Microsoft Access databases (.mdb, .accdb)
using the UCanAccess JDBC driver.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from sqlalchemy import exc, sql
from sqlalchemy.engine import Connection, Dialect

from .base import BaseJDBCDialect, JDBCDriverConfig

logger = logging.getLogger(__name__)


class AccessDialect(BaseJDBCDialect, Dialect):  # type: ignore
    """
    Microsoft Access dialect using UCanAccess JDBC driver.

    UCanAccess is an open-source Java JDBC driver that reads and writes
    Microsoft Access databases (.mdb and .accdb files) without requiring
    Microsoft Office or ODBC drivers.

    Limitations:
    - No stored procedures support (Access macros not supported)
    - Limited transaction support
    - No sequences (uses AutoNumber/COUNTER)
    - Limited SQL syntax compared to full SQL databases
    - Single-user file locking considerations

    Supports Access-specific features including:
    - AutoNumber (COUNTER) columns
    - Memo fields (LONGCHAR)
    - OLE objects
    - Hyperlinks
    - Currency type
    - Yes/No (Boolean) type

    Connection URL format:
        jdbcapi+access:///path/to/database.accdb
        jdbcapi+msaccess:///path/to/database.mdb (alias)

    Special connection properties:
        - memory: true to open database in memory mode
        - newdatabaseversion: V2000, V2003, V2007, V2010 (for creating new DB)
        - encrypt: true to encrypt database
        - jackcessopener: custom opener class
    """

    name = "access"
    driver = "jdbcapi"

    # Access capabilities (quite limited)
    supports_native_boolean = True  # Yes/No type
    supports_sequences = False  # Uses AutoNumber instead
    supports_identity_columns = True  # AutoNumber/COUNTER
    supports_native_enum = False
    supports_multivalues_insert = False  # Access doesn't support multi-row insert
    supports_statement_cache = True
    supports_default_values = True
    supports_empty_insert = False

    # Access-specific
    supports_sane_rowcount = False
    supports_sane_multi_rowcount = False
    postfetch_lastrowid = True

    @classmethod
    def get_driver_config(cls) -> JDBCDriverConfig:
        """Get Microsoft Access JDBC driver configuration."""
        return JDBCDriverConfig(
            driver_class="net.ucanaccess.jdbc.UcanaccessDriver",
            jdbc_url_template="jdbc:ucanaccess://{database}",
            default_port=0,  # File-based, no port
            supports_transactions=True,  # Limited support
            supports_schemas=False,  # Access doesn't have schemas
            supports_sequences=False,
        )

    @classmethod
    def create_connect_args(cls, url):  # type: ignore  # noqa: C901
        """
        Create connection arguments from URL.

        Access uses file paths instead of host/port.

        URL formats supported:
        - jdbcapi+access:///path/to/database.accdb (Unix absolute path)
        - jdbcapi+access:///C:/path/to/database.accdb (Windows absolute path)
        - jdbcapi+access://C:/path/to/database.accdb (Windows drive letter)
        - jdbcapi+access:////server/share/database.accdb (UNC path)
        """
        driver_config = cls.get_driver_config()

        # Extract database path from URL
        database_path = ""

        if url.host:
            # Handle Windows paths like C:/path or //server/share
            if len(url.host) == 1 and url.host.isalpha():
                # Windows drive letter (e.g., C:)
                database_path = f"{url.host}:"
                if url.database:
                    database_path += url.database
            elif url.host.startswith("\\") or (
                url.port is None and "/" in str(url.database or "")
            ):
                # UNC path: //server/share/file.accdb
                database_path = f"//{url.host}"
                if url.database:
                    database_path += "/" + url.database
            else:
                # Network path or Unix path
                database_path = url.host
                if url.database:
                    database_path += "/" + url.database
        elif url.database:
            database_path = url.database

        # Ensure path starts with / for Unix-like paths
        if (
            database_path
            and not database_path.startswith("/")
            and ":" not in database_path
        ):
            database_path = "/" + database_path

        # Normalize the path - handle double slashes but preserve UNC paths
        if database_path.startswith("//"):
            # UNC path - preserve double slash at start
            normalized = "//" + database_path[2:].replace("//", "/")
        else:
            # Regular path
            normalized = database_path.replace("//", "/")

        database_path = normalized

        # Validate path has valid extension
        lower_path = database_path.lower()
        if not lower_path.endswith((".accdb", ".mdb")):
            logger.warning(
                f"Access database should have .accdb or .mdb extension: {database_path}"
            )

        # Build JDBC URL
        jdbc_url = f"jdbc:ucanaccess://{database_path}"

        # Build driver arguments
        driver_args = {}

        query_params = dict(url.query)

        # UCanAccess-specific properties
        if "memory" in query_params:
            driver_args["memory"] = query_params.pop("memory")

        if "newdatabaseversion" in query_params:
            driver_args["newDatabaseVersion"] = query_params.pop("newdatabaseversion")
        elif "newDatabaseVersion" in query_params:
            driver_args["newDatabaseVersion"] = query_params.pop("newDatabaseVersion")

        if "encrypt" in query_params:
            driver_args["encrypt"] = query_params.pop("encrypt")

        if "jackcessopener" in query_params:
            driver_args["jackcessOpener"] = query_params.pop("jackcessopener")

        if "showschema" in query_params:
            driver_args["showSchema"] = query_params.pop("showschema")

        if "sysschema" in query_params:
            driver_args["sysSchema"] = query_params.pop("sysschema")

        # Add remaining query parameters
        driver_args.update(query_params)

        return (
            driver_config.driver_class,
            jdbc_url,
            driver_args if driver_args else None,
        )

    def initialize(self, connection: Connection) -> None:
        """Initialize Microsoft Access connection."""
        if not hasattr(self, "_server_version_info"):
            self._server_version_info = self._get_server_version_info(connection)
        logger.debug("Initialized Microsoft Access JDBC dialect")

    def _get_server_version_info(self, connection: Connection) -> tuple[int, ...]:
        """
        Get Microsoft Access/UCanAccess version.

        Returns:
            Tuple of version numbers (UCanAccess version)
        """
        try:
            # UCanAccess provides version via JDBC metadata
            # We'll try to get Jackcess/UCanAccess version
            connection.execute(sql.text("SELECT 1")).fetchone()

            # Default to a reasonable version
            # UCanAccess 5.x is current
            return (5, 0, 1)

        except exc.DBAPIError as e:
            logger.warning(f"Failed to get Access version: {e}")

        # Default fallback
        return (5, 0, 0)

    def do_ping(self, dbapi_connection: Any) -> bool:
        """Check if Access connection is alive."""
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.debug(f"Access ping failed: {e}")
            return False

    def has_table(
        self, connection: Connection, table_name: str, schema: str | None = None
    ) -> bool:
        """Check if a table exists."""
        # Access doesn't have schemas, ignore schema parameter
        try:
            # Use JDBC metadata for Access
            # This is more reliable than querying system tables
            dbapi_conn = connection.connection.dbapi_connection
            metadata = dbapi_conn.jconn.getMetaData()
            result_set = metadata.getTables(None, None, table_name.upper(), ["TABLE"])

            has_table = result_set.next()
            result_set.close()
            return has_table

        except Exception as e:
            logger.debug(f"has_table check failed: {e}")

            # Fallback: try to query the table using parameterized query
            # Note: Access doesn't support parameterized table names, so we validate
            # the table name to prevent SQL injection
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_ ]*$", table_name):
                logger.warning(f"Invalid table name format: {table_name}")
                return False

            try:
                connection.execute(
                    sql.text(f"SELECT TOP 1 * FROM [{table_name}]")  # noqa: S608
                ).fetchone()
                return True
            except exc.DBAPIError:
                return False

    def _jdbc_type_to_sqlalchemy(self, jdbc_type: int, type_name: str) -> Any:
        """
        Convert JDBC type to SQLAlchemy type.

        Args:
            jdbc_type: JDBC type code
            type_name: JDBC type name string

        Returns:
            SQLAlchemy type class
        """
        from sqlalchemy import (
            Boolean,
            Date,
            DateTime,
            Float,
            Integer,
            LargeBinary,
            Numeric,
            String,
            Text,
            Time,
        )

        # Map JDBC types to SQLAlchemy types
        type_map = {
            # Numeric types
            -6: Integer,  # TINYINT
            5: Integer,  # SMALLINT
            4: Integer,  # INTEGER
            -5: Integer,  # BIGINT
            6: Float,  # FLOAT
            7: Float,  # REAL
            8: Float,  # DOUBLE
            2: Numeric,  # NUMERIC
            3: Numeric,  # DECIMAL
            # String types
            1: String,  # CHAR
            12: String,  # VARCHAR
            -1: Text,  # LONGVARCHAR
            # Date/time types
            91: Date,  # DATE
            92: Time,  # TIME
            93: DateTime,  # TIMESTAMP
            # Binary types
            -2: LargeBinary,  # BINARY
            -3: LargeBinary,  # VARBINARY
            -4: LargeBinary,  # LONGVARBINARY
            # Boolean
            16: Boolean,  # BOOLEAN
            -7: Boolean,  # BIT
        }

        # Check type name for Access-specific types
        upper_name = type_name.upper() if type_name else ""

        if "COUNTER" in upper_name or "AUTOINCREMENT" in upper_name:
            return Integer
        if "CURRENCY" in upper_name or "MONEY" in upper_name:
            return Numeric
        if "MEMO" in upper_name or "LONGCHAR" in upper_name:
            return Text
        if "YESNO" in upper_name:
            return Boolean
        if "OLEOBJECT" in upper_name:
            return LargeBinary
        if "HYPERLINK" in upper_name:
            return String

        return type_map.get(jdbc_type, String)

    def get_columns(
        self,
        connection: Connection,
        table_name: str,
        schema: str | None = None,
        **kwargs: Any,
    ):  # type: ignore
        """Get column information for a table."""
        columns = []

        try:
            dbapi_conn = connection.connection.dbapi_connection
            metadata = dbapi_conn.jconn.getMetaData()
            result_set = metadata.getColumns(None, None, table_name.upper(), None)

            while result_set.next():
                column_name = result_set.getString("COLUMN_NAME")
                data_type = result_set.getInt("DATA_TYPE")
                type_name = result_set.getString("TYPE_NAME")
                nullable = result_set.getInt("NULLABLE") != 0
                default = result_set.getString("COLUMN_DEF")

                # Map Access types to SQLAlchemy types
                col_info = {
                    "name": column_name,
                    "type": self._jdbc_type_to_sqlalchemy(data_type, type_name),
                    "nullable": nullable,
                    "default": default,
                    "autoincrement": "COUNTER" in type_name.upper()
                    if type_name
                    else False,
                }
                columns.append(col_info)

            result_set.close()

        except Exception as e:
            logger.error(f"Failed to get columns for {table_name}: {e}")

        return columns


class MSAccessDialect(AccessDialect):
    """Alias for AccessDialect."""

    name = "msaccess"


# Export the dialect
dialect = AccessDialect
