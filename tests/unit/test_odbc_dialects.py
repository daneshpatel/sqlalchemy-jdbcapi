"""
Comprehensive tests for ODBC dialect functionality.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from sqlalchemy.engine import URL

from sqlalchemy_jdbcapi.dialects.odbc_base import ODBCDialect
from sqlalchemy_jdbcapi.dialects.odbc_mssql import MSSQLODBCDialect
from sqlalchemy_jdbcapi.dialects.odbc_mysql import MariaDBODBCDialect, MySQLODBCDialect
from sqlalchemy_jdbcapi.dialects.odbc_oracle import OracleODBCDialect
from sqlalchemy_jdbcapi.dialects.odbc_postgresql import PostgreSQLODBCDialect


class TestODBCDialectBase:
    """Test base ODBC dialect functionality."""

    @patch("builtins.__import__")
    def test_import_dbapi(self, mock_import):
        """Test importing pyodbc module."""
        mock_pyodbc = Mock()
        mock_import.return_value = mock_pyodbc

        dialect = ODBCDialect()
        dbapi = dialect.import_dbapi()
        assert dbapi is not None

    @patch("builtins.__import__")
    def test_import_dbapi_not_installed(self, mock_import):
        """Test error when pyodbc not installed."""
        mock_import.side_effect = ImportError("No module named 'pyodbc'")

        dialect = ODBCDialect()
        with pytest.raises(ImportError, match="pyodbc is required"):
            dialect.import_dbapi()

    def test_driver_attributes(self):
        """Test basic driver attributes."""
        dialect = ODBCDialect()
        assert dialect.driver == "pyodbc"
        assert dialect.supports_statement_cache is True
        assert dialect.default_paramstyle == "qmark"

    def test_create_connect_args_basic(self):
        """Test basic connection string creation."""
        dialect = ODBCDialect()
        dialect.pyodbc_driver_name = "Test Driver"

        url = URL.create(
            "odbcapi+test",
            username="user",
            password="pass",
            host="localhost",
            port=5432,
            database="testdb",
        )

        args, _kwargs = dialect.create_connect_args(url)

        assert len(args) == 1
        conn_str = args[0]
        assert "DRIVER={Test Driver}" in conn_str
        assert "SERVER=localhost,5432" in conn_str
        assert "DATABASE=testdb" in conn_str
        assert "UID=user" in conn_str
        assert "PWD=pass" in conn_str

    def test_create_connect_args_no_port(self):
        """Test connection string without port."""
        dialect = ODBCDialect()
        dialect.pyodbc_driver_name = "Test Driver"

        url = URL.create(
            "odbcapi+test",
            username="user",
            password="pass",
            host="localhost",
            database="testdb",
        )

        args, _kwargs = dialect.create_connect_args(url)

        conn_str = args[0]
        assert "SERVER=localhost" in conn_str
        assert "SERVER=localhost," not in conn_str

    def test_create_connect_args_query_params(self):
        """Test connection string with query parameters."""
        dialect = ODBCDialect()
        dialect.pyodbc_driver_name = "Test Driver"

        url = URL.create(
            "odbcapi+test",
            username="user",
            password="pass",
            host="localhost",
            database="testdb",
            query={"TrustServerCertificate": "yes", "Encrypt": "yes"},
        )

        args, _kwargs = dialect.create_connect_args(url)

        conn_str = args[0]
        assert "TrustServerCertificate=yes" in conn_str
        assert "Encrypt=yes" in conn_str


class TestPostgreSQLODBCDialect:
    """Test PostgreSQL ODBC dialect."""

    def test_dialect_name(self):
        """Test dialect name and driver."""
        dialect = PostgreSQLODBCDialect()
        assert dialect.name == "postgresql"
        assert dialect.driver == "odbcapi+postgresql"

    def test_pyodbc_driver_name(self):
        """Test ODBC driver name."""
        dialect = PostgreSQLODBCDialect()
        assert dialect.pyodbc_driver_name == "PostgreSQL Unicode"

    def test_supports_features(self):
        """Test PostgreSQL-specific features."""
        dialect = PostgreSQLODBCDialect()
        assert dialect.supports_sequences is True
        assert dialect.supports_native_boolean is True
        assert dialect.default_schema_name == "public"

    def test_server_version_info(self):
        """Test extracting PostgreSQL version."""
        dialect = PostgreSQLODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ["PostgreSQL 15.4 on x86_64-pc-linux-gnu"]

        version = dialect._get_server_version_info(mock_conn)

        assert version == (15, 4)
        mock_cursor.execute.assert_called_once_with("SELECT version()")
        mock_cursor.close.assert_called_once()

    def test_server_version_info_old_format(self):
        """Test extracting version from different format."""
        dialect = PostgreSQLODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ["PostgreSQL 14"]

        version = dialect._get_server_version_info(mock_conn)

        # Should handle partial version gracefully
        assert isinstance(version, tuple)


class TestMySQLODBCDialect:
    """Test MySQL ODBC dialect."""

    def test_dialect_name(self):
        """Test dialect name and driver."""
        dialect = MySQLODBCDialect()
        assert dialect.name == "mysql"
        assert dialect.driver == "odbcapi+mysql"

    def test_pyodbc_driver_name(self):
        """Test ODBC driver name."""
        dialect = MySQLODBCDialect()
        assert dialect.pyodbc_driver_name == "MySQL ODBC 8.0 Driver"

    def test_supports_features(self):
        """Test MySQL-specific features."""
        dialect = MySQLODBCDialect()
        assert dialect.supports_native_decimal is True

    def test_server_version_info(self):
        """Test extracting MySQL version."""
        dialect = MySQLODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ["8.0.34"]

        version = dialect._get_server_version_info(mock_conn)

        assert version == (8, 0, 34)
        mock_cursor.execute.assert_called_once_with("SELECT VERSION()")
        mock_cursor.close.assert_called_once()

    def test_server_version_info_with_suffix(self):
        """Test version extraction with suffix."""
        dialect = MySQLODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ["8.0.34-log"]

        version = dialect._get_server_version_info(mock_conn)

        assert version == (8, 0, 34)


class TestMariaDBODBCDialect:
    """Test MariaDB ODBC dialect."""

    def test_dialect_name(self):
        """Test dialect name and driver."""
        dialect = MariaDBODBCDialect()
        assert dialect.name == "mariadb"
        assert dialect.driver == "odbcapi+mariadb"

    def test_pyodbc_driver_name(self):
        """Test ODBC driver name."""
        dialect = MariaDBODBCDialect()
        assert dialect.pyodbc_driver_name == "MariaDB ODBC 3.1 Driver"

    def test_supports_features(self):
        """Test MariaDB-specific features."""
        dialect = MariaDBODBCDialect()
        assert dialect.supports_native_decimal is True
        assert dialect.supports_sequences is True  # 10.3+

    def test_server_version_info(self):
        """Test extracting MariaDB version."""
        dialect = MariaDBODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ["10.11.3-MariaDB"]

        version = dialect._get_server_version_info(mock_conn)

        assert version == (10, 11, 3)


class TestMSSQLODBCDialect:
    """Test SQL Server ODBC dialect."""

    def test_dialect_name(self):
        """Test dialect name and driver."""
        dialect = MSSQLODBCDialect()
        assert dialect.name == "mssql"
        assert dialect.driver == "odbcapi+mssql"

    def test_pyodbc_driver_name(self):
        """Test ODBC driver name."""
        dialect = MSSQLODBCDialect()
        assert dialect.pyodbc_driver_name == "ODBC Driver 18 for SQL Server"

    def test_supports_features(self):
        """Test SQL Server-specific features."""
        dialect = MSSQLODBCDialect()
        assert dialect.supports_sequences is True  # 2012+
        assert dialect.supports_native_boolean is False
        assert dialect.default_schema_name == "dbo"

    def test_server_version_info(self):
        """Test extracting SQL Server version."""
        dialect = MSSQLODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ["15.0.2000.5"]

        version = dialect._get_server_version_info(mock_conn)

        assert version == (15, 0)
        mock_cursor.execute.assert_called_once_with(
            "SELECT SERVERPROPERTY('ProductVersion')"
        )


class TestOracleODBCDialect:
    """Test Oracle ODBC dialect."""

    def test_dialect_name(self):
        """Test dialect name and driver."""
        dialect = OracleODBCDialect()
        assert dialect.name == "oracle"
        assert dialect.driver == "odbcapi+oracle"

    def test_pyodbc_driver_name(self):
        """Test ODBC driver name."""
        dialect = OracleODBCDialect()
        assert "Oracle" in dialect.pyodbc_driver_name
        assert "instantclient" in dialect.pyodbc_driver_name

    def test_supports_features(self):
        """Test Oracle-specific features."""
        dialect = OracleODBCDialect()
        assert dialect.supports_sequences is True
        assert dialect.supports_native_boolean is False

    def test_server_version_info_from_instance(self):
        """Test extracting Oracle version from v$instance."""
        dialect = OracleODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ["19.0.0.0.0"]

        version = dialect._get_server_version_info(mock_conn)

        assert version == (19, 0)
        mock_cursor.close.assert_called_once()

    def test_server_version_info_from_banner(self):
        """Test extracting Oracle version from banner (fallback)."""
        dialect = OracleODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor

        # First query fails, second succeeds
        mock_cursor.execute.side_effect = [
            Exception("Access denied"),
            None,
        ]
        mock_cursor.fetchone.side_effect = [
            ["Oracle Database 19c Enterprise Edition Release 19.0.0.0.0"],
        ]

        version = dialect._get_server_version_info(mock_conn)

        assert version == (19, 0)

    def test_server_version_info_fallback(self):
        """Test fallback when all queries fail."""
        dialect = OracleODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("All queries failed")

        version = dialect._get_server_version_info(mock_conn)

        assert version == (0, 0)


class TestODBCReflection:
    """Test ODBC reflection capabilities."""

    def test_get_schema_names(self):
        """Test getting list of schemas."""
        dialect = ODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor

        # Mock rows returned from tables()
        mock_row1 = Mock()
        mock_row1.table_schem = "schema1"
        mock_row2 = Mock()
        mock_row2.table_schem = "schema2"
        mock_row3 = Mock()
        mock_row3.table_schem = "schema1"  # Duplicate

        mock_cursor.tables.return_value = [mock_row1, mock_row2, mock_row3]

        schemas = dialect.get_schema_names(mock_conn)

        assert schemas == ["schema1", "schema2"]
        mock_cursor.close.assert_called_once()

    def test_get_table_names(self):
        """Test getting list of tables."""
        dialect = ODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor

        mock_row1 = Mock()
        mock_row1.table_name = "users"
        mock_row2 = Mock()
        mock_row2.table_name = "posts"

        mock_cursor.tables.return_value = [mock_row1, mock_row2]

        tables = dialect.get_table_names(mock_conn, schema="public")

        assert tables == ["posts", "users"]  # Sorted
        mock_cursor.tables.assert_called_once_with(schema="public", tableType="TABLE")

    def test_get_view_names(self):
        """Test getting list of views."""
        dialect = ODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor

        mock_row = Mock()
        mock_row.table_name = "user_view"

        mock_cursor.tables.return_value = [mock_row]

        views = dialect.get_view_names(mock_conn, schema="public")

        assert views == ["user_view"]
        mock_cursor.tables.assert_called_once_with(schema="public", tableType="VIEW")

    def test_has_table_exists(self):
        """Test checking if table exists (true case)."""
        dialect = ODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor

        mock_row = Mock()
        mock_row.table_name = "users"

        mock_cursor.tables.return_value = [mock_row]

        exists = dialect.has_table(mock_conn, "users", schema="public")

        assert exists is True

    def test_has_table_not_exists(self):
        """Test checking if table exists (false case)."""
        dialect = ODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor

        mock_cursor.tables.return_value = []

        exists = dialect.has_table(mock_conn, "nonexistent", schema="public")

        assert exists is False

    def test_get_columns(self):
        """Test getting column information."""
        dialect = ODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor

        mock_col1 = Mock()
        mock_col1.column_name = "id"
        mock_col1.type_name = "INTEGER"
        mock_col1.column_size = None
        mock_col1.decimal_digits = None
        mock_col1.nullable = 0
        mock_col1.column_def = None

        mock_col2 = Mock()
        mock_col2.column_name = "name"
        mock_col2.type_name = "VARCHAR"
        mock_col2.column_size = 100
        mock_col2.decimal_digits = None
        mock_col2.nullable = 1
        mock_col2.column_def = None

        mock_cursor.columns.return_value = [mock_col1, mock_col2]

        columns = dialect.get_columns(mock_conn, "users", schema="public")

        assert len(columns) == 2
        assert columns[0]["name"] == "id"
        assert columns[0]["nullable"] is False
        assert columns[1]["name"] == "name"
        assert columns[1]["nullable"] is True

    def test_get_pk_constraint(self):
        """Test getting primary key constraint."""
        dialect = ODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor

        mock_pk1 = Mock()
        mock_pk1.column_name = "id"
        mock_pk1.pk_name = "users_pkey"

        mock_cursor.primaryKeys.return_value = [mock_pk1]

        pk = dialect.get_pk_constraint(mock_conn, "users", schema="public")

        assert pk["constrained_columns"] == ["id"]
        assert pk["name"] == "users_pkey"

    def test_get_foreign_keys(self):
        """Test getting foreign key constraints."""
        dialect = ODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor

        mock_fk = Mock()
        mock_fk.fk_name = "posts_user_id_fkey"
        mock_fk.fkcolumn_name = "user_id"
        mock_fk.pktable_schem = "public"
        mock_fk.pktable_name = "users"
        mock_fk.pkcolumn_name = "id"

        mock_cursor.foreignKeys.return_value = [mock_fk]

        fks = dialect.get_foreign_keys(mock_conn, "posts", schema="public")

        assert len(fks) == 1
        assert fks[0]["name"] == "posts_user_id_fkey"
        assert fks[0]["constrained_columns"] == ["user_id"]
        assert fks[0]["referred_table"] == "users"
        assert fks[0]["referred_columns"] == ["id"]

    def test_get_indexes(self):
        """Test getting index information."""
        dialect = ODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor

        mock_idx = Mock()
        mock_idx.index_name = "idx_users_email"
        mock_idx.column_name = "email"
        mock_idx.non_unique = 0  # Unique index

        mock_cursor.statistics.return_value = [mock_idx]

        indexes = dialect.get_indexes(mock_conn, "users", schema="public")

        assert len(indexes) == 1
        assert indexes[0]["name"] == "idx_users_email"
        assert indexes[0]["column_names"] == ["email"]
        assert indexes[0]["unique"] is True


class TestODBCTypeMapping:
    """Test ODBC type mapping to SQLAlchemy types."""

    def test_integer_type(self):
        """Test INTEGER mapping."""
        dialect = ODBCDialect()
        sa_type = dialect._get_column_type("INTEGER", None, None)
        assert sa_type.__class__.__name__ == "INTEGER"

    def test_varchar_type(self):
        """Test VARCHAR mapping with size."""
        dialect = ODBCDialect()
        sa_type = dialect._get_column_type("VARCHAR", 100, None)
        assert sa_type.__class__.__name__ == "VARCHAR"

    def test_text_type(self):
        """Test TEXT mapping."""
        dialect = ODBCDialect()
        sa_type = dialect._get_column_type("TEXT", None, None)
        assert sa_type.__class__.__name__ == "TEXT"

    def test_numeric_type(self):
        """Test NUMERIC/DECIMAL mapping."""
        dialect = ODBCDialect()
        sa_type = dialect._get_column_type("DECIMAL", 10, 2)
        assert sa_type.__class__.__name__ == "NUMERIC"

    def test_datetime_types(self):
        """Test DATE, TIME, TIMESTAMP mapping."""
        dialect = ODBCDialect()

        date_type = dialect._get_column_type("DATE", None, None)
        assert date_type.__class__.__name__ == "DATE"

        time_type = dialect._get_column_type("TIME", None, None)
        assert time_type.__class__.__name__ == "TIME"

        timestamp_type = dialect._get_column_type("TIMESTAMP", None, None)
        assert timestamp_type.__class__.__name__ == "TIMESTAMP"

    def test_boolean_type(self):
        """Test BOOLEAN mapping."""
        dialect = ODBCDialect()
        sa_type = dialect._get_column_type("BOOLEAN", None, None)
        assert sa_type.__class__.__name__ == "BOOLEAN"

    def test_blob_type(self):
        """Test BLOB/BINARY mapping."""
        dialect = ODBCDialect()
        sa_type = dialect._get_column_type("BLOB", None, None)
        assert sa_type.__class__.__name__ == "BLOB"

    def test_unknown_type_fallback(self):
        """Test unknown type defaults to VARCHAR."""
        dialect = ODBCDialect()
        sa_type = dialect._get_column_type("UNKNOWN_TYPE", None, None)
        assert sa_type.__class__.__name__ == "VARCHAR"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_connection_string(self):
        """Test handling of minimal connection info."""
        dialect = ODBCDialect()
        dialect.pyodbc_driver_name = "Test Driver"

        url = URL.create("odbcapi+test")

        args, _kwargs = dialect.create_connect_args(url)

        conn_str = args[0]
        assert "DRIVER={Test Driver}" in conn_str

    def test_get_columns_empty_result(self):
        """Test getting columns for empty table."""
        dialect = ODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor
        mock_cursor.columns.return_value = []

        columns = dialect.get_columns(mock_conn, "empty_table")

        assert columns == []

    def test_get_foreign_keys_multiple_columns(self):
        """Test multi-column foreign key."""
        dialect = ODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor

        mock_fk1 = Mock()
        mock_fk1.fk_name = "composite_fk"
        mock_fk1.fkcolumn_name = "col1"
        mock_fk1.pktable_schem = "public"
        mock_fk1.pktable_name = "parent"
        mock_fk1.pkcolumn_name = "id1"

        mock_fk2 = Mock()
        mock_fk2.fk_name = "composite_fk"
        mock_fk2.fkcolumn_name = "col2"
        mock_fk2.pktable_schem = "public"
        mock_fk2.pktable_name = "parent"
        mock_fk2.pkcolumn_name = "id2"

        mock_cursor.foreignKeys.return_value = [mock_fk1, mock_fk2]

        fks = dialect.get_foreign_keys(mock_conn, "child")

        assert len(fks) == 1
        assert fks[0]["constrained_columns"] == ["col1", "col2"]
        assert fks[0]["referred_columns"] == ["id1", "id2"]

    def test_get_indexes_composite(self):
        """Test composite index."""
        dialect = ODBCDialect()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor

        mock_idx1 = Mock()
        mock_idx1.index_name = "composite_idx"
        mock_idx1.column_name = "col1"
        mock_idx1.non_unique = 1

        mock_idx2 = Mock()
        mock_idx2.index_name = "composite_idx"
        mock_idx2.column_name = "col2"
        mock_idx2.non_unique = 1

        mock_cursor.statistics.return_value = [mock_idx1, mock_idx2]

        indexes = dialect.get_indexes(mock_conn, "table")

        assert len(indexes) == 1
        assert indexes[0]["column_names"] == ["col1", "col2"]
        assert indexes[0]["unique"] is False
