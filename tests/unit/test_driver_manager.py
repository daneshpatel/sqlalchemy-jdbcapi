"""
Comprehensive tests for JDBC driver manager functionality.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sqlalchemy_jdbcapi.jdbc.driver_manager import (
    RECOMMENDED_JDBC_DRIVERS,
    JDBCDriver,
    clear_driver_cache,
    download_driver,
    get_all_driver_paths,
    get_classpath_with_drivers,
    get_driver_cache_dir,
    get_driver_path,
    list_cached_drivers,
    verify_driver,
)


class TestJDBCDriver:
    """Test JDBCDriver metadata class."""

    def test_jdbc_driver_creation(self):
        """Test creating JDBCDriver with all fields."""
        driver = JDBCDriver(
            group_id="org.postgresql",
            artifact_id="postgresql",
            version="42.7.1",
            classifier=None,
        )
        assert driver.group_id == "org.postgresql"
        assert driver.artifact_id == "postgresql"
        assert driver.version == "42.7.1"
        assert driver.classifier is None

    def test_jdbc_driver_filename(self):
        """Test JAR filename generation."""
        driver = JDBCDriver(
            group_id="org.postgresql",
            artifact_id="postgresql",
            version="42.7.1",
        )
        assert driver.filename == "postgresql-42.7.1.jar"

    def test_jdbc_driver_filename_with_classifier(self):
        """Test JAR filename with classifier."""
        driver = JDBCDriver(
            group_id="com.microsoft.sqlserver",
            artifact_id="mssql-jdbc",
            version="12.6.0",
            classifier="jre11",
        )
        assert driver.filename == "mssql-jdbc-12.6.0-jre11.jar"

    def test_jdbc_driver_maven_url(self):
        """Test Maven Central URL generation."""
        driver = JDBCDriver(
            group_id="org.postgresql",
            artifact_id="postgresql",
            version="42.7.1",
        )
        expected = (
            "https://repo1.maven.org/maven2/org/postgresql/postgresql/"
            "42.7.1/postgresql-42.7.1.jar"
        )
        assert driver.maven_url == expected

    def test_jdbc_driver_maven_url_nested_group(self):
        """Test Maven URL with nested group ID."""
        driver = JDBCDriver(
            group_id="com.oracle.database.jdbc",
            artifact_id="ojdbc11",
            version="23.3.0.23.09",
        )
        assert "com/oracle/database/jdbc" in driver.maven_url


class TestRecommendedDrivers:
    """Test recommended JDBC drivers dictionary."""

    def test_recommended_drivers_exist(self):
        """Test that all expected drivers are defined."""
        expected_databases = {
            "postgresql",
            "mysql",
            "mariadb",
            "mssql",
            "oracle",
            "db2",
            "sqlite",
            "oceanbase",
        }
        assert set(RECOMMENDED_JDBC_DRIVERS.keys()) == expected_databases

    def test_postgresql_driver(self):
        """Test PostgreSQL driver metadata."""
        driver = RECOMMENDED_JDBC_DRIVERS["postgresql"]
        assert driver.group_id == "org.postgresql"
        assert driver.artifact_id == "postgresql"
        assert driver.version == "42.7.1"

    def test_mysql_driver(self):
        """Test MySQL driver metadata."""
        driver = RECOMMENDED_JDBC_DRIVERS["mysql"]
        assert driver.group_id == "com.mysql"
        assert driver.artifact_id == "mysql-connector-j"

    def test_all_drivers_have_valid_metadata(self):
        """Test that all recommended drivers have valid metadata."""
        for db_name, driver in RECOMMENDED_JDBC_DRIVERS.items():
            assert driver.group_id, f"{db_name} missing group_id"
            assert driver.artifact_id, f"{db_name} missing artifact_id"
            assert driver.version, f"{db_name} missing version"
            assert ".jar" in driver.filename


class TestDriverCacheDir:
    """Test driver cache directory management."""

    def test_get_default_cache_dir(self):
        """Test default cache directory location."""
        cache_dir = get_driver_cache_dir()
        assert isinstance(cache_dir, Path)
        assert ".sqlalchemy-jdbcapi" in str(cache_dir)
        assert "drivers" in str(cache_dir)

    def test_get_custom_cache_dir(self):
        """Test custom cache directory from environment."""
        with patch.dict(
            "os.environ", {"SQLALCHEMY_JDBCAPI_DRIVER_CACHE": "/custom/path"}
        ):
            from sqlalchemy_jdbcapi.jdbc.driver_manager import (
                get_driver_cache_dir as get_cache,
            )

            cache_dir = get_cache()
            assert str(cache_dir) == "/custom/path"


class TestDriverVerification:
    """Test driver JAR verification."""

    def test_verify_valid_jar(self):
        """Test verification of valid JAR file."""
        with tempfile.NamedTemporaryFile(suffix=".jar", delete=False) as f:
            f.write(b"PK\x03\x04")  # JAR/ZIP signature
            jar_path = Path(f.name)

        try:
            assert verify_driver(jar_path) is True
        finally:
            jar_path.unlink()

    def test_verify_nonexistent_file(self):
        """Test verification fails for non-existent file."""
        assert verify_driver(Path("/nonexistent/file.jar")) is False

    def test_verify_empty_file(self):
        """Test verification fails for empty file."""
        with tempfile.NamedTemporaryFile(suffix=".jar", delete=False) as f:
            jar_path = Path(f.name)

        try:
            assert verify_driver(jar_path) is False
        finally:
            jar_path.unlink()

    def test_verify_wrong_extension(self):
        """Test verification fails for wrong file extension."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"content")
            txt_path = Path(f.name)

        try:
            assert verify_driver(txt_path) is False
        finally:
            txt_path.unlink()

    def test_verify_directory(self):
        """Test verification fails for directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            assert verify_driver(Path(tmpdir)) is False


class TestDriverDownload:
    """Test driver download functionality."""

    @patch("shutil.copyfileobj")
    @patch("urllib.request.urlopen")
    def test_download_driver_success(self, mock_urlopen, mock_copyfileobj):
        """Test successful driver download."""
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        # Mock file writing
        def copy_side_effect(source, dest):
            dest.write(b"jar_content")

        mock_copyfileobj.side_effect = copy_side_effect

        driver = JDBCDriver(
            group_id="org.postgresql",
            artifact_id="postgresql",
            version="42.7.1",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            path = download_driver(driver, cache_dir=cache_dir)

            assert path.exists()
            assert path.name == "postgresql-42.7.1.jar"
            assert path.parent == cache_dir

    @patch("urllib.request.urlopen")
    def test_download_driver_network_error(self, mock_urlopen):
        """Test download failure due to network error."""
        mock_urlopen.side_effect = Exception("Network error")

        driver = JDBCDriver(
            group_id="org.postgresql",
            artifact_id="postgresql",
            version="42.7.1",
        )

        with (
            tempfile.TemporaryDirectory() as tmpdir,
            pytest.raises(RuntimeError, match="Failed to download"),
        ):
            download_driver(driver, cache_dir=Path(tmpdir))

    @patch("urllib.request.urlopen")
    def test_download_driver_already_exists(self, mock_urlopen):
        """Test skipping download when driver already exists."""
        driver = JDBCDriver(
            group_id="org.postgresql",
            artifact_id="postgresql",
            version="42.7.1",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            jar_path = cache_dir / driver.filename
            jar_path.write_bytes(b"existing_content")

            # Should not call urlopen since file exists
            path = download_driver(driver, cache_dir=cache_dir, force=False)

            assert path == jar_path
            assert path.read_bytes() == b"existing_content"
            mock_urlopen.assert_not_called()

    @patch("shutil.copyfileobj")
    @patch("urllib.request.urlopen")
    def test_download_driver_force_redownload(self, mock_urlopen, mock_copyfileobj):
        """Test force re-download of existing driver."""
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        # Mock file writing
        def copy_side_effect(source, dest):
            dest.write(b"new_content")

        mock_copyfileobj.side_effect = copy_side_effect

        driver = JDBCDriver(
            group_id="org.postgresql",
            artifact_id="postgresql",
            version="42.7.1",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            jar_path = cache_dir / driver.filename
            jar_path.write_bytes(b"old_content")

            path = download_driver(driver, cache_dir=cache_dir, force=True)

            assert path.exists()
            mock_urlopen.assert_called_once()


class TestGetDriverPath:
    """Test getting driver path with auto-download."""

    @patch("sqlalchemy_jdbcapi.jdbc.driver_manager.download_driver")
    def test_get_driver_path_auto_download(self, mock_download):
        """Test auto-download when driver not in cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            expected_path = cache_dir / "postgresql-42.7.1.jar"
            mock_download.return_value = expected_path

            path = get_driver_path(
                "postgresql", auto_download=True, cache_dir=cache_dir
            )

            assert path == expected_path
            mock_download.assert_called_once()

    def test_get_driver_path_no_auto_download_missing(self):
        """Test error when driver missing and auto-download disabled."""
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            pytest.raises(RuntimeError, match="JDBC driver not found"),
        ):
            get_driver_path("postgresql", auto_download=False, cache_dir=Path(tmpdir))

    def test_get_driver_path_invalid_database(self):
        """Test error for unsupported database."""
        with pytest.raises(ValueError, match="No recommended driver"):
            get_driver_path("unsupported_db")

    def test_get_driver_path_existing_driver(self):
        """Test getting path to existing cached driver."""
        driver = RECOMMENDED_JDBC_DRIVERS["postgresql"]

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            jar_path = cache_dir / driver.filename
            jar_path.write_bytes(b"driver_content")

            path = get_driver_path("postgresql", cache_dir=cache_dir)

            assert path == jar_path
            assert path.exists()


class TestGetAllDriverPaths:
    """Test getting multiple driver paths."""

    @patch("sqlalchemy_jdbcapi.jdbc.driver_manager.get_driver_path")
    def test_get_all_drivers_default(self, mock_get_path):
        """Test getting all recommended drivers."""
        mock_get_path.return_value = Path("/fake/driver.jar")

        get_all_driver_paths(auto_download=False)

        # Should attempt to get all 8 recommended drivers
        assert mock_get_path.call_count == 8

    @patch("sqlalchemy_jdbcapi.jdbc.driver_manager.get_driver_path")
    def test_get_specific_drivers(self, mock_get_path):
        """Test getting specific subset of drivers."""
        mock_get_path.return_value = Path("/fake/driver.jar")

        get_all_driver_paths(databases=["postgresql", "mysql"], auto_download=False)

        assert mock_get_path.call_count == 2

    @patch("sqlalchemy_jdbcapi.jdbc.driver_manager.get_driver_path")
    def test_get_all_drivers_handles_errors(self, mock_get_path):
        """Test that errors for individual drivers don't stop others."""

        def side_effect(db, **kwargs):
            if db == "postgresql":
                raise RuntimeError("Download failed")
            return Path(f"/fake/{db}.jar")

        mock_get_path.side_effect = side_effect

        paths = get_all_driver_paths(
            databases=["postgresql", "mysql"], auto_download=False
        )

        # Should return mysql path even though postgresql failed
        assert len(paths) == 1
        assert "mysql" in str(paths[0])


class TestGetClasspathWithDrivers:
    """Test classpath building with mixed sources."""

    @patch("sqlalchemy_jdbcapi.jdbc.driver_manager.get_all_driver_paths")
    def test_classpath_auto_only(self, mock_get_paths):
        """Test classpath from auto-downloaded drivers only."""
        mock_get_paths.return_value = [
            Path("/cache/postgresql.jar"),
            Path("/cache/mysql.jar"),
        ]

        classpath = get_classpath_with_drivers(
            databases=["postgresql", "mysql"], auto_download=True
        )

        assert len(classpath) == 2
        assert Path("/cache/postgresql.jar") in classpath

    def test_classpath_manual_only(self):
        """Test classpath from manual paths only."""
        manual = [Path("/manual/driver1.jar"), Path("/manual/driver2.jar")]

        classpath = get_classpath_with_drivers(
            databases=None, auto_download=False, manual_classpath=manual
        )

        assert classpath == manual

    @patch("sqlalchemy_jdbcapi.jdbc.driver_manager.get_all_driver_paths")
    def test_classpath_manual_priority(self, mock_get_paths):
        """Test that manual paths have priority over auto-downloaded."""
        mock_get_paths.return_value = [Path("/cache/postgresql.jar")]
        manual = [Path("/manual/postgresql.jar")]

        classpath = get_classpath_with_drivers(
            databases=["postgresql"], auto_download=True, manual_classpath=manual
        )

        # Manual should come first
        assert classpath[0] == Path("/manual/postgresql.jar")

    @patch("sqlalchemy_jdbcapi.jdbc.driver_manager.get_all_driver_paths")
    def test_classpath_deduplication(self, mock_get_paths):
        """Test that duplicate paths are removed."""
        shared_path = Path("/shared/driver.jar")
        mock_get_paths.return_value = [shared_path]
        manual = [shared_path, Path("/manual/other.jar")]

        classpath = get_classpath_with_drivers(
            databases=["postgresql"], auto_download=True, manual_classpath=manual
        )

        # Should only appear once
        assert classpath.count(shared_path) == 1
        assert len(classpath) == 2


class TestDriverCacheManagement:
    """Test driver cache listing and clearing."""

    def test_list_cached_drivers_empty(self):
        """Test listing empty cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            drivers = list_cached_drivers(cache_dir=Path(tmpdir))
            assert drivers == []

    def test_list_cached_drivers(self):
        """Test listing cached drivers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            jar1 = cache_dir / "driver1.jar"
            jar2 = cache_dir / "driver2.jar"
            jar1.write_bytes(b"content1")
            jar2.write_bytes(b"content2")

            drivers = list_cached_drivers(cache_dir=cache_dir)

            assert len(drivers) == 2
            assert jar1 in drivers
            assert jar2 in drivers

    def test_list_cached_drivers_filters_invalid(self):
        """Test that invalid files are filtered out."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            valid_jar = cache_dir / "valid.jar"
            valid_jar.write_bytes(b"content")
            empty_jar = cache_dir / "empty.jar"
            empty_jar.touch()
            txt_file = cache_dir / "readme.txt"
            txt_file.write_text("not a jar")

            drivers = list_cached_drivers(cache_dir=cache_dir)

            assert len(drivers) == 1
            assert valid_jar in drivers

    def test_list_cached_drivers_nonexistent_dir(self):
        """Test listing non-existent cache directory."""
        drivers = list_cached_drivers(cache_dir=Path("/nonexistent/path"))
        assert drivers == []

    def test_clear_driver_cache(self):
        """Test clearing driver cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            jar1 = cache_dir / "driver1.jar"
            jar2 = cache_dir / "driver2.jar"
            jar1.write_bytes(b"content1")
            jar2.write_bytes(b"content2")

            count = clear_driver_cache(cache_dir=cache_dir)

            assert count == 2
            assert not jar1.exists()
            assert not jar2.exists()

    def test_clear_driver_cache_empty(self):
        """Test clearing empty cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            count = clear_driver_cache(cache_dir=Path(tmpdir))
            assert count == 0

    def test_clear_driver_cache_nonexistent(self):
        """Test clearing non-existent cache."""
        count = clear_driver_cache(cache_dir=Path("/nonexistent/path"))
        assert count == 0

    def test_clear_driver_cache_only_jars(self):
        """Test that only JAR files are deleted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            jar = cache_dir / "driver.jar"
            txt = cache_dir / "readme.txt"
            jar.write_bytes(b"content")
            txt.write_text("keep me")

            count = clear_driver_cache(cache_dir=cache_dir)

            assert count == 1
            assert not jar.exists()
            assert txt.exists()  # Should not delete non-JAR files


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_jdbc_driver_empty_version(self):
        """Test creating driver with empty version string."""
        driver = JDBCDriver(group_id="org.test", artifact_id="test", version="")
        assert driver.filename == "test-.jar"

    def test_jdbc_driver_special_characters(self):
        """Test driver with special characters in version."""
        driver = JDBCDriver(
            group_id="org.test",
            artifact_id="test",
            version="1.0-SNAPSHOT",
        )
        assert driver.filename == "test-1.0-SNAPSHOT.jar"

    def test_get_driver_path_custom_driver(self):
        """Test using custom driver metadata."""
        custom_driver = JDBCDriver(
            group_id="com.custom",
            artifact_id="custom-driver",
            version="1.0.0",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            jar_path = cache_dir / custom_driver.filename
            jar_path.write_bytes(b"custom_driver")

            path = get_driver_path("custom", driver=custom_driver, cache_dir=cache_dir)

            assert path.exists()
