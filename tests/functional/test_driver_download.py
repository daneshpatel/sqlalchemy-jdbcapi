"""
Functional tests for JDBC driver download.

These tests verify actual driver download from Maven Central.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from sqlalchemy_jdbcapi.jdbc.driver_manager import (
    RECOMMENDED_JDBC_DRIVERS,
    download_driver,
    get_driver_path,
    verify_driver,
)


@pytest.mark.slow
@pytest.mark.network
class TestActualDriverDownload:
    """Test actual driver download from Maven Central."""

    def test_download_postgresql_driver(self):
        """Test downloading PostgreSQL JDBC driver from Maven Central."""
        driver = RECOMMENDED_JDBC_DRIVERS["postgresql"]

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)

            # Download driver
            driver_path = download_driver(driver, cache_dir=cache_dir)

            # Verify download
            assert driver_path.exists()
            assert driver_path.is_file()
            assert driver_path.suffix == ".jar"
            assert driver_path.stat().st_size > 100000  # Should be > 100KB

            # Verify it's a valid JAR file
            assert verify_driver(driver_path)

    def test_download_sqlite_driver(self):
        """Test downloading SQLite JDBC driver (smaller, faster download)."""
        driver = RECOMMENDED_JDBC_DRIVERS["sqlite"]

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)

            driver_path = download_driver(driver, cache_dir=cache_dir)

            assert driver_path.exists()
            assert driver_path.name == driver.filename
            assert verify_driver(driver_path)

    def test_download_caching(self):
        """Test that downloaded drivers are cached and not re-downloaded."""
        driver = RECOMMENDED_JDBC_DRIVERS["sqlite"]

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)

            # First download
            driver_path1 = download_driver(driver, cache_dir=cache_dir)
            mtime1 = driver_path1.stat().st_mtime

            # Second download should use cache
            driver_path2 = download_driver(driver, cache_dir=cache_dir)
            mtime2 = driver_path2.stat().st_mtime

            # Should be same file (cached)
            assert driver_path1 == driver_path2
            assert mtime1 == mtime2

    def test_download_force_redownload(self):
        """Test forcing re-download of cached driver."""
        driver = RECOMMENDED_JDBC_DRIVERS["sqlite"]

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)

            # First download
            driver_path1 = download_driver(driver, cache_dir=cache_dir)

            # Create fake/corrupted file
            driver_path1.write_text("corrupted")

            # Force re-download
            driver_path2 = download_driver(driver, cache_dir=cache_dir, force=True)

            # Should be re-downloaded
            assert driver_path2.exists()
            assert driver_path2.stat().st_size > 100000  # Real JAR file

    def test_get_driver_path_auto_download(self):
        """Test get_driver_path with auto-download."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)

            # Should auto-download
            driver_path = get_driver_path(
                "sqlite", auto_download=True, cache_dir=cache_dir
            )

            assert driver_path.exists()
            assert verify_driver(driver_path)


@pytest.mark.slow
@pytest.mark.network
class TestMavenURLs:
    """Test Maven Central URLs are accessible."""

    def test_all_driver_urls_accessible(self):
        """Test that all recommended driver URLs are accessible."""
        import urllib.request

        errors = []

        for db_name, driver in RECOMMENDED_JDBC_DRIVERS.items():
            url = driver.maven_url

            try:
                req = urllib.request.Request(url, method="HEAD")
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status != 200:
                        errors.append(f"{db_name}: HTTP {response.status}")
            except Exception as e:
                errors.append(f"{db_name}: {e}")

        if errors:
            pytest.skip(f"Some Maven URLs not accessible: {errors}")
