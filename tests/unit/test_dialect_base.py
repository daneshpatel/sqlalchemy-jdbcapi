"""
Tests for base JDBC dialect implementation.

Tests the abstract base class and common dialect functionality.
"""

from __future__ import annotations

import pytest

from sqlalchemy_jdbcapi.dialects.base import (
    JDBCDriverConfig,
)


class TestJDBCDriverConfig:
    """Test JDBC driver configuration."""

    def test_driver_config_creation(self):
        """Test creating driver config."""
        config = JDBCDriverConfig(
            driver_class="org.postgresql.Driver",
            jdbc_url_template="jdbc:postgresql://{host}:{port}/{database}",
            default_port=5432,
        )

        assert config.driver_class == "org.postgresql.Driver"
        assert config.default_port == 5432
        assert config.supports_transactions is True
        assert config.supports_schemas is True

    def test_format_jdbc_url_basic(self):
        """Test formatting JDBC URL."""
        config = JDBCDriverConfig(
            driver_class="org.postgresql.Driver",
            jdbc_url_template="jdbc:postgresql://{host}:{port}/{database}",
            default_port=5432,
        )

        url = config.format_jdbc_url("localhost", 5432, "mydb")

        assert url == "jdbc:postgresql://localhost:5432/mydb"

    def test_format_jdbc_url_default_port(self):
        """Test JDBC URL with default port."""
        config = JDBCDriverConfig(
            driver_class="org.postgresql.Driver",
            jdbc_url_template="jdbc:postgresql://{host}:{port}/{database}",
            default_port=5432,
        )

        # Port is None - should use default
        url = config.format_jdbc_url("localhost", None, "mydb")

        assert url == "jdbc:postgresql://localhost:5432/mydb"

    def test_format_jdbc_url_no_database(self):
        """Test JDBC URL without database."""
        config = JDBCDriverConfig(
            driver_class="org.mysql.Driver",
            jdbc_url_template="jdbc:mysql://{host}:{port}/{database}",
            default_port=3306,
        )

        url = config.format_jdbc_url("localhost", 3306, None)

        assert url == "jdbc:mysql://localhost:3306/"

    def test_format_jdbc_url_with_query_params(self):
        """Test JDBC URL with query parameters."""
        config = JDBCDriverConfig(
            driver_class="org.postgresql.Driver",
            jdbc_url_template="jdbc:postgresql://{host}:{port}/{database}",
            default_port=5432,
        )

        url = config.format_jdbc_url(
            "localhost", 5432, "mydb", query_params={"ssl": "true", "timeout": "30"}
        )

        assert "localhost:5432/mydb" in url
        assert "ssl=true" in url
        assert "timeout=30" in url

    def test_format_jdbc_url_with_existing_query(self):
        """Test adding params to URL that already has query string."""
        config = JDBCDriverConfig(
            driver_class="org.postgresql.Driver",
            jdbc_url_template="jdbc:postgresql://{host}:{port}/{database}?sslmode=require",
            default_port=5432,
        )

        url = config.format_jdbc_url(
            "localhost", 5432, "mydb", query_params={"timeout": "30"}
        )

        assert "sslmode=require" in url
        assert "timeout=30" in url
        # Should use & separator since ? already exists
        assert "&timeout=30" in url

    def test_driver_config_immutable(self):
        """Test that driver config is immutable (frozen dataclass)."""
        config = JDBCDriverConfig(
            driver_class="org.postgresql.Driver",
            jdbc_url_template="jdbc:postgresql://{host}:{port}/{database}",
            default_port=5432,
        )

        # Should not be able to modify
        with pytest.raises(AttributeError):
            config.default_port = 3306  # type: ignore

    def test_driver_config_supports_flags(self):
        """Test driver config feature flags."""
        # Config with all features disabled
        config = JDBCDriverConfig(
            driver_class="test.Driver",
            jdbc_url_template="jdbc:test://{host}",
            default_port=1234,
            supports_transactions=False,
            supports_schemas=False,
            supports_sequences=False,
        )

        assert config.supports_transactions is False
        assert config.supports_schemas is False
        assert config.supports_sequences is False
