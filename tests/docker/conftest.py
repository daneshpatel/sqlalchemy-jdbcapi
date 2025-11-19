"""
Pytest configuration for Docker-based functional tests.

These tests require running database containers via docker-compose.
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_connection_url(dialect: str, driver: str = "jdbcapi") -> str:
    """
    Get connection URL for a specific database from environment variables.

    Args:
        dialect: Database dialect (postgresql, mysql, mariadb, mssql)
        driver: Driver name (jdbcapi)

    Returns:
        SQLAlchemy connection URL
    """
    dialect_upper = dialect.upper()

    host = os.environ.get(f"{dialect_upper}_HOST", "localhost")
    port = os.environ.get(f"{dialect_upper}_PORT", "5432")
    user = os.environ.get(f"{dialect_upper}_USER", "testuser")
    password = os.environ.get(f"{dialect_upper}_PASSWORD", "testpass")
    database = os.environ.get(f"{dialect_upper}_DB", "testdb")

    # Handle special cases for port mapping
    port_map = {
        "postgresql": "5432",
        "mysql": "3306",
        "mariadb": "3307",  # Mapped to different host port
        "mssql": "1433",
    }

    if dialect in port_map:
        default_port = port_map[dialect]
        port = os.environ.get(f"{dialect_upper}_PORT", default_port)

    return f"{driver}+{dialect}://{user}:{password}@{host}:{port}/{database}"


@pytest.fixture(scope="session")
def postgres_engine():
    """Create PostgreSQL engine for testing."""
    url = get_connection_url("postgresql")
    engine = create_engine(url, echo=False)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def mysql_engine():
    """Create MySQL engine for testing."""
    url = get_connection_url("mysql")
    engine = create_engine(url, echo=False)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def mariadb_engine():
    """Create MariaDB engine for testing."""
    url = get_connection_url("mariadb")
    # MariaDB uses the mysql dialect
    url = url.replace("+mariadb", "+mysql")
    engine = create_engine(url, echo=False)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def mssql_engine():
    """Create SQL Server engine for testing."""
    url = get_connection_url("mssql")
    engine = create_engine(url, echo=False)
    yield engine
    engine.dispose()


@pytest.fixture
def postgres_session(postgres_engine):
    """Create PostgreSQL session for testing."""
    Session = sessionmaker(bind=postgres_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def mysql_session(mysql_engine):
    """Create MySQL session for testing."""
    Session = sessionmaker(bind=mysql_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def mariadb_session(mariadb_engine):
    """Create MariaDB session for testing."""
    Session = sessionmaker(bind=mariadb_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def mssql_session(mssql_engine):
    """Create SQL Server session for testing."""
    Session = sessionmaker(bind=mssql_engine)
    session = Session()
    yield session
    session.close()
