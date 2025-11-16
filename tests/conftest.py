"""
Pytest configuration and fixtures for sqlalchemy-jdbcapi tests.
"""

from __future__ import annotations

from unittest.mock import MagicMock, Mock

import pytest


@pytest.fixture
def mock_jpype(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """
    Mock JPype module for testing without JVM.

    This fixture allows tests to run without a real JVM installation.
    """
    mock_jpype_module = Mock()
    mock_jpype_module.isJVMStarted.return_value = False
    mock_jpype_module.startJVM = Mock()
    mock_jpype_module.shutdownJVM = Mock()

    # Mock JClass
    def mock_jclass(class_name: str) -> Mock:
        mock_class = Mock()
        mock_class.__name__ = class_name
        return mock_class

    mock_jpype_module.JClass = mock_jclass

    monkeypatch.setattr("jpype.isJVMStarted", mock_jpype_module.isJVMStarted)
    monkeypatch.setattr("jpype.startJVM", mock_jpype_module.startJVM)
    monkeypatch.setattr("jpype.JClass", mock_jpype_module.JClass)

    return mock_jpype_module


@pytest.fixture
def mock_jdbc_connection() -> MagicMock:
    """Mock JDBC connection for testing."""
    conn = MagicMock()
    conn.closed = False
    conn.commit = Mock()
    conn.rollback = Mock()
    conn.close = Mock()
    conn.createStatement = Mock()
    conn.prepareStatement = Mock()
    return conn


@pytest.fixture
def mock_jdbc_cursor() -> MagicMock:
    """Mock JDBC cursor for testing."""
    cursor = MagicMock()
    cursor.execute = Mock(return_value=True)
    cursor.fetchone = Mock(return_value=None)
    cursor.fetchall = Mock(return_value=[])
    cursor.fetchmany = Mock(return_value=[])
    cursor.close = Mock()
    return cursor


@pytest.fixture
def sample_query() -> str:
    """Sample SQL query for testing."""
    return "SELECT id, name, email FROM users WHERE active = ?"


@pytest.fixture
def sample_query_params() -> tuple[bool]:
    """Sample query parameters for testing."""
    return (True,)
