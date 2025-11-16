"""
Integration tests for package installation and setup.

These tests verify that the package is correctly installed and configured.
"""

from __future__ import annotations

import sys
from importlib.metadata import entry_points

import pytest


class TestPackageInstallation:
    """Test that the package is properly installed."""

    def test_package_importable(self):
        """Test that the package can be imported."""
        import sqlalchemy_jdbcapi

        assert sqlalchemy_jdbcapi is not None

    def test_version_available(self):
        """Test that version is available."""
        import sqlalchemy_jdbcapi

        version = getattr(sqlalchemy_jdbcapi, "__version__", None)
        assert version is not None
        assert isinstance(version, str)

    def test_main_modules_importable(self):
        """Test that main modules can be imported."""
        # JDBC modules
        from sqlalchemy_jdbcapi.jdbc import driver_manager, jvm

        assert driver_manager is not None
        assert jvm is not None

        # ODBC modules (may fail if pyodbc not installed, that's ok)
        try:
            from sqlalchemy_jdbcapi.odbc import connection, exceptions

            assert connection is not None
            assert exceptions is not None
        except ImportError:
            # pyodbc not installed, skip
            pass

    def test_jdbc_dialects_importable(self):
        """Test that JDBC dialects can be imported."""
        from sqlalchemy_jdbcapi.dialects import (
            db2,
            mssql,
            mysql,
            oceanbase,
            oracle,
            postgresql,
            sqlite,
        )

        assert db2 is not None
        assert mssql is not None
        assert mysql is not None
        assert oceanbase is not None
        assert oracle is not None
        assert postgresql is not None
        assert sqlite is not None

    def test_odbc_dialects_importable(self):
        """Test that ODBC dialects can be imported."""
        from sqlalchemy_jdbcapi.dialects import (
            odbc_base,
            odbc_mssql,
            odbc_mysql,
            odbc_oracle,
            odbc_postgresql,
        )

        assert odbc_base is not None
        assert odbc_mssql is not None
        assert odbc_mysql is not None
        assert odbc_oracle is not None
        assert odbc_postgresql is not None


class TestEntryPoints:
    """Test that SQLAlchemy entry points are registered."""

    def test_jdbc_entry_points_registered(self):
        """Test that JDBC dialects are registered with SQLAlchemy."""
        eps = entry_points()

        # Handle both new and old API
        if hasattr(eps, "select"):
            dialects = list(eps.select(group="sqlalchemy.dialects"))
        else:
            dialects = eps.get("sqlalchemy.dialects", [])

        jdbc_dialects = [ep for ep in dialects if "jdbcapi" in ep.name]

        # Should have at least the main JDBC dialects
        jdbc_names = {ep.name for ep in jdbc_dialects}

        expected_dialects = {
            "jdbcapi.postgresql",
            "jdbcapi.mysql",
            "jdbcapi.mssql",
            "jdbcapi.oracle",
            "jdbcapi.db2",
            "jdbcapi.sqlite",
            "jdbcapi.mariadb",
        }

        assert expected_dialects.issubset(jdbc_names), (
            f"Missing JDBC dialects: {expected_dialects - jdbc_names}"
        )

    def test_odbc_entry_points_registered(self):
        """Test that ODBC dialects are registered with SQLAlchemy."""
        eps = entry_points()

        # Handle both new and old API
        if hasattr(eps, "select"):
            dialects = list(eps.select(group="sqlalchemy.dialects"))
        else:
            dialects = eps.get("sqlalchemy.dialects", [])

        odbc_dialects = [ep for ep in dialects if "odbcapi" in ep.name]

        # Should have ODBC dialects
        odbc_names = {ep.name for ep in odbc_dialects}

        expected_dialects = {
            "odbcapi.postgresql",
            "odbcapi.mysql",
            "odbcapi.mssql",
            "odbcapi.oracle",
        }

        assert expected_dialects.issubset(odbc_names), (
            f"Missing ODBC dialects: {expected_dialects - odbc_names}"
        )


class TestDriverManager:
    """Test driver manager functionality."""

    def test_recommended_drivers_available(self):
        """Test that recommended drivers are defined."""
        from sqlalchemy_jdbcapi.jdbc.driver_manager import RECOMMENDED_JDBC_DRIVERS

        assert len(RECOMMENDED_JDBC_DRIVERS) > 0

        # Check for common databases
        assert "postgresql" in RECOMMENDED_JDBC_DRIVERS
        assert "mysql" in RECOMMENDED_JDBC_DRIVERS
        assert "mssql" in RECOMMENDED_JDBC_DRIVERS
        assert "oracle" in RECOMMENDED_JDBC_DRIVERS

    def test_maven_urls_valid(self):
        """Test that Maven URLs are properly formatted."""
        from sqlalchemy_jdbcapi.jdbc.driver_manager import RECOMMENDED_JDBC_DRIVERS

        for db_name, driver in RECOMMENDED_JDBC_DRIVERS.items():
            url = driver.maven_url

            # Should start with Maven Central URL
            assert url.startswith("https://repo1.maven.org/maven2/"), (
                f"Invalid Maven URL for {db_name}: {url}"
            )

            # Should end with .jar
            assert url.endswith(".jar"), (
                f"Maven URL should end with .jar for {db_name}: {url}"
            )

            # Should contain version
            assert driver.version in url, f"Version not in URL for {db_name}"

    def test_driver_filenames(self):
        """Test that driver filenames are correctly generated."""
        from sqlalchemy_jdbcapi.jdbc.driver_manager import RECOMMENDED_JDBC_DRIVERS

        for db_name, driver in RECOMMENDED_JDBC_DRIVERS.items():
            filename = driver.filename

            # Should end with .jar
            assert filename.endswith(".jar"), (
                f"Filename should end with .jar for {db_name}: {filename}"
            )

            # Should contain artifact_id
            assert driver.artifact_id in filename, (
                f"Artifact ID not in filename for {db_name}"
            )

            # Should contain version
            assert driver.version in filename, f"Version not in filename for {db_name}"

    def test_get_driver_cache_dir(self):
        """Test getting driver cache directory."""
        from sqlalchemy_jdbcapi.jdbc.driver_manager import get_driver_cache_dir

        cache_dir = get_driver_cache_dir()

        assert cache_dir is not None
        assert cache_dir.name == "drivers"
        assert ".sqlalchemy-jdbcapi" in str(cache_dir)


class TestSQLAlchemyIntegration:
    """Test SQLAlchemy integration."""

    def test_jdbc_url_parsing(self):
        """Test that JDBC URLs can be parsed."""
        from sqlalchemy import make_url

        test_urls = [
            "jdbcapi+postgresql://user:pass@localhost:5432/testdb",
            "jdbcapi+mysql://user:pass@localhost:3306/testdb",
            "jdbcapi+mssql://user:pass@localhost:1433/testdb",
            "jdbcapi+oracle://user:pass@localhost:1521/testdb",
        ]

        for url_str in test_urls:
            url = make_url(url_str)
            assert url.drivername.startswith("jdbcapi+"), (
                f"Invalid driver name for {url_str}"
            )

    @pytest.mark.skipif(
        sys.modules.get("pyodbc") is None, reason="pyodbc not installed"
    )
    def test_odbc_url_parsing(self):
        """Test that ODBC URLs can be parsed (only if pyodbc installed)."""
        from sqlalchemy import make_url

        test_urls = [
            "odbcapi+postgresql://user:pass@localhost:5432/testdb",
            "odbcapi+mysql://user:pass@localhost:3306/testdb",
            "odbcapi+mssql://user:pass@localhost:1433/testdb",
            "odbcapi+oracle://user:pass@localhost:1521/testdb",
        ]

        for url_str in test_urls:
            url = make_url(url_str)
            assert url.drivername.startswith("odbcapi+"), (
                f"Invalid driver name for {url_str}"
            )

    def test_jdbc_dialect_loading(self):
        """Test that JDBC dialects can be loaded by SQLAlchemy."""
        from sqlalchemy import create_engine
        from sqlalchemy.pool import StaticPool

        # Create engine without connecting (just to test dialect loading)
        engine = create_engine(
            "jdbcapi+sqlite:///:memory:",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )

        assert engine is not None
        assert "SQLite" in engine.dialect.__class__.__name__


class TestExceptionHierarchy:
    """Test exception hierarchy."""

    def test_jdbc_exceptions(self):
        """Test JDBC exception imports."""
        from sqlalchemy_jdbcapi.jdbc.exceptions import (
            DatabaseError,
            Error,
            InterfaceError,
            JVMNotStartedError,
        )

        assert issubclass(InterfaceError, Error)
        assert issubclass(DatabaseError, Error)
        assert issubclass(JVMNotStartedError, Error)

    @pytest.mark.skipif(
        sys.modules.get("pyodbc") is None, reason="pyodbc not installed"
    )
    def test_odbc_exceptions(self):
        """Test ODBC exception imports (only if pyodbc installed)."""
        from sqlalchemy_jdbcapi.odbc.exceptions import (
            DatabaseError,
            Error,
            InterfaceError,
        )

        assert issubclass(InterfaceError, Error)
        assert issubclass(DatabaseError, Error)
