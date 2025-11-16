"""
Tests for JDBC cursor implementation.

Covers cursor operations, parameter binding, and result fetching.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from sqlalchemy_jdbcapi.jdbc.cursor import Cursor
from sqlalchemy_jdbcapi.jdbc.exceptions import InterfaceError, ProgrammingError


class TestCursor:
    """Test JDBC Cursor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_connection = Mock()
        self.mock_jdbc_conn = Mock()
        self.cursor = Cursor(self.mock_connection, self.mock_jdbc_conn)

    def test_cursor_creation(self):
        """Test cursor can be created."""
        assert self.cursor is not None
        assert not self.cursor._closed
        assert self.cursor.rowcount == -1

    def test_cursor_description_initially_none(self):
        """Test description is None before query execution."""
        assert self.cursor.description is None

    def test_execute_basic_query(self):
        """Test executing a basic SQL query."""
        mock_stmt = Mock()
        mock_resultset = Mock()
        mock_metadata = Mock()

        # Setup result set
        mock_resultset.getMetaData.return_value = mock_metadata
        mock_metadata.getColumnCount.return_value = 2
        mock_metadata.getColumnLabel.side_effect = ["id", "name"]
        mock_metadata.getColumnTypeName.side_effect = ["INTEGER", "VARCHAR"]

        # Setup statement
        mock_stmt.execute.return_value = True
        mock_stmt.getResultSet.return_value = mock_resultset

        self.mock_jdbc_conn.createStatement.return_value = mock_stmt

        # Execute query
        self.cursor.execute("SELECT * FROM users")

        # Verify
        self.mock_jdbc_conn.createStatement.assert_called_once()
        mock_stmt.execute.assert_called_once_with("SELECT * FROM users")
        assert self.cursor.description is not None
        assert len(self.cursor.description) == 2

    def test_execute_with_parameters(self):
        """Test executing query with parameters."""
        mock_stmt = Mock()
        mock_stmt.execute.return_value = False
        mock_stmt.getUpdateCount.return_value = 1

        self.mock_jdbc_conn.prepareStatement.return_value = mock_stmt

        # Execute with parameters
        self.cursor.execute("INSERT INTO users VALUES (?, ?)", [1, "Alice"])

        # Verify prepared statement used
        self.mock_jdbc_conn.prepareStatement.assert_called_once()
        assert mock_stmt.setObject.call_count == 2

    def test_execute_update_query(self):
        """Test executing UPDATE/INSERT query."""
        mock_stmt = Mock()
        mock_stmt.execute.return_value = False  # False means update count available
        mock_stmt.getUpdateCount.return_value = 5

        self.mock_jdbc_conn.createStatement.return_value = mock_stmt

        self.cursor.execute("UPDATE users SET name='Bob'")

        assert self.cursor.rowcount == 5

    def test_execute_on_closed_cursor(self):
        """Test executing on closed cursor raises error."""
        self.cursor.close()

        with pytest.raises(InterfaceError, match="Cursor is closed"):
            self.cursor.execute("SELECT 1")

    def test_executemany(self):
        """Test executing query multiple times."""
        mock_stmt = Mock()
        mock_stmt.executeBatch.return_value = [1, 1, 1]

        self.mock_jdbc_conn.prepareStatement.return_value = mock_stmt

        # Execute many
        params = [[1, "Alice"], [2, "Bob"], [3, "Charlie"]]
        self.cursor.executemany("INSERT INTO users VALUES (?, ?)", params)

        # Verify batch execution
        assert mock_stmt.addBatch.call_count == 3
        mock_stmt.executeBatch.assert_called_once()
        assert self.cursor.rowcount == 3

    def test_fetchone_basic(self):
        """Test fetching one row."""
        mock_resultset = Mock()
        mock_resultset.next.side_effect = [True, False]

        # Setup metadata for description
        mock_metadata = Mock()
        mock_metadata.getColumnCount.return_value = 2
        mock_metadata.getColumnLabel.side_effect = ["id", "name"]
        mock_metadata.getColumnTypeName.side_effect = ["INTEGER", "VARCHAR"]
        mock_metadata.getColumnType.side_effect = [4, 12]  # SQL types

        mock_resultset.getMetaData.return_value = mock_metadata
        # Type converter uses getLong() for INTEGER and getString() for VARCHAR
        mock_resultset.getLong.return_value = 1
        mock_resultset.getString.return_value = "Alice"
        mock_resultset.wasNull.return_value = False

        self.cursor._jdbc_resultset = mock_resultset
        self.cursor._build_description()

        # Fetch one row
        row = self.cursor.fetchone()

        assert row is not None
        assert len(row) == 2
        assert row[0] == 1
        assert row[1] == "Alice"

        # Next fetch should return None
        row = self.cursor.fetchone()
        assert row is None

    def test_fetchone_no_results(self):
        """Test fetchone when no results available."""
        with pytest.raises(InterfaceError, match="No query has been executed"):
            self.cursor.fetchone()

    def test_fetchmany(self):
        """Test fetching multiple rows."""
        mock_resultset = Mock()
        # Return True 5 times, then False
        mock_resultset.next.side_effect = [True] * 5 + [False]

        mock_metadata = Mock()
        mock_metadata.getColumnCount.return_value = 1
        mock_metadata.getColumnLabel.return_value = "id"
        mock_metadata.getColumnTypeName.return_value = "INTEGER"
        mock_metadata.getColumnType.return_value = 4

        mock_resultset.getMetaData.return_value = mock_metadata
        # INTEGER uses getLong()
        mock_resultset.getLong.side_effect = [1, 2, 3, 4, 5]
        mock_resultset.wasNull.return_value = False

        self.cursor._jdbc_resultset = mock_resultset
        self.cursor._build_description()

        # Fetch 3 rows
        rows = self.cursor.fetchmany(3)

        assert len(rows) == 3
        assert rows[0][0] == 1
        assert rows[1][0] == 2
        assert rows[2][0] == 3

    def test_fetchall(self):
        """Test fetching all rows."""
        mock_resultset = Mock()
        mock_resultset.next.side_effect = [True, True, True, False]

        mock_metadata = Mock()
        mock_metadata.getColumnCount.return_value = 1
        mock_metadata.getColumnLabel.return_value = "id"
        mock_metadata.getColumnTypeName.return_value = "INTEGER"
        mock_metadata.getColumnType.return_value = 4

        mock_resultset.getMetaData.return_value = mock_metadata
        # INTEGER uses getLong()
        mock_resultset.getLong.side_effect = [1, 2, 3]
        mock_resultset.wasNull.return_value = False

        self.cursor._jdbc_resultset = mock_resultset
        self.cursor._build_description()

        # Fetch all rows
        rows = self.cursor.fetchall()

        assert len(rows) == 3
        assert rows[0][0] == 1
        assert rows[2][0] == 3

    def test_cursor_as_iterator(self):
        """Test using cursor as iterator."""
        mock_resultset = Mock()
        mock_resultset.next.side_effect = [True, True, False]

        mock_metadata = Mock()
        mock_metadata.getColumnCount.return_value = 1
        mock_metadata.getColumnLabel.return_value = "id"
        mock_metadata.getColumnTypeName.return_value = "INTEGER"
        mock_metadata.getColumnType.return_value = 4

        mock_resultset.getMetaData.return_value = mock_metadata
        # INTEGER uses getLong()
        mock_resultset.getLong.side_effect = [1, 2]
        mock_resultset.wasNull.return_value = False

        self.cursor._jdbc_resultset = mock_resultset
        self.cursor._build_description()

        # Iterate over cursor
        rows = list(self.cursor)

        assert len(rows) == 2
        assert rows[0][0] == 1
        assert rows[1][0] == 2

    def test_close_cursor(self):
        """Test closing cursor."""
        mock_stmt = Mock()
        self.cursor._jdbc_statement = mock_stmt

        self.cursor.close()

        assert self.cursor._closed
        mock_stmt.close.assert_called_once()

    def test_close_cursor_idempotent(self):
        """Test closing cursor multiple times."""
        mock_stmt = Mock()
        self.cursor._jdbc_statement = mock_stmt

        self.cursor.close()
        self.cursor.close()  # Should not raise

        assert mock_stmt.close.call_count == 1

    def test_setinputsizes(self):
        """Test setinputsizes (no-op in JDBC)."""
        # Should not raise
        self.cursor.setinputsizes([100, 200])

    def test_setoutputsize(self):
        """Test setoutputsize (no-op in JDBC)."""
        # Should not raise
        self.cursor.setoutputsize(100, 0)

    def test_arraysize_property(self):
        """Test arraysize property."""
        assert self.cursor.arraysize == 1

        self.cursor.arraysize = 100
        assert self.cursor.arraysize == 100

    def test_handle_null_values(self):
        """Test proper handling of NULL values."""
        mock_resultset = Mock()
        mock_resultset.next.side_effect = [True, False]

        mock_metadata = Mock()
        mock_metadata.getColumnCount.return_value = 1
        mock_metadata.getColumnLabel.return_value = "value"
        mock_metadata.getColumnTypeName.return_value = "VARCHAR"
        mock_metadata.getColumnType.return_value = 12

        mock_resultset.getMetaData.return_value = mock_metadata
        mock_resultset.getObject.return_value = None
        mock_resultset.wasNull.return_value = True

        self.cursor._jdbc_resultset = mock_resultset
        self.cursor._build_description()

        row = self.cursor.fetchone()

        assert row is not None
        assert row[0] is None

    def test_execute_error_handling(self):
        """Test error handling in execute."""
        mock_stmt = Mock()
        mock_stmt.execute.side_effect = Exception("SQL error")

        self.mock_jdbc_conn.createStatement.return_value = mock_stmt

        with pytest.raises(ProgrammingError, match="Failed to execute"):
            self.cursor.execute("INVALID SQL")

    def test_executemany_error_handling(self):
        """Test error handling in executemany."""
        mock_stmt = Mock()
        mock_stmt.executeBatch.side_effect = Exception("Batch error")

        self.mock_jdbc_conn.prepareStatement.return_value = mock_stmt

        with pytest.raises(ProgrammingError, match="Failed to execute batch"):
            self.cursor.executemany("INSERT INTO users VALUES (?)", [[1], [2]])


class TestCursorParameterBinding:
    """Test parameter binding in cursor."""

    def test_bind_integer_parameter(self):
        """Test binding integer parameter."""
        mock_connection = Mock()
        mock_jdbc_conn = Mock()
        cursor = Cursor(mock_connection, mock_jdbc_conn)

        mock_stmt = Mock()

        # Call internal method directly
        cursor._bind_parameters(mock_stmt, [42])

        mock_stmt.setObject.assert_called_once_with(1, 42)

    def test_bind_string_parameter(self):
        """Test binding string parameter."""
        mock_connection = Mock()
        mock_jdbc_conn = Mock()
        cursor = Cursor(mock_connection, mock_jdbc_conn)

        mock_stmt = Mock()

        cursor._bind_parameters(mock_stmt, ["hello"])

        mock_stmt.setObject.assert_called_once_with(1, "hello")

    def test_bind_none_parameter(self):
        """Test binding None (NULL) parameter."""
        mock_connection = Mock()
        mock_jdbc_conn = Mock()
        cursor = Cursor(mock_connection, mock_jdbc_conn)

        mock_stmt = Mock()

        cursor._bind_parameters(mock_stmt, [None])

        # None uses setNull() not setObject()
        mock_stmt.setNull.assert_called_once_with(1, 0)

    def test_bind_multiple_parameters(self):
        """Test binding multiple parameters."""
        mock_connection = Mock()
        mock_jdbc_conn = Mock()
        cursor = Cursor(mock_connection, mock_jdbc_conn)

        mock_stmt = Mock()

        cursor._bind_parameters(mock_stmt, [1, "Alice", None, 42.5])

        # 3 setObject calls (for 1, "Alice", 42.5) and 1 setNull call (for None)
        assert mock_stmt.setObject.call_count == 3
        assert mock_stmt.setNull.call_count == 1
