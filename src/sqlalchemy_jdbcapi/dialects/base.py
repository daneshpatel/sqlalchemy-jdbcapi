"""
Base JDBC dialect implementation following SOLID principles.

This module provides the abstract base class for all JDBC dialects,
implementing common functionality and defining the interface that
database-specific dialects must implement.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar

from sqlalchemy import pool
from sqlalchemy.engine import Connection, Dialect, reflection
from sqlalchemy.engine.url import URL
from sqlalchemy.types import (
    BIGINT,
    BINARY,
    BOOLEAN,
    CHAR,
    DATE,
    DECIMAL,
    FLOAT,
    INTEGER,
    NUMERIC,
    REAL,
    SMALLINT,
    TIME,
    TIMESTAMP,
    VARBINARY,
    VARCHAR,
)

from ..jdbc.exceptions import DatabaseError, OperationalError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class JDBCDriverConfig:
    """
    Configuration for a JDBC driver.

    This encapsulates all driver-specific configuration in a single
    immutable object, following the Single Responsibility Principle.
    """

    driver_class: str
    """Fully qualified Java class name of the JDBC driver"""

    jdbc_url_template: str
    """Template for JDBC URL (e.g., 'jdbc:postgresql://{host}:{port}/{database}')"""

    default_port: int
    """Default port number for the database"""

    supports_transactions: bool = True
    """Whether the database supports transactions"""

    supports_schemas: bool = True
    """Whether the database supports schemas"""

    supports_sequences: bool = True
    """Whether the database supports sequences"""

    def format_jdbc_url(
        self,
        host: str,
        port: int | None,
        database: str | None,
        query_params: dict[str, Any] | None = None,
    ) -> str:
        """
        Format a JDBC connection URL.

        Args:
            host: Database host
            port: Database port (uses default_port if None)
            database: Database name
            query_params: Additional query parameters

        Returns:
            Formatted JDBC URL
        """
        port = port or self.default_port
        url = self.jdbc_url_template.format(
            host=host, port=port, database=database or ""
        )

        if query_params:
            params = "&".join(f"{k}={v}" for k, v in query_params.items())
            separator = "?" if "?" not in url else "&"
            url = f"{url}{separator}{params}"

        return url


class BaseJDBCDialect(Dialect, ABC):
    """
    Abstract base class for JDBC-based SQLAlchemy dialects.

    This class implements the Template Method pattern, providing common
    JDBC functionality while allowing database-specific customization
    through abstract methods.

    Subclasses must implement:
    - get_driver_config(): Return driver configuration
    - _get_server_version_info(): Parse database version

    SQLAlchemy 2.0+ compatible with full type hints.
    """

    # DB-API module (our custom JDBC bridge)
    driver = "jdbcapi"

    # SQLAlchemy capabilities
    supports_native_decimal = True
    supports_sane_rowcount = False
    supports_sane_multi_rowcount = False
    supports_unicode_binds = True
    supports_statement_cache = True
    supports_server_side_cursors = False

    # Connection pooling
    supports_native_boolean = True
    poolclass = pool.QueuePool

    # Execution options
    execution_ctx_cls: ClassVar[type | None] = None

    @classmethod
    def dbapi(cls) -> type:
        """
        Return the DB-API module.

        Returns our custom JDBC bridge module that implements
        the Python DB-API 2.0 specification.
        """
        from .. import jdbc

        return jdbc  # type: ignore

    @classmethod
    @abstractmethod
    def get_driver_config(cls) -> JDBCDriverConfig:
        """
        Get JDBC driver configuration for this dialect.

        This method must be implemented by each database dialect
        to provide driver-specific configuration.

        Returns:
            JDBCDriverConfig instance
        """
        ...

    def create_connect_args(self, url: URL) -> tuple[list[Any], dict[str, Any]]:
        """
        Create connection arguments from SQLAlchemy URL.

        Converts a SQLAlchemy URL into arguments for our JDBC connect()
        function, following the Adapter pattern.

        Args:
            url: SQLAlchemy connection URL

        Returns:
            Tuple of (args, kwargs) for jdbc.connect()
        """
        config = self.get_driver_config()

        # Build JDBC URL
        jdbc_url = config.format_jdbc_url(
            host=url.host or "localhost",
            port=url.port,
            database=url.database,
            query_params=dict(url.query) if url.query else None,
        )

        logger.debug(f"Creating connection to: {jdbc_url}")

        # Build driver arguments
        driver_args: dict[str, Any] = {}

        if url.username:
            driver_args["user"] = url.username
        if url.password:
            driver_args["password"] = url.password

        # Add query parameters as connection properties
        if url.query:
            driver_args.update(url.query)

        # Connection arguments for jdbc.connect()
        kwargs = {
            "jclassname": config.driver_class,
            "url": jdbc_url,
            "driver_args": driver_args if driver_args else None,
        }

        return ([], kwargs)

    def initialize(self, connection: Connection) -> None:
        """
        Initialize a new connection.

        Called when a new connection is established to set up
        connection-specific settings.

        Args:
            connection: SQLAlchemy connection object
        """
        super().initialize(connection)

        # Set up server version
        if not hasattr(self, "_server_version_info"):
            self._server_version_info = self._get_server_version_info(connection)
            logger.debug(f"Server version: {self._server_version_info}")

    @abstractmethod
    def _get_server_version_info(self, connection: Connection) -> tuple[int, ...]:
        """
        Get database server version information.

        This must be implemented by each dialect to parse version
        information in a database-specific way.

        Args:
            connection: SQLAlchemy connection

        Returns:
            Tuple of version numbers (e.g., (14, 5, 0))
        """
        ...

    def is_disconnect(self, e: Exception, connection: Any, cursor: Any) -> bool:
        """
        Check if an exception indicates a database disconnect.

        Args:
            e: Exception that occurred
            connection: Database connection
            cursor: Database cursor

        Returns:
            True if this is a disconnect error
        """
        if isinstance(e, (DatabaseError, OperationalError)):
            error_str = str(e).lower()
            disconnect_indicators = [
                "connection is closed",
                "cursor is closed",
                "connection reset",
                "broken pipe",
                "connection refused",
                "connection lost",
                "can't connect",
                "connection terminated",
            ]
            return any(indicator in error_str for indicator in disconnect_indicators)

        return False

    def do_rollback(self, dbapi_connection: Any) -> None:
        """
        Perform a rollback on the connection.

        Some JDBC drivers have issues with rollback,
        this can be overridden by subclasses.

        Args:
            dbapi_connection: DB-API connection object
        """
        try:
            dbapi_connection.rollback()
        except Exception as e:
            logger.warning(f"Rollback failed: {e}")

    def do_commit(self, dbapi_connection: Any) -> None:
        """
        Perform a commit on the connection.

        Args:
            dbapi_connection: DB-API connection object
        """
        dbapi_connection.commit()

    def do_close(self, dbapi_connection: Any) -> None:
        """
        Close the connection.

        Args:
            dbapi_connection: DB-API connection object
        """
        dbapi_connection.close()

    def do_ping(self, dbapi_connection: Any) -> bool:
        """
        Check if connection is alive.

        Args:
            dbapi_connection: DB-API connection object

        Returns:
            True if connection is alive, False otherwise
        """
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.debug(f"Ping failed: {e}")
            return False

    def get_isolation_level(self, dbapi_connection: Any) -> str | None:
        """
        Get the current transaction isolation level.

        Args:
            dbapi_connection: DB-API connection object

        Returns:
            Isolation level name or None
        """
        # This would need JDBC-specific implementation
        # Most JDBC connections support getTransactionIsolation()
        return None

    def set_isolation_level(self, dbapi_connection: Any, level: str) -> None:
        """
        Set the transaction isolation level.

        Args:
            dbapi_connection: DB-API connection object
            level: Isolation level to set
        """
        # This would need JDBC-specific implementation
        # Most JDBC connections support setTransactionIsolation()

    # ========================================================================
    # JDBC Reflection Methods - Using DatabaseMetaData API
    # ========================================================================

    def _get_jdbc_metadata(self, connection: Connection) -> Any:
        """
        Get JDBC DatabaseMetaData object from connection.

        Args:
            connection: SQLAlchemy connection

        Returns:
            JDBC DatabaseMetaData object
        """
        # Get the raw JDBC connection
        dbapi_conn = connection.connection.dbapi_connection
        if hasattr(dbapi_conn, "_jdbc_connection"):
            jdbc_conn = dbapi_conn._jdbc_connection
            return jdbc_conn.getMetaData()
        raise OperationalError("Cannot access JDBC connection metadata")

    def _jdbc_type_to_sqlalchemy(self, jdbc_type_name: str, jdbc_type: int) -> Any:
        """
        Convert JDBC type to SQLAlchemy type.

        Args:
            jdbc_type_name: JDBC type name (e.g., 'VARCHAR')
            jdbc_type: JDBC type code (from java.sql.Types)

        Returns:
            SQLAlchemy type instance
        """
        # Map common JDBC type codes to SQLAlchemy types
        type_map = {
            -7: BOOLEAN,  # BIT
            -6: SMALLINT,  # TINYINT
            -5: BIGINT,  # BIGINT
            -4: VARBINARY,  # LONGVARBINARY
            -3: VARBINARY,  # VARBINARY
            -2: BINARY,  # BINARY
            -1: VARCHAR,  # LONGVARCHAR
            1: CHAR,  # CHAR
            2: NUMERIC,  # NUMERIC
            3: DECIMAL,  # DECIMAL
            4: INTEGER,  # INTEGER
            5: SMALLINT,  # SMALLINT
            6: FLOAT,  # FLOAT
            7: REAL,  # REAL
            8: FLOAT,  # DOUBLE
            12: VARCHAR,  # VARCHAR
            16: BOOLEAN,  # BOOLEAN
            91: DATE,  # DATE
            92: TIME,  # TIME
            93: TIMESTAMP,  # TIMESTAMP
        }

        return type_map.get(jdbc_type, VARCHAR())

    @reflection.cache
    def get_schema_names(self, connection: Connection, **kw: Any) -> list[str]:
        """
        Get list of schema names using JDBC DatabaseMetaData.

        Args:
            connection: SQLAlchemy connection
            **kw: Additional keyword arguments

        Returns:
            List of schema names
        """
        try:
            metadata = self._get_jdbc_metadata(connection)
            schemas = []

            rs = metadata.getSchemas()
            while rs.next():
                schema_name = rs.getString("TABLE_SCHEM")
                if schema_name:
                    schemas.append(schema_name)
            rs.close()

            logger.debug(f"Found {len(schemas)} schemas")
            return schemas

        except Exception as e:
            logger.warning(f"Failed to get schema names: {e}")
            return []

    @reflection.cache
    def get_table_names(
        self, connection: Connection, schema: str | None = None, **kw: Any
    ) -> list[str]:
        """
        Get list of table names using JDBC DatabaseMetaData.

        Args:
            connection: SQLAlchemy connection
            schema: Schema name (None for default schema)
            **kw: Additional keyword arguments

        Returns:
            List of table names
        """
        try:
            metadata = self._get_jdbc_metadata(connection)
            tables = []

            # getTables(catalog, schemaPattern, tableNamePattern, types[])
            rs = metadata.getTables(None, schema, "%", ["TABLE"])
            while rs.next():
                table_name = rs.getString("TABLE_NAME")
                if table_name:
                    tables.append(table_name)
            rs.close()

            logger.debug(f"Found {len(tables)} tables in schema '{schema}'")
            return tables

        except Exception as e:
            logger.warning(f"Failed to get table names: {e}")
            return []

    @reflection.cache
    def get_view_names(
        self, connection: Connection, schema: str | None = None, **kw: Any
    ) -> list[str]:
        """
        Get list of view names using JDBC DatabaseMetaData.

        Args:
            connection: SQLAlchemy connection
            schema: Schema name (None for default schema)
            **kw: Additional keyword arguments

        Returns:
            List of view names
        """
        try:
            metadata = self._get_jdbc_metadata(connection)
            views = []

            rs = metadata.getTables(None, schema, "%", ["VIEW"])
            while rs.next():
                view_name = rs.getString("TABLE_NAME")
                if view_name:
                    views.append(view_name)
            rs.close()

            logger.debug(f"Found {len(views)} views in schema '{schema}'")
            return views

        except Exception as e:
            logger.warning(f"Failed to get view names: {e}")
            return []

    def has_table(
        self,
        connection: Connection,
        table_name: str,
        schema: str | None = None,
        **kw: Any,
    ) -> bool:
        """
        Check if a table exists using JDBC DatabaseMetaData.

        Args:
            connection: SQLAlchemy connection
            table_name: Table name to check
            schema: Schema name (None for default schema)
            **kw: Additional keyword arguments

        Returns:
            True if table exists, False otherwise
        """
        try:
            metadata = self._get_jdbc_metadata(connection)

            rs = metadata.getTables(None, schema, table_name, ["TABLE"])
            exists = rs.next()
            rs.close()

            logger.debug(f"Table '{schema}.{table_name}' exists: {exists}")
            return exists

        except Exception as e:
            logger.warning(f"Failed to check table existence: {e}")
            return False

    @reflection.cache
    def get_columns(
        self,
        connection: Connection,
        table_name: str,
        schema: str | None = None,
        **kw: Any,
    ) -> list[dict[str, Any]]:
        """
        Get column definitions for a table using JDBC DatabaseMetaData.

        Args:
            connection: SQLAlchemy connection
            table_name: Table name
            schema: Schema name (None for default schema)
            **kw: Additional keyword arguments

        Returns:
            List of column dictionaries with keys:
            - name: Column name
            - type: SQLAlchemy type instance
            - nullable: Boolean
            - default: Default value (string or None)
            - autoincrement: Boolean
        """
        try:
            metadata = self._get_jdbc_metadata(connection)
            columns = []

            rs = metadata.getColumns(None, schema, table_name, "%")
            while rs.next():
                column_name = rs.getString("COLUMN_NAME")
                data_type = rs.getInt("DATA_TYPE")
                type_name = rs.getString("TYPE_NAME")
                column_size = rs.getInt("COLUMN_SIZE")
                nullable = rs.getInt("NULLABLE") == 1  # DatabaseMetaData.columnNullable
                column_def = rs.getString("COLUMN_DEF")
                is_autoincrement = rs.getString("IS_AUTOINCREMENT")

                # Convert JDBC type to SQLAlchemy type
                sa_type = self._jdbc_type_to_sqlalchemy(type_name, data_type)

                # Apply size for character/binary types
                if hasattr(sa_type, "length") and column_size:
                    if isinstance(sa_type, (VARCHAR, CHAR, VARBINARY, BINARY)):
                        sa_type = type(sa_type)(length=column_size)

                columns.append(
                    {
                        "name": column_name,
                        "type": sa_type,
                        "nullable": nullable,
                        "default": column_def,
                        "autoincrement": is_autoincrement == "YES"
                        if is_autoincrement
                        else False,
                    }
                )

            rs.close()

            logger.debug(
                f"Found {len(columns)} columns for table '{schema}.{table_name}'"
            )
            return columns

        except Exception as e:
            logger.warning(f"Failed to get columns: {e}")
            return []

    @reflection.cache
    def get_pk_constraint(
        self,
        connection: Connection,
        table_name: str,
        schema: str | None = None,
        **kw: Any,
    ) -> dict[str, Any]:
        """
        Get primary key constraint for a table using JDBC DatabaseMetaData.

        Args:
            connection: SQLAlchemy connection
            table_name: Table name
            schema: Schema name (None for default schema)
            **kw: Additional keyword arguments

        Returns:
            Dictionary with keys:
            - name: Constraint name
            - constrained_columns: List of column names
        """
        try:
            metadata = self._get_jdbc_metadata(connection)
            pk_columns = []
            pk_name = None

            rs = metadata.getPrimaryKeys(None, schema, table_name)
            while rs.next():
                column_name = rs.getString("COLUMN_NAME")
                pk_name = rs.getString("PK_NAME")
                key_seq = rs.getInt("KEY_SEQ")
                pk_columns.append((key_seq, column_name))

            rs.close()

            # Sort by KEY_SEQ to maintain correct column order
            pk_columns.sort(key=lambda x: x[0])
            constrained_columns = [col for _, col in pk_columns]

            result = {
                "name": pk_name,
                "constrained_columns": constrained_columns,
            }

            logger.debug(f"Primary key for '{schema}.{table_name}': {result}")
            return result

        except Exception as e:
            logger.warning(f"Failed to get primary key: {e}")
            return {"name": None, "constrained_columns": []}

    @reflection.cache
    def get_foreign_keys(
        self,
        connection: Connection,
        table_name: str,
        schema: str | None = None,
        **kw: Any,
    ) -> list[dict[str, Any]]:
        """
        Get foreign key constraints for a table using JDBC DatabaseMetaData.

        Args:
            connection: SQLAlchemy connection
            table_name: Table name
            schema: Schema name (None for default schema)
            **kw: Additional keyword arguments

        Returns:
            List of dictionaries with keys:
            - name: Constraint name
            - constrained_columns: List of local column names
            - referred_schema: Referenced schema name
            - referred_table: Referenced table name
            - referred_columns: List of referenced column names
        """
        try:
            metadata = self._get_jdbc_metadata(connection)
            fks: dict[str, dict[str, Any]] = {}

            rs = metadata.getImportedKeys(None, schema, table_name)
            while rs.next():
                fk_name = rs.getString("FK_NAME")
                fk_column = rs.getString("FKCOLUMN_NAME")
                pk_table = rs.getString("PKTABLE_NAME")
                pk_schema = rs.getString("PKTABLE_SCHEM")
                pk_column = rs.getString("PKCOLUMN_NAME")
                key_seq = rs.getInt("KEY_SEQ")

                if fk_name not in fks:
                    fks[fk_name] = {
                        "name": fk_name,
                        "constrained_columns": [],
                        "referred_schema": pk_schema,
                        "referred_table": pk_table,
                        "referred_columns": [],
                        "_seq": [],
                    }

                fks[fk_name]["_seq"].append(key_seq)
                fks[fk_name]["constrained_columns"].append(fk_column)
                fks[fk_name]["referred_columns"].append(pk_column)

            rs.close()

            # Sort columns by KEY_SEQ
            result = []
            for fk_name, fk_data in fks.items():
                # Sort by sequence
                sorted_data = sorted(
                    zip(
                        fk_data["_seq"],
                        fk_data["constrained_columns"],
                        fk_data["referred_columns"],
                    )
                )
                fk_data["constrained_columns"] = [col for _, col, _ in sorted_data]
                fk_data["referred_columns"] = [col for _, _, col in sorted_data]
                del fk_data["_seq"]
                result.append(fk_data)

            logger.debug(
                f"Found {len(result)} foreign keys for '{schema}.{table_name}'"
            )
            return result

        except Exception as e:
            logger.warning(f"Failed to get foreign keys: {e}")
            return []

    @reflection.cache
    def get_indexes(
        self,
        connection: Connection,
        table_name: str,
        schema: str | None = None,
        **kw: Any,
    ) -> list[dict[str, Any]]:
        """
        Get indexes for a table using JDBC DatabaseMetaData.

        Args:
            connection: SQLAlchemy connection
            table_name: Table name
            schema: Schema name (None for default schema)
            **kw: Additional keyword arguments

        Returns:
            List of dictionaries with keys:
            - name: Index name
            - column_names: List of column names
            - unique: Boolean
        """
        try:
            metadata = self._get_jdbc_metadata(connection)
            indexes: dict[str, dict[str, Any]] = {}

            # getIndexInfo(catalog, schema, table, unique, approximate)
            rs = metadata.getIndexInfo(None, schema, table_name, False, True)
            while rs.next():
                index_name = rs.getString("INDEX_NAME")

                # Skip statistics
                if not index_name:
                    continue

                column_name = rs.getString("COLUMN_NAME")
                non_unique = rs.getBoolean("NON_UNIQUE")
                ordinal_position = rs.getInt("ORDINAL_POSITION")

                if index_name not in indexes:
                    indexes[index_name] = {
                        "name": index_name,
                        "column_names": [],
                        "unique": not non_unique,
                        "_positions": [],
                    }

                indexes[index_name]["_positions"].append(ordinal_position)
                indexes[index_name]["column_names"].append(column_name)

            rs.close()

            # Sort columns by ordinal position
            result = []
            for idx_name, idx_data in indexes.items():
                sorted_data = sorted(
                    zip(idx_data["_positions"], idx_data["column_names"])
                )
                idx_data["column_names"] = [col for _, col in sorted_data]
                del idx_data["_positions"]
                result.append(idx_data)

            logger.debug(f"Found {len(result)} indexes for '{schema}.{table_name}'")
            return result

        except Exception as e:
            logger.warning(f"Failed to get indexes: {e}")
            return []

    @reflection.cache
    def get_unique_constraints(
        self,
        connection: Connection,
        table_name: str,
        schema: str | None = None,
        **kw: Any,
    ) -> list[dict[str, Any]]:
        """
        Get unique constraints for a table.

        This is extracted from get_indexes() by filtering for unique indexes.

        Args:
            connection: SQLAlchemy connection
            table_name: Table name
            schema: Schema name (None for default schema)
            **kw: Additional keyword arguments

        Returns:
            List of dictionaries with keys:
            - name: Constraint name
            - column_names: List of column names
        """
        try:
            indexes = self.get_indexes(connection, table_name, schema, **kw)
            unique_constraints = [
                {"name": idx["name"], "column_names": idx["column_names"]}
                for idx in indexes
                if idx.get("unique", False)
            ]

            logger.debug(
                f"Found {len(unique_constraints)} unique constraints for '{schema}.{table_name}'"
            )
            return unique_constraints

        except Exception as e:
            logger.warning(f"Failed to get unique constraints: {e}")
            return []

    @reflection.cache
    def get_check_constraints(
        self,
        connection: Connection,
        table_name: str,
        schema: str | None = None,
        **kw: Any,
    ) -> list[dict[str, Any]]:
        """
        Get check constraints for a table.

        Note: JDBC DatabaseMetaData doesn't have a standard method for check constraints.
        This returns an empty list. Database-specific dialects should override this
        method to query system tables if check constraint information is needed.

        Args:
            connection: SQLAlchemy connection
            table_name: Table name
            schema: Schema name (None for default schema)
            **kw: Additional keyword arguments

        Returns:
            List of dictionaries with keys:
            - name: Constraint name
            - sqltext: Check constraint SQL expression
        """
        # JDBC doesn't provide standard access to check constraints
        # Subclasses can override to query database-specific system tables
        logger.debug(
            f"Check constraints not available via JDBC for '{schema}.{table_name}'"
        )
        return []

    def __repr__(self) -> str:
        """String representation of the dialect."""
        return f"<{self.__class__.__name__}>"
