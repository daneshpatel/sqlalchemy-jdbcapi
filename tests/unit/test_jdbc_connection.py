"""
Comprehensive tests for JDBC connection module.

Tests the JDBC connection wrapper and DB-API 2.0 compliance.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from sqlalchemy_jdbcapi.jdbc.connection import Connection, connect
from sqlalchemy_jdbcapi.jdbc.exceptions import DatabaseError, InterfaceError


class TestJDBCConnection:
    """Test JDBC Connection class."""

    @patch("sqlalchemy_jdbcapi.jdbc.connection.start_jvm")
    @patch("jpype.JClass")
    def test_connection_creation_basic(self, mock_jclass, mock_start_jvm):
        """Test basic JDBC connection creation."""
        # Setup mocks
        mock_driver = Mock()
        mock_driver_manager = Mock()
        mock_jdbc_conn = Mock()

        def jclass_side_effect(name):
            if "Driver" in name and "Manager" not in name:
                return mock_driver
            if "DriverManager" in name:
                return mock_driver_manager
            return Mock()

        mock_jclass.side_effect = jclass_side_effect
        mock_driver_manager.getConnection.return_value = mock_jdbc_conn

        # Create connection
        conn = Connection(
            jclassname="org.postgresql.Driver",
            url="jdbc:postgresql://localhost:5432/testdb",
            driver_args=None,
        )

        # Verify connection created
        assert conn is not None

        # Verify JVM started
        mock_start_jvm.assert_called_once()

        # Verify driver loaded
        assert mock_jclass.called

        # Verify connection created
        mock_driver_manager.getConnection.assert_called_once()

    @patch("sqlalchemy_jdbcapi.jdbc.connection.start_jvm")
    @patch("jpype.JClass")
    def test_connection_with_dict_args(self, mock_jclass, mock_start_jvm):
        """Test connection with dictionary driver args."""
        mock_driver = Mock()
        mock_driver_manager = Mock()
        mock_jdbc_conn = Mock()
        mock_properties = Mock()

        def jclass_side_effect(name):
            if "Properties" in name:
                return lambda: mock_properties
            if "Driver" in name and "Manager" not in name:
                return mock_driver
            if "DriverManager" in name:
                return mock_driver_manager
            return Mock()

        mock_jclass.side_effect = jclass_side_effect
        mock_driver_manager.getConnection.return_value = mock_jdbc_conn

        # Create connection with dict args
        conn = Connection(
            jclassname="org.postgresql.Driver",
            url="jdbc:postgresql://localhost:5432/testdb",
            driver_args={"user": "testuser", "password": "testpass"},
        )

        # Verify connection created
        assert conn is not None
        # Verify properties were set
        assert mock_properties.setProperty.called

    @patch("sqlalchemy_jdbcapi.jdbc.connection.start_jvm")
    @patch("jpype.JClass")
    def test_connection_with_list_args(self, mock_jclass, mock_start_jvm):
        """Test connection with list driver args (user, password)."""
        mock_driver = Mock()
        mock_driver_manager = Mock()
        mock_jdbc_conn = Mock()

        def jclass_side_effect(name):
            if "Driver" in name and "Manager" not in name:
                return mock_driver
            if "DriverManager" in name:
                return mock_driver_manager
            return Mock()

        mock_jclass.side_effect = jclass_side_effect
        mock_driver_manager.getConnection.return_value = mock_jdbc_conn

        # Create connection with list args
        conn = Connection(
            jclassname="org.postgresql.Driver",
            url="jdbc:postgresql://localhost:5432/testdb",
            driver_args=["testuser", "testpass"],
        )

        # Verify connection created
        assert conn is not None
        # Verify connection called with user/pass
        call_args = mock_driver_manager.getConnection.call_args
        assert len(call_args[0]) == 3  # url, user, password

    @patch("sqlalchemy_jdbcapi.jdbc.connection.start_jvm")
    @patch("jpype.JClass")
    def test_connection_invalid_driver_args(self, mock_jclass, mock_start_jvm):
        """Test connection with invalid driver args raises error."""
        # ValueError is wrapped in DatabaseError by the connection class
        with pytest.raises(DatabaseError, match="Failed to connect"):
            Connection(
                jclassname="org.postgresql.Driver",
                url="jdbc:postgresql://localhost:5432/testdb",
                driver_args="invalid",  # Should be dict, list, or None
            )

    @patch("sqlalchemy_jdbcapi.jdbc.connection.start_jvm")
    def test_connection_jvm_start_failure(self, mock_start_jvm):
        """Test handling of JVM start failure."""
        mock_start_jvm.side_effect = Exception("JVM start failed")

        with pytest.raises(InterfaceError, match="Failed to start JVM"):
            Connection(
                jclassname="org.postgresql.Driver",
                url="jdbc:postgresql://localhost:5432/testdb",
            )

    @patch("sqlalchemy_jdbcapi.jdbc.connection.start_jvm")
    @patch("jpype.JClass")
    def test_connection_database_error(self, mock_jclass, mock_start_jvm):
        """Test handling of database connection errors."""
        mock_driver_manager = Mock()
        mock_driver_manager.getConnection.side_effect = Exception("Connection refused")

        def jclass_side_effect(name):
            if "DriverManager" in name:
                return mock_driver_manager
            return Mock()

        mock_jclass.side_effect = jclass_side_effect

        with pytest.raises(DatabaseError, match="Failed to connect"):
            Connection(
                jclassname="org.postgresql.Driver",
                url="jdbc:postgresql://localhost:5432/testdb",
            )

    @patch("sqlalchemy_jdbcapi.jdbc.connection.start_jvm")
    @patch("jpype.JClass")
    def test_connection_close(self, mock_jclass, mock_start_jvm):
        """Test closing JDBC connection."""
        mock_jdbc_conn = Mock()
        mock_driver_manager = Mock()
        mock_driver_manager.getConnection.return_value = mock_jdbc_conn

        def jclass_side_effect(name):
            if "DriverManager" in name:
                return mock_driver_manager
            return Mock()

        mock_jclass.side_effect = jclass_side_effect

        conn = Connection(
            jclassname="org.postgresql.Driver",
            url="jdbc:postgresql://localhost:5432/testdb",
        )

        conn.close()

        # Verify JDBC connection closed
        mock_jdbc_conn.close.assert_called_once()
        assert conn.closed

    @patch("sqlalchemy_jdbcapi.jdbc.connection.start_jvm")
    @patch("jpype.JClass")
    def test_connection_close_idempotent(self, mock_jclass, mock_start_jvm):
        """Test that closing connection multiple times is safe."""
        mock_jdbc_conn = Mock()
        mock_driver_manager = Mock()
        mock_driver_manager.getConnection.return_value = mock_jdbc_conn

        def jclass_side_effect(name):
            if "DriverManager" in name:
                return mock_driver_manager
            return Mock()

        mock_jclass.side_effect = jclass_side_effect

        conn = Connection(
            jclassname="org.postgresql.Driver",
            url="jdbc:postgresql://localhost:5432/testdb",
        )

        conn.close()
        conn.close()  # Should not raise

        # Close should only be called once on JDBC connection
        assert mock_jdbc_conn.close.call_count == 1

    @patch("sqlalchemy_jdbcapi.jdbc.connection.start_jvm")
    @patch("jpype.JClass")
    def test_connection_commit(self, mock_jclass, mock_start_jvm):
        """Test committing transaction."""
        mock_jdbc_conn = Mock()
        mock_driver_manager = Mock()
        mock_driver_manager.getConnection.return_value = mock_jdbc_conn

        def jclass_side_effect(name):
            if "DriverManager" in name:
                return mock_driver_manager
            return Mock()

        mock_jclass.side_effect = jclass_side_effect

        conn = Connection(
            jclassname="org.postgresql.Driver",
            url="jdbc:postgresql://localhost:5432/testdb",
        )

        conn.commit()

        mock_jdbc_conn.commit.assert_called_once()

    @patch("sqlalchemy_jdbcapi.jdbc.connection.start_jvm")
    @patch("jpype.JClass")
    def test_connection_rollback(self, mock_jclass, mock_start_jvm):
        """Test rolling back transaction."""
        mock_jdbc_conn = Mock()
        mock_driver_manager = Mock()
        mock_driver_manager.getConnection.return_value = mock_jdbc_conn

        def jclass_side_effect(name):
            if "DriverManager" in name:
                return mock_driver_manager
            return Mock()

        mock_jclass.side_effect = jclass_side_effect

        conn = Connection(
            jclassname="org.postgresql.Driver",
            url="jdbc:postgresql://localhost:5432/testdb",
        )

        conn.rollback()

        mock_jdbc_conn.rollback.assert_called_once()

    @patch("sqlalchemy_jdbcapi.jdbc.connection.start_jvm")
    @patch("jpype.JClass")
    def test_connection_operations_on_closed(self, mock_jclass, mock_start_jvm):
        """Test that operations on closed connection raise errors."""
        mock_jdbc_conn = Mock()
        mock_driver_manager = Mock()
        mock_driver_manager.getConnection.return_value = mock_jdbc_conn

        def jclass_side_effect(name):
            if "DriverManager" in name:
                return mock_driver_manager
            return Mock()

        mock_jclass.side_effect = jclass_side_effect

        conn = Connection(
            jclassname="org.postgresql.Driver",
            url="jdbc:postgresql://localhost:5432/testdb",
        )

        conn.close()

        with pytest.raises(InterfaceError, match="Connection is closed"):
            conn.commit()

        with pytest.raises(InterfaceError, match="Connection is closed"):
            conn.rollback()

        with pytest.raises(InterfaceError, match="Connection is closed"):
            conn.cursor()


class TestConnectFunction:
    """Test the connect() convenience function."""

    @patch("sqlalchemy_jdbcapi.jdbc.connection.Connection")
    def test_connect_basic(self, mock_connection_class):
        """Test basic connect() function."""
        mock_conn = Mock()
        mock_connection_class.return_value = mock_conn

        result = connect(
            jclassname="org.postgresql.Driver",
            url="jdbc:postgresql://localhost:5432/testdb",
        )

        assert result == mock_conn
        mock_connection_class.assert_called_once()

    @patch("sqlalchemy_jdbcapi.jdbc.connection.Connection")
    def test_connect_with_args(self, mock_connection_class):
        """Test connect() with driver args."""
        mock_conn = Mock()
        mock_connection_class.return_value = mock_conn

        result = connect(
            jclassname="org.postgresql.Driver",
            url="jdbc:postgresql://localhost:5432/testdb",
            driver_args={"user": "test", "password": "pass"},
        )

        assert result == mock_conn
        call_kwargs = mock_connection_class.call_args[1]
        assert "driver_args" in call_kwargs
