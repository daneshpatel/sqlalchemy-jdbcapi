"""
Unit tests for dialect implementations.
"""

from __future__ import annotations

from sqlalchemy.engine.url import make_url

from sqlalchemy_jdbcapi.dialects import (
    # New dialects
    AccessDialect,
    AvaticaDialect,
    CalciteDialect,
    # Existing dialects
    DB2Dialect,
    GBase8sDialect,
    IBMiSeriesDialect,
    MariaDBDialect,
    MSSQLDialect,
    MySQLDialect,
    OracleDialect,
    PhoenixDialect,
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
        assert kwargs["driver_args"]["password"] == "pass"  # noqa: S105 - Test password


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

        _args, kwargs = dialect.create_connect_args(url)

        assert "jdbc:sqlite::memory:" in kwargs["url"]


# New dialect tests


class TestGBase8sDialect:
    """Tests for GBase 8s dialect."""

    def test_driver_config(self) -> None:
        """Test GBase 8s driver configuration."""
        config = GBase8sDialect.get_driver_config()
        assert config.driver_class == "com.gbasedbt.jdbc.Driver"
        assert config.default_port == 9088
        assert config.supports_transactions is True
        assert config.supports_sequences is True

    def test_dialect_name(self) -> None:
        """Test dialect name."""
        dialect = GBase8sDialect()
        assert dialect.name == "gbase8s"
        assert dialect.driver == "jdbcapi"

    def test_capabilities(self) -> None:
        """Test GBase 8s capabilities."""
        dialect = GBase8sDialect()
        assert dialect.supports_sequences is True
        assert dialect.supports_identity_columns is True
        assert dialect.supports_native_boolean is False


class TestIBMiSeriesDialect:
    """Tests for IBM iSeries dialect."""

    def test_driver_config(self) -> None:
        """Test IBM iSeries driver configuration."""
        config = IBMiSeriesDialect.get_driver_config()
        assert config.driver_class == "com.ibm.as400.access.AS400JDBCDriver"
        assert config.supports_transactions is True
        assert config.supports_sequences is True

    def test_dialect_name(self) -> None:
        """Test dialect name."""
        dialect = IBMiSeriesDialect()
        assert dialect.name == "iseries"
        assert dialect.driver == "jdbcapi"

    def test_create_connect_args(self) -> None:
        """Test connection argument creation for iSeries."""
        url = make_url("jdbcapi+iseries://user:pass@as400host/MYLIB")

        result = IBMiSeriesDialect.create_connect_args(url)

        assert result[0] == "com.ibm.as400.access.AS400JDBCDriver"
        assert "jdbc:as400://" in result[1]
        assert "as400host" in result[1]

    def test_capabilities(self) -> None:
        """Test IBM iSeries capabilities."""
        dialect = IBMiSeriesDialect()
        assert dialect.supports_sequences is True
        assert dialect.supports_identity_columns is True
        assert dialect.default_schema_name == "QGPL"


class TestAccessDialect:
    """Tests for Microsoft Access dialect."""

    def test_driver_config(self) -> None:
        """Test Access driver configuration."""
        config = AccessDialect.get_driver_config()
        assert config.driver_class == "net.ucanaccess.jdbc.UcanaccessDriver"
        assert config.default_port == 0  # File-based
        assert config.supports_schemas is False
        assert config.supports_sequences is False

    def test_dialect_name(self) -> None:
        """Test dialect name."""
        dialect = AccessDialect()
        assert dialect.name == "access"
        assert dialect.driver == "jdbcapi"

    def test_capabilities(self) -> None:
        """Test Access capabilities (limited)."""
        dialect = AccessDialect()
        assert dialect.supports_sequences is False
        assert dialect.supports_identity_columns is True
        assert dialect.supports_native_boolean is True
        assert dialect.supports_multivalues_insert is False


class TestAvaticaDialect:
    """Tests for Apache Avatica dialect."""

    def test_driver_config(self) -> None:
        """Test Avatica driver configuration."""
        config = AvaticaDialect.get_driver_config()
        assert config.driver_class == "org.apache.calcite.avatica.remote.Driver"
        assert config.default_port == 8765
        assert config.supports_transactions is True

    def test_dialect_name(self) -> None:
        """Test dialect name."""
        dialect = AvaticaDialect()
        assert dialect.name == "avatica"
        assert dialect.driver == "jdbcapi"

    def test_is_async(self) -> None:
        """Test async flag is false for sync dialect."""
        dialect = AvaticaDialect()
        assert not getattr(dialect, "is_async", False)


class TestPhoenixDialect:
    """Tests for Apache Phoenix dialect."""

    def test_driver_config(self) -> None:
        """Test Phoenix driver configuration."""
        config = PhoenixDialect.get_driver_config()
        assert config.driver_class == "org.apache.phoenix.jdbc.PhoenixDriver"
        assert config.default_port == 2181  # ZooKeeper port

    def test_dialect_name(self) -> None:
        """Test dialect name."""
        dialect = PhoenixDialect()
        assert dialect.name == "phoenix"

    def test_supports_sequences(self) -> None:
        """Test Phoenix supports sequences."""
        dialect = PhoenixDialect()
        assert dialect.supports_sequences is True


class TestCalciteDialect:
    """Tests for Apache Calcite dialect."""

    def test_driver_config(self) -> None:
        """Test Calcite driver configuration."""
        config = CalciteDialect.get_driver_config()
        assert config.driver_class == "org.apache.calcite.jdbc.Driver"

    def test_dialect_name(self) -> None:
        """Test dialect name."""
        dialect = CalciteDialect()
        assert dialect.name == "calcite"
