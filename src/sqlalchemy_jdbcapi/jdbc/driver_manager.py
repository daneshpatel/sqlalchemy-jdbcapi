"""
JDBC driver auto-download and management.

This module handles automatic downloading of JDBC drivers from Maven Central
and provides fallback to manual driver configuration via CLASSPATH.
"""

from __future__ import annotations

import logging
import os
import shutil
import urllib.request
from pathlib import Path
from typing import NamedTuple

logger = logging.getLogger(__name__)

# Default driver cache directory
DEFAULT_DRIVER_CACHE = Path.home() / ".sqlalchemy-jdbcapi" / "drivers"


class JDBCDriver(NamedTuple):
    """JDBC driver metadata for automatic download."""

    group_id: str
    artifact_id: str
    version: str
    classifier: str | None = None

    @property
    def filename(self) -> str:
        """Get the JAR filename."""
        if self.classifier:
            return f"{self.artifact_id}-{self.version}-{self.classifier}.jar"
        return f"{self.artifact_id}-{self.version}.jar"

    @property
    def maven_url(self) -> str:
        """Get the Maven Central download URL."""
        base_url = "https://repo1.maven.org/maven2"
        group_path = self.group_id.replace(".", "/")
        return (
            f"{base_url}/{group_path}/{self.artifact_id}/{self.version}/{self.filename}"
        )


# Recommended JDBC drivers for auto-download from Maven Central
# These versions are tested and known to work well
# TODO: Consider checking for newer versions periodically
RECOMMENDED_JDBC_DRIVERS = {
    "postgresql": JDBCDriver(
        group_id="org.postgresql",
        artifact_id="postgresql",
        version="42.7.1",  # Latest stable as of 2024
    ),
    "mysql": JDBCDriver(
        group_id="com.mysql",
        artifact_id="mysql-connector-j",
        version="8.3.0",  # Note: Oracle renamed this from mysql-connector-java
    ),
    "mariadb": JDBCDriver(
        group_id="org.mariadb.jdbc",
        artifact_id="mariadb-java-client",
        version="3.3.2",
    ),
    "mssql": JDBCDriver(
        group_id="com.microsoft.sqlserver",
        artifact_id="mssql-jdbc",
        version="12.6.0.jre11",  # JRE11 version for Java 11+ compatibility
    ),
    "oracle": JDBCDriver(
        group_id="com.oracle.database.jdbc",
        artifact_id="ojdbc11",
        version="23.3.0.23.09",
    ),
    "db2": JDBCDriver(
        group_id="com.ibm.db2",
        artifact_id="jcc",
        version="11.5.9.0",
    ),
    "sqlite": JDBCDriver(
        group_id="org.xerial",
        artifact_id="sqlite-jdbc",
        version="3.45.0.0",
    ),
    "oceanbase": JDBCDriver(
        group_id="com.oceanbase",
        artifact_id="oceanbase-client",
        version="2.4.9",
    ),
}


def get_driver_cache_dir() -> Path:
    """
    Get the driver cache directory.

    Returns:
        Path to the driver cache directory.
    """
    cache_dir = os.environ.get("SQLALCHEMY_JDBCAPI_DRIVER_CACHE")
    if cache_dir:
        return Path(cache_dir)
    return DEFAULT_DRIVER_CACHE


def download_driver(
    driver: JDBCDriver,
    cache_dir: Path | None = None,
    force: bool = False,
) -> Path:
    """
    Download a JDBC driver from Maven Central.

    Args:
        driver: JDBC driver metadata.
        cache_dir: Directory to cache downloaded drivers. If None, uses default.
        force: Force re-download even if driver exists.

    Returns:
        Path to the downloaded driver JAR file.

    Raises:
        RuntimeError: If download fails.
    """
    if cache_dir is None:
        cache_dir = get_driver_cache_dir()

    # Create cache directory if it doesn't exist
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Target file path
    target_path = cache_dir / driver.filename

    # Check if driver already exists
    if target_path.exists() and not force:
        logger.debug(f"Driver already cached: {target_path}")
        return target_path

    # Download driver
    logger.info(f"Downloading JDBC driver: {driver.filename}")
    logger.debug(f"URL: {driver.maven_url}")

    try:
        with urllib.request.urlopen(driver.maven_url) as response:
            # Download to temporary file first
            temp_path = target_path.with_suffix(".tmp")
            with open(temp_path, "wb") as f:
                shutil.copyfileobj(response, f)

            # Move to final location
            temp_path.replace(target_path)

        logger.info(f"Driver downloaded successfully: {target_path}")
        return target_path

    except Exception as e:
        error_msg = f"Failed to download driver from {driver.maven_url}: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_driver_path(
    database: str,
    driver: JDBCDriver | None = None,
    auto_download: bool = True,
    cache_dir: Path | None = None,
) -> Path:
    """
    Get the path to a JDBC driver, downloading if necessary.

    Args:
        database: Database name (e.g., 'postgresql', 'mysql').
        driver: Custom driver metadata. If None, uses recommended driver.
        auto_download: Whether to auto-download driver if not found.
        cache_dir: Directory to cache downloaded drivers.

    Returns:
        Path to the JDBC driver JAR file.

    Raises:
        RuntimeError: If driver not found and auto-download disabled.
    """
    if driver is None:
        driver = RECOMMENDED_JDBC_DRIVERS.get(database.lower())
        if driver is None:
            raise ValueError(f"No recommended driver for database: {database}")

    if cache_dir is None:
        cache_dir = get_driver_cache_dir()

    target_path = cache_dir / driver.filename

    # Check if driver exists in cache
    if target_path.exists():
        return target_path

    # Try to auto-download
    if auto_download:
        return download_driver(driver, cache_dir)

    raise RuntimeError(
        f"JDBC driver not found: {target_path}. "
        f"Enable auto_download or set CLASSPATH environment variable."
    )


def get_all_driver_paths(
    databases: list[str] | None = None,
    auto_download: bool = True,
    cache_dir: Path | None = None,
) -> list[Path]:
    """
    Get paths to multiple JDBC drivers.

    Args:
        databases: List of database names. If None, downloads all recommended drivers.
        auto_download: Whether to auto-download drivers if not found.
        cache_dir: Directory to cache downloaded drivers.

    Returns:
        List of paths to JDBC driver JAR files.
    """
    if databases is None:
        databases = list(RECOMMENDED_JDBC_DRIVERS.keys())

    paths = []
    for database in databases:
        try:
            path = get_driver_path(
                database, auto_download=auto_download, cache_dir=cache_dir
            )
            paths.append(path)
        except Exception as e:
            logger.warning(f"Failed to get driver for {database}: {e}")

    return paths


def get_classpath_with_drivers(
    databases: list[str] | None = None,
    auto_download: bool = True,
    manual_classpath: list[Path] | None = None,
) -> list[Path]:
    """
    Get comprehensive classpath including auto-downloaded and manual drivers.

    Args:
        databases: List of database names for auto-download. If None, downloads all recommended.
        auto_download: Whether to auto-download drivers.
        manual_classpath: Additional manual classpath entries.

    Returns:
        List of all classpath entries.
    """
    classpath = []

    # Add manual classpath entries first (higher priority)
    if manual_classpath:
        classpath.extend(manual_classpath)

    # Add auto-downloaded drivers
    if auto_download:
        try:
            auto_paths = get_all_driver_paths(databases, auto_download=True)
            classpath.extend(auto_paths)
        except Exception as e:
            logger.warning(f"Failed to auto-download some drivers: {e}")

    # Remove duplicates while preserving order
    seen = set()
    unique_classpath = []
    for path in classpath:
        if path not in seen:
            seen.add(path)
            unique_classpath.append(path)

    return unique_classpath


def verify_driver(driver_path: Path) -> bool:
    """
    Verify that a JDBC driver JAR file is valid.

    Args:
        driver_path: Path to the driver JAR file.

    Returns:
        True if driver appears valid, False otherwise.
    """
    if not driver_path.exists():
        return False

    if not driver_path.is_file():
        return False

    if not driver_path.suffix == ".jar":
        return False

    # Check if file is not empty
    if driver_path.stat().st_size == 0:
        return False

    # Could add more validation (e.g., ZIP file structure)
    return True


def list_cached_drivers(cache_dir: Path | None = None) -> list[Path]:
    """
    List all cached JDBC drivers.

    Args:
        cache_dir: Directory to check. If None, uses default.

    Returns:
        List of paths to cached driver JAR files.
    """
    if cache_dir is None:
        cache_dir = get_driver_cache_dir()

    if not cache_dir.exists():
        return []

    return [path for path in cache_dir.glob("*.jar") if verify_driver(path)]


def clear_driver_cache(cache_dir: Path | None = None) -> int:
    """
    Clear the driver cache directory.

    Args:
        cache_dir: Directory to clear. If None, uses default.

    Returns:
        Number of files deleted.
    """
    if cache_dir is None:
        cache_dir = get_driver_cache_dir()

    if not cache_dir.exists():
        return 0

    count = 0
    for path in cache_dir.glob("*.jar"):
        try:
            path.unlink()
            count += 1
            logger.debug(f"Deleted cached driver: {path}")
        except Exception as e:
            logger.warning(f"Failed to delete {path}: {e}")

    return count
