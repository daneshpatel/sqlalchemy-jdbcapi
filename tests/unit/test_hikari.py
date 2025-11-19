"""
Unit tests for HikariCP connection pool integration.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from sqlalchemy_jdbcapi.jdbc.hikari import HikariConfig, HikariConnectionPool


class TestHikariConfig:
    """Tests for HikariConfig dataclass."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = HikariConfig(
            jdbc_url="jdbc:postgresql://localhost:5432/testdb",
            username="user",
            password="pass",
        )

        assert config.jdbc_url == "jdbc:postgresql://localhost:5432/testdb"
        assert config.username == "user"
        assert config.password == "pass"  # noqa: S105
        assert config.maximum_pool_size == 10
        assert (
            config.minimum_idle == 10
        )  # Best practice: equal to max for fixed-size pool
        assert config.connection_timeout == 30000
        assert config.idle_timeout == 600000
        assert config.max_lifetime == 1800000
        assert config.keepalive_time == 0  # Disabled by default
        assert config.connection_test_query is None
        assert config.connection_init_sql is None
        assert config.pool_name == "JDBCAPIPool"
        assert config.auto_commit is False
        assert config.read_only is False
        assert config.transaction_isolation is None

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = HikariConfig(
            jdbc_url="jdbc:mysql://localhost:3306/mydb",
            username="root",
            password="secret",
            driver_class="com.mysql.cj.jdbc.Driver",
            maximum_pool_size=50,
            minimum_idle=10,
            connection_timeout=60000,
            pool_name="MyPool",
            auto_commit=True,
            leak_detection_threshold=30000,
            data_source_properties={"cachePrepStmts": "true"},
        )

        assert config.maximum_pool_size == 50
        assert config.minimum_idle == 10
        assert config.connection_timeout == 60000
        assert config.pool_name == "MyPool"
        assert config.auto_commit is True
        assert config.leak_detection_threshold == 30000
        assert config.data_source_properties == {"cachePrepStmts": "true"}

    def test_config_with_schema(self) -> None:
        """Test configuration with catalog and schema."""
        config = HikariConfig(
            jdbc_url="jdbc:oracle:thin:@localhost:1521/ORCL",
            catalog="MY_CATALOG",
            schema="MY_SCHEMA",
        )

        assert config.catalog == "MY_CATALOG"
        assert config.schema == "MY_SCHEMA"


class TestHikariConnectionPool:
    """Tests for HikariConnectionPool."""

    @patch("sqlalchemy_jdbcapi.jdbc.hikari.start_jvm")
    def test_pool_initialization_jvm_error(self, mock_start_jvm: MagicMock) -> None:
        """Test pool initialization handles JVM errors."""
        mock_start_jvm.side_effect = Exception("JVM failed")

        config = HikariConfig(
            jdbc_url="jdbc:postgresql://localhost:5432/testdb",
        )

        from sqlalchemy_jdbcapi.jdbc.exceptions import InterfaceError

        with pytest.raises(InterfaceError, match="Failed to start JVM"):
            HikariConnectionPool(config)

    @patch("sqlalchemy_jdbcapi.jdbc.hikari.start_jvm")
    @patch("jpype.JClass")
    def test_pool_initialization_success(
        self, mock_jclass: MagicMock, mock_start_jvm: MagicMock
    ) -> None:
        """Test successful pool initialization."""
        # Mock HikariConfig class
        mock_hikari_config = MagicMock()
        mock_hikari_datasource = MagicMock()

        def jclass_side_effect(class_name):
            if "HikariConfig" in class_name:
                return MagicMock(return_value=mock_hikari_config)
            if "HikariDataSource" in class_name:
                return MagicMock(return_value=mock_hikari_datasource)
            return MagicMock()

        mock_jclass.side_effect = jclass_side_effect

        config = HikariConfig(
            jdbc_url="jdbc:postgresql://localhost:5432/testdb",
            username="user",
            password="pass",
            maximum_pool_size=20,
            pool_name="TestPool",
        )

        pool = HikariConnectionPool(config)

        # Verify configuration was set
        mock_hikari_config.setJdbcUrl.assert_called_with(
            "jdbc:postgresql://localhost:5432/testdb"
        )
        mock_hikari_config.setUsername.assert_called_with("user")
        mock_hikari_config.setPassword.assert_called_with("pass")
        mock_hikari_config.setMaximumPoolSize.assert_called_with(20)
        mock_hikari_config.setPoolName.assert_called_with("TestPool")

        # Cleanup
        pool.close()

    @patch("sqlalchemy_jdbcapi.jdbc.hikari.start_jvm")
    @patch("jpype.JClass")
    def test_pool_get_connection(
        self, mock_jclass: MagicMock, mock_start_jvm: MagicMock
    ) -> None:
        """Test getting a connection from the pool."""
        mock_datasource = MagicMock()
        mock_connection = MagicMock()
        mock_datasource.getConnection.return_value = mock_connection

        mock_jclass.side_effect = lambda x: MagicMock(
            return_value=mock_datasource if "DataSource" in x else MagicMock()
        )

        config = HikariConfig(jdbc_url="jdbc:postgresql://localhost:5432/testdb")
        pool = HikariConnectionPool(config)

        conn = pool.get_connection()

        assert conn is mock_connection
        mock_datasource.getConnection.assert_called_once()

        pool.close()

    @patch("sqlalchemy_jdbcapi.jdbc.hikari.start_jvm")
    @patch("jpype.JClass")
    def test_pool_close(
        self, mock_jclass: MagicMock, mock_start_jvm: MagicMock
    ) -> None:
        """Test closing the pool."""
        mock_datasource = MagicMock()
        mock_jclass.side_effect = lambda x: MagicMock(
            return_value=mock_datasource if "DataSource" in x else MagicMock()
        )

        config = HikariConfig(jdbc_url="jdbc:postgresql://localhost:5432/testdb")
        pool = HikariConnectionPool(config)

        pool.close()

        mock_datasource.close.assert_called_once()
        assert pool._closed is True

    @patch("sqlalchemy_jdbcapi.jdbc.hikari.start_jvm")
    @patch("jpype.JClass")
    def test_pool_stats(
        self, mock_jclass: MagicMock, mock_start_jvm: MagicMock
    ) -> None:
        """Test getting pool statistics."""
        mock_datasource = MagicMock()
        mock_pool_mxbean = MagicMock()
        mock_pool_mxbean.getTotalConnections.return_value = 10
        mock_pool_mxbean.getActiveConnections.return_value = 3
        mock_pool_mxbean.getIdleConnections.return_value = 7
        mock_pool_mxbean.getThreadsAwaitingConnection.return_value = 0
        mock_datasource.getHikariPoolMXBean.return_value = mock_pool_mxbean

        mock_jclass.side_effect = lambda x: MagicMock(
            return_value=mock_datasource if "DataSource" in x else MagicMock()
        )

        config = HikariConfig(
            jdbc_url="jdbc:postgresql://localhost:5432/testdb",
            pool_name="StatsPool",
        )
        pool = HikariConnectionPool(config)

        stats = pool.pool_stats

        assert stats["pool_name"] == "StatsPool"
        assert stats["total_connections"] == 10
        assert stats["active_connections"] == 3
        assert stats["idle_connections"] == 7
        assert stats["threads_awaiting_connection"] == 0

        pool.close()

    @patch("sqlalchemy_jdbcapi.jdbc.hikari.start_jvm")
    @patch("jpype.JClass")
    def test_pool_context_manager(
        self, mock_jclass: MagicMock, mock_start_jvm: MagicMock
    ) -> None:
        """Test pool as context manager."""
        mock_datasource = MagicMock()
        mock_jclass.side_effect = lambda x: MagicMock(
            return_value=mock_datasource if "DataSource" in x else MagicMock()
        )

        config = HikariConfig(jdbc_url="jdbc:postgresql://localhost:5432/testdb")

        with HikariConnectionPool(config) as pool:
            assert pool._closed is False

        mock_datasource.close.assert_called_once()

    @patch("sqlalchemy_jdbcapi.jdbc.hikari.start_jvm")
    @patch("jpype.JClass")
    def test_get_connection_when_closed(
        self, mock_jclass: MagicMock, mock_start_jvm: MagicMock
    ) -> None:
        """Test getting connection from closed pool raises error."""
        mock_datasource = MagicMock()
        mock_jclass.side_effect = lambda x: MagicMock(
            return_value=mock_datasource if "DataSource" in x else MagicMock()
        )

        config = HikariConfig(jdbc_url="jdbc:postgresql://localhost:5432/testdb")
        pool = HikariConnectionPool(config)
        pool.close()

        from sqlalchemy_jdbcapi.jdbc.exceptions import InterfaceError

        with pytest.raises(InterfaceError, match="pool is closed"):
            pool.get_connection()
