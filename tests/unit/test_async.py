"""
Unit tests for async JDBC connection and cursor.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sqlalchemy_jdbcapi.jdbc.async_connection import AsyncConnection
from sqlalchemy_jdbcapi.jdbc.async_cursor import AsyncCursor
from sqlalchemy_jdbcapi.jdbc.connection import Connection
from sqlalchemy_jdbcapi.jdbc.cursor import Cursor


class TestAsyncCursor:
    """Tests for async cursor."""

    @pytest.fixture
    def mock_sync_cursor(self) -> MagicMock:
        """Create a mock synchronous cursor."""
        cursor = MagicMock(spec=Cursor)
        cursor.description = (
            ("id", 4, None, None, None, None, True),
            ("name", 12, None, None, None, None, True),
        )
        cursor.rowcount = 1
        cursor.arraysize = 100
        cursor.lastrowid = 1
        return cursor

    @pytest.fixture
    def async_cursor(self, mock_sync_cursor: MagicMock) -> AsyncCursor:
        """Create an async cursor with mock sync cursor."""
        return AsyncCursor(mock_sync_cursor)

    def test_init(self, async_cursor: AsyncCursor, mock_sync_cursor: MagicMock) -> None:
        """Test async cursor initialization."""
        assert async_cursor._sync_cursor is mock_sync_cursor
        assert async_cursor._closed is False

    def test_description(
        self, async_cursor: AsyncCursor, mock_sync_cursor: MagicMock
    ) -> None:
        """Test description property."""
        assert async_cursor.description == mock_sync_cursor.description

    def test_rowcount(
        self, async_cursor: AsyncCursor, mock_sync_cursor: MagicMock
    ) -> None:
        """Test rowcount property."""
        assert async_cursor.rowcount == mock_sync_cursor.rowcount

    def test_arraysize(
        self, async_cursor: AsyncCursor, mock_sync_cursor: MagicMock
    ) -> None:
        """Test arraysize property."""
        assert async_cursor.arraysize == mock_sync_cursor.arraysize

        async_cursor.arraysize = 200
        assert mock_sync_cursor.arraysize == 200

    def test_lastrowid(
        self, async_cursor: AsyncCursor, mock_sync_cursor: MagicMock
    ) -> None:
        """Test lastrowid property."""
        assert async_cursor.lastrowid == mock_sync_cursor.lastrowid

    @pytest.mark.asyncio
    async def test_execute(
        self, async_cursor: AsyncCursor, mock_sync_cursor: MagicMock
    ) -> None:
        """Test execute method."""
        result = await async_cursor.execute("SELECT 1")
        assert result is async_cursor
        mock_sync_cursor.execute.assert_called_once_with("SELECT 1", None)

    @pytest.mark.asyncio
    async def test_execute_with_params(
        self, async_cursor: AsyncCursor, mock_sync_cursor: MagicMock
    ) -> None:
        """Test execute with parameters."""
        await async_cursor.execute("SELECT * FROM users WHERE id = ?", (1,))
        mock_sync_cursor.execute.assert_called_once_with(
            "SELECT * FROM users WHERE id = ?", (1,)
        )

    @pytest.mark.asyncio
    async def test_executemany(
        self, async_cursor: AsyncCursor, mock_sync_cursor: MagicMock
    ) -> None:
        """Test executemany method."""
        params = [(1,), (2,), (3,)]
        await async_cursor.executemany("INSERT INTO t VALUES (?)", params)
        mock_sync_cursor.executemany.assert_called_once_with(
            "INSERT INTO t VALUES (?)", params
        )

    @pytest.mark.asyncio
    async def test_fetchone(
        self, async_cursor: AsyncCursor, mock_sync_cursor: MagicMock
    ) -> None:
        """Test fetchone method."""
        mock_sync_cursor.fetchone.return_value = (1, "test")
        result = await async_cursor.fetchone()
        assert result == (1, "test")

    @pytest.mark.asyncio
    async def test_fetchmany(
        self, async_cursor: AsyncCursor, mock_sync_cursor: MagicMock
    ) -> None:
        """Test fetchmany method."""
        mock_sync_cursor.fetchmany.return_value = [(1, "a"), (2, "b")]
        result = await async_cursor.fetchmany(2)
        assert result == [(1, "a"), (2, "b")]

    @pytest.mark.asyncio
    async def test_fetchall(
        self, async_cursor: AsyncCursor, mock_sync_cursor: MagicMock
    ) -> None:
        """Test fetchall method."""
        mock_sync_cursor.fetchall.return_value = [(1, "a"), (2, "b"), (3, "c")]
        result = await async_cursor.fetchall()
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_close(
        self, async_cursor: AsyncCursor, mock_sync_cursor: MagicMock
    ) -> None:
        """Test close method."""
        await async_cursor.close()
        assert async_cursor._closed is True
        mock_sync_cursor.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(
        self, mock_sync_cursor: MagicMock
    ) -> None:
        """Test async context manager."""
        async with AsyncCursor(mock_sync_cursor) as cursor:
            assert cursor._closed is False
        assert cursor._closed is True

    @pytest.mark.asyncio
    async def test_async_iteration(
        self, async_cursor: AsyncCursor, mock_sync_cursor: MagicMock
    ) -> None:
        """Test async iteration over results."""
        mock_sync_cursor.fetchone.side_effect = [(1,), (2,), None]

        results = []
        async for row in async_cursor:
            results.append(row)

        assert results == [(1,), (2,)]


class TestAsyncConnection:
    """Tests for async connection."""

    @pytest.fixture
    def mock_sync_connection(self) -> MagicMock:
        """Create a mock synchronous connection."""
        conn = MagicMock(spec=Connection)
        conn._jdbc_connection = MagicMock()
        conn.cursor.return_value = MagicMock(spec=Cursor)
        return conn

    @pytest.fixture
    def async_connection(self, mock_sync_connection: MagicMock) -> AsyncConnection:
        """Create an async connection with mock sync connection."""
        return AsyncConnection(mock_sync_connection)

    def test_init(
        self, async_connection: AsyncConnection, mock_sync_connection: MagicMock
    ) -> None:
        """Test async connection initialization."""
        assert async_connection._sync_connection is mock_sync_connection
        assert async_connection._closed is False

    def test_closed_property(self, async_connection: AsyncConnection) -> None:
        """Test closed property."""
        assert async_connection.closed is False
        async_connection._closed = True
        assert async_connection.closed is True

    def test_jconn_property(
        self, async_connection: AsyncConnection, mock_sync_connection: MagicMock
    ) -> None:
        """Test jconn property exposes JDBC connection."""
        assert async_connection.jconn is mock_sync_connection._jdbc_connection

    @pytest.mark.asyncio
    async def test_commit(
        self, async_connection: AsyncConnection, mock_sync_connection: MagicMock
    ) -> None:
        """Test commit method."""
        await async_connection.commit()
        mock_sync_connection.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_rollback(
        self, async_connection: AsyncConnection, mock_sync_connection: MagicMock
    ) -> None:
        """Test rollback method."""
        await async_connection.rollback()
        mock_sync_connection.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_close(
        self, async_connection: AsyncConnection, mock_sync_connection: MagicMock
    ) -> None:
        """Test close method."""
        await async_connection.close()
        assert async_connection._closed is True
        mock_sync_connection.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_cursor(
        self, async_connection: AsyncConnection, mock_sync_connection: MagicMock
    ) -> None:
        """Test cursor creation."""
        cursor = await async_connection.cursor()
        assert isinstance(cursor, AsyncCursor)
        mock_sync_connection.cursor.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_auto_commit(
        self, async_connection: AsyncConnection, mock_sync_connection: MagicMock
    ) -> None:
        """Test set_auto_commit method."""
        await async_connection.set_auto_commit(True)
        mock_sync_connection.set_auto_commit.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_get_auto_commit(
        self, async_connection: AsyncConnection, mock_sync_connection: MagicMock
    ) -> None:
        """Test get_auto_commit method."""
        mock_sync_connection.get_auto_commit.return_value = False
        result = await async_connection.get_auto_commit()
        assert result is False

    @pytest.mark.asyncio
    async def test_context_manager_commit_on_success(
        self, mock_sync_connection: MagicMock
    ) -> None:
        """Test context manager commits on success."""
        async with AsyncConnection(mock_sync_connection):
            pass

        mock_sync_connection.commit.assert_called_once()
        mock_sync_connection.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_rollback_on_error(
        self, mock_sync_connection: MagicMock
    ) -> None:
        """Test context manager rolls back on error."""
        with pytest.raises(ValueError):
            async with AsyncConnection(mock_sync_connection):
                raise ValueError("Test error")

        mock_sync_connection.rollback.assert_called_once()
        mock_sync_connection.close.assert_called_once()
