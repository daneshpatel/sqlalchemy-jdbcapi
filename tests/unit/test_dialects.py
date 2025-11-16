"""
Unit tests for dialect implementations.
"""

from __future__ import annotations

import pytest
from sqlalchemy.engine.url import make_url

from sqlalchemy_jdbcapi.dialects import (
    DB2Dialect,
    MariaDBDialect,
    MSSQLDialect,
    MySQLDialect,
    OceanBaseDialect,
    OracleDialect,
    PostgreSQLDialect,
    SQLiteDialect,
)


class TestPostgreSQLDialect:
    """Tests for PostgreSQL dialect."""

    def test_driver_config(self) -> None:
        """Test PostgreSQL driver configuration."""
        config = PostgreSQLDialect.get_driver_config()
        assert config.driver_class == "org.postgresql.Driver"
        assert config.default_port == 5432
        assert config.supports_transactions is True

    def test_create_connect_args(self) -> None:
        """Test connection argument creation."""
        dialect = PostgreSQLDialect()
        url = make_url("jdbcapi+postgresql://user:pass@localhost:5432/testdb")

        args, kwargs = dialect.create_connect_args(url)

        assert len(args) == 0
        assert kwargs["jclassname"] == "org.postgresql.Driver"
        assert "jdbc:postgresql://" in kwargs["url"]
        assert kwargs["driver_args"]["user"] == "user"
        assert kwargs["driver_args"]["password"] == "pass"


class TestOracleDialect:
    """Tests for Oracle dialect."""

    def test_driver_config(self) -> None:
        """Test Oracle driver configuration."""
        config = OracleDialect.get_driver_config()
        assert config.driver_class == "oracle.jdbc.OracleDriver"
        assert config.default_port == 1521
        assert config.supports_sequences is True

    def test_create_connect_args(self) -> None:
        """Test connection argument creation."""
        dialect = OracleDialect()
        url = make_url("jdbcapi+oracle://user:pass@localhost:1521/ORCL")

        args, kwargs = dialect.create_connect_args(url)

        assert len(args) == 0
        assert kwargs["jclassname"] == "oracle.jdbc.OracleDriver"
        assert "jdbc:oracle:thin:@" in kwargs["url"]


class TestMySQLDialect:
    """Tests for MySQL dialect."""

    def test_driver_config(self) -> None:
        """Test MySQL driver configuration."""
        config = MySQLDialect.get_driver_config()
        assert config.driver_class == "com.mysql.cj.jdbc.Driver"
        assert config.default_port == 3306

    def test_create_connect_args(self) -> None:
        """Test connection argument creation."""
        dialect = MySQLDialect()
        url = make_url("jdbcapi+mysql://root:password@localhost:3306/mydb")

        args, kwargs = dialect.create_connect_args(url)

        assert len(args) == 0
        assert "jdbc:mysql://" in kwargs["url"]


class TestMariaDBDialect:
    """Tests for MariaDB dialect."""

    def test_driver_config(self) -> None:
        """Test MariaDB driver configuration."""
        config = MariaDBDialect.get_driver_config()
        assert config.driver_class == "org.mariadb.jdbc.Driver"
        assert config.supports_sequences is True


class TestMSSQLDialect:
    """Tests for SQL Server dialect."""

    def test_driver_config(self) -> None:
        """Test SQL Server driver configuration."""
        config = MSSQLDialect.get_driver_config()
        assert config.driver_class == "com.microsoft.sqlserver.jdbc.SQLServerDriver"
        assert config.default_port == 1433


class TestDB2Dialect:
    """Tests for DB2 dialect."""

    def test_driver_config(self) -> None:
        """Test DB2 driver configuration."""
        config = DB2Dialect.get_driver_config()
        assert config.driver_class == "com.ibm.db2.jcc.DB2Driver"
        assert config.default_port == 50000


class TestSQLiteDialect:
    """Tests for SQLite dialect."""

    def test_driver_config(self) -> None:
        """Test SQLite driver configuration."""
        config = SQLiteDialect.get_driver_config()
        assert config.driver_class == "org.sqlite.JDBC"

    def test_memory_database(self) -> None:
        """Test in-memory database URL."""
        dialect = SQLiteDialect()
        url = make_url("jdbcapi+sqlite:///:memory:")

        args, kwargs = dialect.create_connect_args(url)

        assert "jdbc:sqlite::memory:" in kwargs["url"]
