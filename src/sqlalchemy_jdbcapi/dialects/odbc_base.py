"""
Base ODBC dialect for SQLAlchemy.

Provides the foundation for ODBC-based database dialects using pyodbc.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from sqlalchemy import pool
from sqlalchemy.engine import URL, default
from sqlalchemy.engine.interfaces import ReflectedColumn

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection as SAConnection

logger = logging.getLogger(__name__)


class ODBCDialect(default.DefaultDialect):
    """
    Base ODBC dialect for SQLAlchemy.

    This provides common functionality for all ODBC-based dialects.
    """

    driver = "pyodbc"
    supports_statement_cache = True
    supports_native_decimal = True
    supports_unicode_binds = True
    supports_unicode_statements = True
    supports_multivalues_insert = True
    supports_native_boolean = False

    default_paramstyle = "qmark"
    poolclass = pool.QueuePool

    # ODBC-specific attributes
    pyodbc_driver_name: str | None = None
    default_schema_name: str | None = None

    @classmethod
    def import_dbapi(cls) -> Any:
        """Import the pyodbc module."""
        try:
            import pyodbc

            return pyodbc
        except ImportError as e:
            raise ImportError(
                "pyodbc is required for ODBC dialects. "
                "Install with: pip install 'sqlalchemy-jdbcapi[odbc]' or pip install pyodbc"
            ) from e

    def create_connect_args(self, url: URL) -> tuple[list[Any], dict[str, Any]]:
        """
        Build connection arguments from SQLAlchemy URL.

        Args:
            url: SQLAlchemy connection URL.

        Returns:
            Tuple of (args, kwargs) for connect function.
        """
        opts = url.translate_connect_args(
            username="uid", password="pwd", database="database"
        )
        opts.update(url.query)

        # Build ODBC connection string
        keys = opts.keys()
        conn_str_parts = []

        # Add driver
        if "driver" not in keys and self.pyodbc_driver_name:
            conn_str_parts.append(f"DRIVER={{{self.pyodbc_driver_name}}}")

        # Add server
        if "host" in keys and opts["host"]:
            host = opts.pop("host")
            port = opts.pop("port", None)
            if port:
                conn_str_parts.append(f"SERVER={host},{port}")
            else:
                conn_str_parts.append(f"SERVER={host}")

        # Add database
        if "database" in keys and opts.get("database"):
            conn_str_parts.append(f"DATABASE={opts.pop('database')}")

        # Add UID/PWD
        if "uid" in keys and opts.get("uid"):
            conn_str_parts.append(f"UID={opts.pop('uid')}")
        if "pwd" in keys and opts.get("pwd"):
            conn_str_parts.append(f"PWD={opts.pop('pwd')}")

        # Add remaining options
        for key, value in opts.items():
            if value is not None:
                conn_str_parts.append(f"{key}={value}")

        connection_string = ";".join(conn_str_parts)

        return ([connection_string], {})

    def get_schema_names(self, connection: SAConnection, **kwargs: Any) -> list[str]:
        """
        Get list of schema names.

        Args:
            connection: SQLAlchemy connection.
            **kwargs: Additional arguments.

        Returns:
            List of schema names.
        """
        cursor = connection.connection.cursor()
        try:
            schemas = []
            for row in cursor.tables():
                if row.table_schem and row.table_schem not in schemas:
                    schemas.append(row.table_schem)
            return sorted(schemas)
        finally:
            cursor.close()

    def get_table_names(
        self, connection: SAConnection, schema: str | None = None, **kwargs: Any
    ) -> list[str]:
        """
        Get list of table names in a schema.

        Args:
            connection: SQLAlchemy connection.
            schema: Schema name (optional).
            **kwargs: Additional arguments.

        Returns:
            List of table names.
        """
        cursor = connection.connection.cursor()
        try:
            tables = []
            for row in cursor.tables(schema=schema, tableType="TABLE"):
                tables.append(row.table_name)
            return sorted(tables)
        finally:
            cursor.close()

    def get_view_names(
        self, connection: SAConnection, schema: str | None = None, **kwargs: Any
    ) -> list[str]:
        """
        Get list of view names in a schema.

        Args:
            connection: SQLAlchemy connection.
            schema: Schema name (optional).
            **kwargs: Additional arguments.

        Returns:
            List of view names.
        """
        cursor = connection.connection.cursor()
        try:
            views = []
            for row in cursor.tables(schema=schema, tableType="VIEW"):
                views.append(row.table_name)
            return sorted(views)
        finally:
            cursor.close()

    def has_table(
        self,
        connection: SAConnection,
        table_name: str,
        schema: str | None = None,
        **kwargs: Any,
    ) -> bool:
        """
        Check if a table exists.

        Args:
            connection: SQLAlchemy connection.
            table_name: Table name.
            schema: Schema name (optional).
            **kwargs: Additional arguments.

        Returns:
            True if table exists, False otherwise.
        """
        cursor = connection.connection.cursor()
        try:
            for row in cursor.tables(table=table_name, schema=schema):
                if row.table_name == table_name:
                    return True
            return False
        finally:
            cursor.close()

    def get_columns(
        self,
        connection: SAConnection,
        table_name: str,
        schema: str | None = None,
        **kwargs: Any,
    ) -> list[ReflectedColumn]:
        """
        Get column information for a table.

        Args:
            connection: SQLAlchemy connection.
            table_name: Table name.
            schema: Schema name (optional).
            **kwargs: Additional arguments.

        Returns:
            List of column dictionaries.
        """
        cursor = connection.connection.cursor()
        try:
            columns = []
            for row in cursor.columns(table=table_name, schema=schema):
                column_info = {
                    "name": row.column_name,
                    "type": self._get_column_type(
                        row.type_name, row.column_size, row.decimal_digits
                    ),
                    "nullable": row.nullable == 1,
                    "default": row.column_def,
                }
                columns.append(column_info)
            return columns
        finally:
            cursor.close()

    def _get_column_type(  # noqa: C901 - Type mapping requires complexity
        self, type_name: str, size: int | None, precision: int | None
    ) -> Any:
        """
        Map ODBC type name to SQLAlchemy type.

        Args:
            type_name: ODBC type name.
            size: Column size.
            precision: Decimal precision.

        Returns:
            SQLAlchemy type object.
        """
        from sqlalchemy import types

        # Basic type mapping
        type_name_upper = type_name.upper()

        if "INT" in type_name_upper:
            return types.INTEGER()
        if "VARCHAR" in type_name_upper or "CHAR" in type_name_upper:
            return types.VARCHAR(length=size) if size else types.VARCHAR()
        if "TEXT" in type_name_upper:
            return types.TEXT()
        if "FLOAT" in type_name_upper or "REAL" in type_name_upper:
            return types.FLOAT()
        if "DECIMAL" in type_name_upper or "NUMERIC" in type_name_upper:
            return types.NUMERIC(precision=size, scale=precision)
        if "DATE" in type_name_upper and "TIME" not in type_name_upper:
            return types.DATE()
        if "TIME" in type_name_upper and "STAMP" not in type_name_upper:
            return types.TIME()
        if "TIMESTAMP" in type_name_upper or "DATETIME" in type_name_upper:
            return types.TIMESTAMP()
        if "BOOL" in type_name_upper:
            return types.BOOLEAN()
        if "BLOB" in type_name_upper or "BINARY" in type_name_upper:
            return types.BLOB()
        # Default to VARCHAR for unknown types
        return types.VARCHAR()

    def get_pk_constraint(
        self,
        connection: SAConnection,
        table_name: str,
        schema: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get primary key constraint information.

        Args:
            connection: SQLAlchemy connection.
            table_name: Table name.
            schema: Schema name (optional).
            **kwargs: Additional arguments.

        Returns:
            Dictionary with 'constrained_columns' and 'name'.
        """
        cursor = connection.connection.cursor()
        try:
            pk_columns = []
            pk_name = None
            for row in cursor.primaryKeys(table=table_name, schema=schema):
                pk_columns.append(row.column_name)
                if pk_name is None:
                    pk_name = row.pk_name

            return {
                "constrained_columns": pk_columns,
                "name": pk_name,
            }
        finally:
            cursor.close()

    def get_foreign_keys(
        self,
        connection: SAConnection,
        table_name: str,
        schema: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get foreign key constraints.

        Args:
            connection: SQLAlchemy connection.
            table_name: Table name.
            schema: Schema name (optional).
            **kwargs: Additional arguments.

        Returns:
            List of foreign key dictionaries.
        """
        cursor = connection.connection.cursor()
        try:
            fks: dict[str, dict[str, Any]] = {}
            for row in cursor.foreignKeys(table=table_name, schema=schema):
                fk_name = row.fk_name or f"fk_{len(fks)}"
                if fk_name not in fks:
                    fks[fk_name] = {
                        "name": fk_name,
                        "constrained_columns": [],
                        "referred_schema": row.pktable_schem,
                        "referred_table": row.pktable_name,
                        "referred_columns": [],
                    }
                fks[fk_name]["constrained_columns"].append(row.fkcolumn_name)
                fks[fk_name]["referred_columns"].append(row.pkcolumn_name)

            return list(fks.values())
        finally:
            cursor.close()

    def get_indexes(
        self,
        connection: SAConnection,
        table_name: str,
        schema: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get index information.

        Args:
            connection: SQLAlchemy connection.
            table_name: Table name.
            schema: Schema name (optional).
            **kwargs: Additional arguments.

        Returns:
            List of index dictionaries.
        """
        cursor = connection.connection.cursor()
        try:
            indexes: dict[str, dict[str, Any]] = {}
            for row in cursor.statistics(table=table_name, schema=schema):
                if row.index_name:
                    if row.index_name not in indexes:
                        indexes[row.index_name] = {
                            "name": row.index_name,
                            "column_names": [],
                            "unique": row.non_unique == 0,
                        }
                    indexes[row.index_name]["column_names"].append(row.column_name)

            return list(indexes.values())
        finally:
            cursor.close()
