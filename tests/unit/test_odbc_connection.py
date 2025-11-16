"""
Tests for ODBC connection and exception handling.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from sqlalchemy_jdbcapi.odbc.connection import Connection, connect
from sqlalchemy_jdbcapi.odbc.exceptions import (
    DatabaseError,
    DataError,
    Error,
    IntegrityError,
    InterfaceError,
    InternalError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    Warning,
)


class TestODBCExceptions:
    """Test ODBC exception hierarchy."""

    def test_exception_hierarchy(self):
        """Test that exceptions follow DB-API 2.0 hierarchy."""
        # All should inherit from Error
        assert issubclass(Warning, Exception)
        assert issubclass(InterfaceError, Error)
        assert issubclass(DatabaseError, Error)
        assert issubclass(OperationalError, DatabaseError)
        assert issubclass(IntegrityError, DatabaseError)
        assert issubclass(InternalError, DatabaseError)
        assert issubclass(ProgrammingError, DatabaseError)
        assert issubclass(NotSupportedError, DatabaseError)
        assert issubclass(DataError, DatabaseError)

    def test_create_exceptions(self):
        """Test creating and raising exceptions."""
        with pytest.raises(InterfaceError):
            raise InterfaceError("Test interface error")

        with pytest.raises(DatabaseError):
            raise DatabaseError("Test database error")

        with pytest.raises(OperationalError):
            raise OperationalError("Test operational error")


class TestODBCConnection:
    """Test ODBC Connection wrapper."""

    def test_connection_creation(self):
        """Test creating connection wrapper."""
        mock_pyodbc_conn = Mock()
        conn = Connection(mock_pyodbc_conn)

        assert conn._connection is mock_pyodbc_conn
        assert conn._closed is False

    def test_cursor_creation(self):
        """Test creating cursor from connection."""
        mock_pyodbc_conn = Mock()
        mock_cursor = Mock()
        mock_pyodbc_conn.cursor.return_value = mock_cursor

        conn = Connection(mock_pyodbc_conn)
        cursor = conn.cursor()

        assert cursor is mock_cursor
        mock_pyodbc_conn.cursor.assert_called_once()

    def test_cursor_on_closed_connection(self):
        """Test error when creating cursor on closed connection."""
        mock_pyodbc_conn = Mock()
        conn = Connection(mock_pyodbc_conn)
        conn._closed = True

        with pytest.raises(InterfaceError, match="Connection is closed"):
            conn.cursor()

    def test_commit(self):
        """Test committing transaction."""
        mock_pyodbc_conn = Mock()
        conn = Connection(mock_pyodbc_conn)

        conn.commit()

        mock_pyodbc_conn.commit.assert_called_once()

    def test_commit_on_closed_connection(self):
        """Test error when committing closed connection."""
        mock_pyodbc_conn = Mock()
        conn = Connection(mock_pyodbc_conn)
        conn._closed = True

        with pytest.raises(InterfaceError, match="Connection is closed"):
            conn.commit()

    def test_commit_failure(self):
        """Test handling commit failure."""
        mock_pyodbc_conn = Mock()
        mock_pyodbc_conn.commit.side_effect = Exception("Commit failed")

        conn = Connection(mock_pyodbc_conn)

        with pytest.raises(DatabaseError, match="Failed to commit"):
            conn.commit()

    def test_rollback(self):
        """Test rolling back transaction."""
        mock_pyodbc_conn = Mock()
        conn = Connection(mock_pyodbc_conn)

        conn.rollback()

        mock_pyodbc_conn.rollback.assert_called_once()

    def test_rollback_on_closed_connection(self):
        """Test error when rolling back closed connection."""
        mock_pyodbc_conn = Mock()
        conn = Connection(mock_pyodbc_conn)
        conn._closed = True

        with pytest.raises(InterfaceError, match="Connection is closed"):
            conn.rollback()

    def test_rollback_failure(self):
        """Test handling rollback failure."""
        mock_pyodbc_conn = Mock()
        mock_pyodbc_conn.rollback.side_effect = Exception("Rollback failed")

        conn = Connection(mock_pyodbc_conn)

        with pytest.raises(DatabaseError, match="Failed to rollback"):
            conn.rollback()

    def test_close(self):
        """Test closing connection."""
        mock_pyodbc_conn = Mock()
        conn = Connection(mock_pyodbc_conn)

        conn.close()

        assert conn._closed is True
        mock_pyodbc_conn.close.assert_called_once()

    def test_close_idempotent(self):
        """Test that closing twice doesn't error."""
        mock_pyodbc_conn = Mock()
        conn = Connection(mock_pyodbc_conn)

        conn.close()
        conn.close()

        # Should only close once
        mock_pyodbc_conn.close.assert_called_once()

    def test_context_manager_success(self):
        """Test using connection as context manager (success)."""
        mock_pyodbc_conn = Mock()
        conn = Connection(mock_pyodbc_conn)

        with conn as c:
            assert c is conn

        # Should commit and close on successful exit
        mock_pyodbc_conn.commit.assert_called_once()
        mock_pyodbc_conn.close.assert_called_once()

    def test_context_manager_exception(self):
        """Test using connection as context manager (exception)."""
        mock_pyodbc_conn = Mock()
        conn = Connection(mock_pyodbc_conn)

        with pytest.raises(ValueError, match="Test error"), conn:
            raise ValueError("Test error")

        # Should rollback and close on exception
        mock_pyodbc_conn.rollback.assert_called_once()
        mock_pyodbc_conn.commit.assert_not_called()
        mock_pyodbc_conn.close.assert_called_once()

    def test_closed_property(self):
        """Test closed property."""
        mock_pyodbc_conn = Mock()
        conn = Connection(mock_pyodbc_conn)

        assert conn.closed is False

        conn.close()

        assert conn.closed is True


class TestODBCConnect:
    """Test ODBC connect function."""

    @patch("builtins.__import__")
    def test_connect_success(self, mock_import):
        """Test successful connection."""
        mock_pyodbc = Mock()
        mock_conn = Mock()
        mock_pyodbc.connect.return_value = mock_conn
        mock_import.return_value = mock_pyodbc

        conn = connect("DSN=TestDB;UID=user;PWD=pass")

        assert isinstance(conn, Connection)
        assert conn._connection is mock_conn

    @patch("builtins.__import__")
    def test_connect_with_autocommit(self, mock_import):
        """Test connection with autocommit enabled."""
        mock_pyodbc = Mock()
        mock_conn = Mock()
        mock_pyodbc.connect.return_value = mock_conn
        mock_import.return_value = mock_pyodbc

        connect("DSN=TestDB", autocommit=True)

        call_kwargs = mock_pyodbc.connect.call_args[1]
        assert call_kwargs.get("autocommit") is True

    @patch("builtins.__import__")
    def test_connect_with_timeout(self, mock_import):
        """Test connection with timeout."""
        mock_pyodbc = Mock()
        mock_conn = Mock()
        mock_pyodbc.connect.return_value = mock_conn
        mock_import.return_value = mock_pyodbc

        connect("DSN=TestDB", timeout=30)

        call_kwargs = mock_pyodbc.connect.call_args[1]
        assert call_kwargs.get("timeout") == 30

    @patch("builtins.__import__")
    def test_connect_with_kwargs(self, mock_import):
        """Test connection with additional kwargs."""
        mock_pyodbc = Mock()
        mock_conn = Mock()
        mock_pyodbc.connect.return_value = mock_conn
        mock_import.return_value = mock_pyodbc

        connect("DSN=TestDB", ansi=True, unicode_results=True)

        call_kwargs = mock_pyodbc.connect.call_args[1]
        assert call_kwargs.get("ansi") is True
        assert call_kwargs.get("unicode_results") is True

    @patch("builtins.__import__")
    def test_connect_pyodbc_not_installed(self, mock_import):
        """Test error when pyodbc not installed."""
        mock_import.side_effect = ImportError("No module named 'pyodbc'")

        with pytest.raises(InterfaceError, match="pyodbc is not installed"):
            connect("DSN=TestDB")

    @patch("builtins.__import__")
    def test_connect_failure(self, mock_import):
        """Test handling connection failure."""
        mock_pyodbc = Mock()
        mock_pyodbc.Error = Exception
        mock_pyodbc.connect.side_effect = Exception("Connection failed")
        mock_import.return_value = mock_pyodbc

        with pytest.raises(DatabaseError, match="Failed to connect"):
            connect("DSN=TestDB")


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_connection_with_none(self):
        """Test creating connection with None."""
        conn = Connection(None)
        assert conn._connection is None

    def test_multiple_commits(self):
        """Test multiple commits in succession."""
        mock_pyodbc_conn = Mock()
        conn = Connection(mock_pyodbc_conn)

        conn.commit()
        conn.commit()
        conn.commit()

        assert mock_pyodbc_conn.commit.call_count == 3

    def test_multiple_rollbacks(self):
        """Test multiple rollbacks in succession."""
        mock_pyodbc_conn = Mock()
        conn = Connection(mock_pyodbc_conn)

        conn.rollback()
        conn.rollback()
        conn.rollback()

        assert mock_pyodbc_conn.rollback.call_count == 3

    def test_operations_after_close(self):
        """Test that operations fail after closing."""
        mock_pyodbc_conn = Mock()
        conn = Connection(mock_pyodbc_conn)
        conn.close()

        with pytest.raises(InterfaceError):
            conn.cursor()

        with pytest.raises(InterfaceError):
            conn.commit()

        with pytest.raises(InterfaceError):
            conn.rollback()

    @patch("builtins.__import__")
    def test_connect_empty_connection_string(self, mock_import):
        """Test connecting with empty connection string."""
        mock_pyodbc = Mock()
        mock_conn = Mock()
        mock_pyodbc.connect.return_value = mock_conn
        mock_import.return_value = mock_pyodbc

        conn = connect("")

        assert isinstance(conn, Connection)

    def test_connection_repr(self):
        """Test connection string representation."""
        mock_pyodbc_conn = Mock()
        conn = Connection(mock_pyodbc_conn)

        # Should not raise
        repr(conn)
        assert "Connection" in str(type(conn))

    def test_nested_context_managers(self):
        """Test nested context manager usage."""
        mock_pyodbc_conn = Mock()

        with Connection(mock_pyodbc_conn), Connection(mock_pyodbc_conn):
            pass

        # Both should commit and close
        assert mock_pyodbc_conn.commit.call_count >= 2

    @patch("builtins.__import__")
    def test_connect_special_characters_in_password(self, mock_import):
        """Test connection string with special characters in password."""
        mock_pyodbc = Mock()
        mock_conn = Mock()
        mock_pyodbc.connect.return_value = mock_conn
        mock_import.return_value = mock_pyodbc

        # Should not raise
        conn = connect("DSN=TestDB;PWD=p@ss{w}ord;with=special")

        assert isinstance(conn, Connection)

    def test_commit_during_rollback_failure(self):
        """Test behavior when both commit and rollback fail."""
        mock_pyodbc_conn = Mock()
        mock_pyodbc_conn.commit.side_effect = Exception("Commit failed")
        mock_pyodbc_conn.rollback.side_effect = Exception("Rollback failed")

        conn = Connection(mock_pyodbc_conn)

        with pytest.raises(DatabaseError, match="Failed to commit"):
            conn.commit()

        with pytest.raises(DatabaseError, match="Failed to rollback"):
            conn.rollback()
