"""
Unit tests for Database X-Ray monitoring features.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from sqlalchemy_jdbcapi.xray.monitor import (
    DatabaseMonitor,
    QueryMetrics,
    QueryStats,
    XRayConfig,
)
from sqlalchemy_jdbcapi.xray.tracer import QueryTracer, TracedConnection, TracedCursor


class TestXRayConfig:
    """Tests for XRayConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = XRayConfig()

        assert config.slow_query_threshold == 1.0
        assert config.max_query_history == 1000
        assert config.log_queries is False
        assert config.capture_parameters is False
        assert config.capture_stack_trace is False
        assert config.aggregation_interval == 60

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        callback = MagicMock()
        config = XRayConfig(
            slow_query_threshold=0.5,
            max_query_history=500,
            log_queries=True,
            capture_parameters=True,
            slow_query_callback=callback,
        )

        assert config.slow_query_threshold == 0.5
        assert config.max_query_history == 500
        assert config.log_queries is True
        assert config.capture_parameters is True
        assert config.slow_query_callback is callback


class TestQueryMetrics:
    """Tests for QueryMetrics."""

    def test_query_metrics_creation(self) -> None:
        """Test creating query metrics."""
        metrics = QueryMetrics(
            query="SELECT * FROM users",
            execution_time=0.5,
            timestamp=datetime.now(),  # noqa: DTZ005
            success=True,
            rows_affected=10,
        )

        assert metrics.query == "SELECT * FROM users"
        assert metrics.execution_time == 0.5
        assert metrics.success is True
        assert metrics.rows_affected == 10

    def test_is_slow_property(self) -> None:
        """Test is_slow property."""
        fast = QueryMetrics(
            query="SELECT 1",
            execution_time=0.1,
            timestamp=datetime.now(),  # noqa: DTZ005
            success=True,
        )
        assert fast.is_slow is False

        slow = QueryMetrics(
            query="SELECT * FROM large_table",
            execution_time=2.0,
            timestamp=datetime.now(),  # noqa: DTZ005
            success=True,
        )
        assert slow.is_slow is True

    def test_failed_query_metrics(self) -> None:
        """Test metrics for failed queries."""
        metrics = QueryMetrics(
            query="SELECT * FROM nonexistent",
            execution_time=0.01,
            timestamp=datetime.now(),  # noqa: DTZ005
            success=False,
            error="Table not found",
        )

        assert metrics.success is False
        assert metrics.error == "Table not found"


class TestQueryStats:
    """Tests for QueryStats aggregation."""

    def test_empty_stats(self) -> None:
        """Test empty statistics."""
        stats = QueryStats()

        assert stats.total_queries == 0
        assert stats.total_time == 0.0
        assert stats.avg_time == 0.0
        assert stats.error_count == 0

    def test_add_execution(self) -> None:
        """Test adding executions to stats."""
        stats = QueryStats()

        stats.add_execution(0.1)
        assert stats.total_queries == 1
        assert stats.total_time == pytest.approx(0.1)
        assert stats.min_time == pytest.approx(0.1)
        assert stats.max_time == pytest.approx(0.1)
        assert stats.first_seen is not None
        assert stats.last_seen is not None

        stats.add_execution(0.2)
        assert stats.total_queries == 2
        assert stats.total_time == pytest.approx(0.3)
        assert stats.min_time == pytest.approx(0.1)
        assert stats.max_time == pytest.approx(0.2)
        assert stats.avg_time == pytest.approx(0.15)

    def test_error_counting(self) -> None:
        """Test error counting."""
        stats = QueryStats()

        stats.add_execution(0.1, is_error=False)
        stats.add_execution(0.2, is_error=True)
        stats.add_execution(0.3, is_error=True)

        assert stats.total_queries == 3
        assert stats.error_count == 2

    def test_slow_query_counting(self) -> None:
        """Test slow query counting."""
        stats = QueryStats()

        stats.add_execution(0.1, is_slow=False)
        stats.add_execution(1.5, is_slow=True)

        assert stats.slow_query_count == 1

    def test_percentile_calculations(self) -> None:
        """Test percentile calculations."""
        stats = QueryStats()

        # Add 100 executions
        for i in range(100):
            stats.add_execution(i * 0.01)

        assert stats.median_time == pytest.approx(0.495, rel=0.01)
        assert stats.p95_time == pytest.approx(0.95, rel=0.01)
        assert stats.p99_time == pytest.approx(0.99, rel=0.01)

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        stats = QueryStats()
        stats.add_execution(0.1)
        stats.add_execution(0.2)

        d = stats.to_dict()

        assert d["total_queries"] == 2
        assert d["avg_time"] == pytest.approx(0.15, rel=0.01)
        assert "first_seen" in d
        assert "last_seen" in d


class TestDatabaseMonitor:
    """Tests for DatabaseMonitor."""

    def test_monitor_creation(self) -> None:
        """Test monitor creation."""
        monitor = DatabaseMonitor()

        assert monitor._total_queries == 0
        assert monitor._total_errors == 0

    def test_record_query(self) -> None:
        """Test recording a query."""
        monitor = DatabaseMonitor()

        metrics = monitor.record_query(
            query="SELECT * FROM users",
            execution_time=0.1,
            success=True,
            rows_affected=10,
        )

        assert metrics.query == "SELECT * FROM users"
        assert monitor._total_queries == 1
        assert monitor._total_errors == 0

    def test_record_failed_query(self) -> None:
        """Test recording a failed query."""
        monitor = DatabaseMonitor()

        monitor.record_query(
            query="SELECT * FROM nonexistent",
            execution_time=0.01,
            success=False,
            error="Table not found",
        )

        assert monitor._total_queries == 1
        assert monitor._total_errors == 1

    def test_slow_query_detection(self) -> None:
        """Test slow query detection."""
        config = XRayConfig(slow_query_threshold=0.5)
        monitor = DatabaseMonitor(config)

        monitor.record_query("SELECT 1", 0.1, success=True)
        monitor.record_query("SELECT * FROM big", 1.0, success=True)

        assert monitor._total_slow_queries == 1

    def test_slow_query_callback(self) -> None:
        """Test slow query callback is invoked."""
        callback = MagicMock()
        config = XRayConfig(slow_query_threshold=0.5, slow_query_callback=callback)
        monitor = DatabaseMonitor(config)

        monitor.record_query("SELECT * FROM big", 1.0, success=True)

        callback.assert_called_once()
        args = callback.call_args[0]
        assert args[0].execution_time == 1.0

    def test_get_summary(self) -> None:
        """Test getting monitoring summary."""
        monitor = DatabaseMonitor()

        monitor.record_query("SELECT 1", 0.1, success=True)
        monitor.record_query("SELECT 2", 0.2, success=False, error="Error")

        summary = monitor.get_summary()

        assert summary["queries"]["total"] == 2
        assert summary["queries"]["errors"] == 1
        assert "uptime_seconds" in summary

    def test_get_slow_queries(self) -> None:
        """Test getting slow queries."""
        config = XRayConfig(slow_query_threshold=0.5)
        monitor = DatabaseMonitor(config)

        monitor.record_query("fast", 0.1, success=True)
        monitor.record_query("slow1", 1.0, success=True)
        monitor.record_query("slow2", 2.0, success=True)

        slow = monitor.get_slow_queries(limit=2)

        assert len(slow) == 2
        assert slow[0].execution_time == 2.0  # Sorted by time desc
        assert slow[1].execution_time == 1.0

    def test_query_normalization(self) -> None:
        """Test query normalization for statistics grouping."""
        monitor = DatabaseMonitor()

        # These should be normalized to the same pattern
        monitor.record_query("SELECT * FROM users WHERE id = 1", 0.1, success=True)
        monitor.record_query("SELECT * FROM users WHERE id = 2", 0.1, success=True)
        monitor.record_query("SELECT * FROM users WHERE id = 100", 0.1, success=True)

        stats = monitor.get_query_stats()

        # Should have only one normalized pattern
        assert len(stats) == 1
        pattern = next(iter(stats.keys()))
        assert stats[pattern]["total_queries"] == 3

    def test_get_top_queries(self) -> None:
        """Test getting top queries by metric."""
        monitor = DatabaseMonitor()

        monitor.record_query("fast", 0.1, success=True)
        monitor.record_query("medium", 0.5, success=True)
        monitor.record_query("slow", 1.0, success=True)

        top = monitor.get_top_queries(by="avg_time", limit=2)

        assert len(top) == 2
        # Slow should be first
        assert top[0][1]["avg_time"] > top[1][1]["avg_time"]

    def test_connection_tracking(self) -> None:
        """Test connection tracking."""
        monitor = DatabaseMonitor()

        monitor.record_connection_open()
        monitor.record_connection_open()

        assert monitor._active_connections == 2
        assert monitor._total_connections == 2

        monitor.record_connection_close()

        assert monitor._active_connections == 1
        assert monitor._total_connections == 2

    def test_reset(self) -> None:
        """Test resetting monitor."""
        monitor = DatabaseMonitor()

        monitor.record_query("SELECT 1", 0.1, success=True)
        monitor.record_connection_open()

        monitor.reset()

        assert monitor._total_queries == 0
        assert monitor._active_connections == 0
        assert len(monitor._query_history) == 0

    def test_export_metrics(self) -> None:
        """Test exporting all metrics."""
        monitor = DatabaseMonitor()

        monitor.record_query("SELECT 1", 0.1, success=True)

        export = monitor.export_metrics()

        assert "summary" in export
        assert "top_by_time" in export
        assert "top_by_count" in export
        assert "recent_errors" in export
        assert "slow_queries" in export

    def test_max_history_limit(self) -> None:
        """Test that history is limited to max size."""
        config = XRayConfig(max_query_history=5)
        monitor = DatabaseMonitor(config)

        for i in range(10):
            monitor.record_query(f"SELECT {i}", 0.1, success=True)

        assert len(monitor._query_history) == 5


class TestTracedCursor:
    """Tests for TracedCursor."""

    def test_traced_cursor_execute(self) -> None:
        """Test traced cursor execute."""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 5
        monitor = DatabaseMonitor()

        traced = TracedCursor(mock_cursor, monitor)
        traced.execute("SELECT * FROM users")

        mock_cursor.execute.assert_called_once_with("SELECT * FROM users", None)
        assert monitor._total_queries == 1

    def test_traced_cursor_with_params(self) -> None:
        """Test traced cursor with parameters."""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        monitor = DatabaseMonitor()

        traced = TracedCursor(mock_cursor, monitor)
        traced.execute("SELECT * FROM users WHERE id = ?", (1,))

        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM users WHERE id = ?", (1,)
        )

    def test_traced_cursor_error_tracking(self) -> None:
        """Test traced cursor tracks errors."""
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB Error")
        monitor = DatabaseMonitor()

        traced = TracedCursor(mock_cursor, monitor)

        with pytest.raises(Exception, match="DB Error"):
            traced.execute("SELECT * FROM invalid")

        assert monitor._total_queries == 1
        assert monitor._total_errors == 1

    def test_traced_cursor_fetch_operations(self) -> None:
        """Test traced cursor fetch operations."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, "test")
        mock_cursor.fetchall.return_value = [(1, "a"), (2, "b")]

        traced = TracedCursor(mock_cursor, DatabaseMonitor())

        assert traced.fetchone() == (1, "test")
        assert traced.fetchall() == [(1, "a"), (2, "b")]

    def test_traced_cursor_properties(self) -> None:
        """Test traced cursor properties."""
        mock_cursor = MagicMock()
        mock_cursor.description = (("id", 4),)
        mock_cursor.rowcount = 10
        mock_cursor.arraysize = 100

        traced = TracedCursor(mock_cursor, DatabaseMonitor())

        assert traced.description == (("id", 4),)
        assert traced.rowcount == 10
        assert traced.arraysize == 100


class TestQueryTracer:
    """Tests for QueryTracer."""

    def test_tracer_creation(self) -> None:
        """Test tracer creation."""
        tracer = QueryTracer()

        assert tracer.monitor is not None
        assert tracer.capture_stack is False

    def test_trace_cursor(self) -> None:
        """Test tracing a cursor."""
        tracer = QueryTracer()
        mock_cursor = MagicMock()

        traced = tracer.trace_cursor(mock_cursor)

        assert isinstance(traced, TracedCursor)

    def test_trace_connection(self) -> None:
        """Test tracing a connection."""
        tracer = QueryTracer()
        mock_conn = MagicMock()

        traced = tracer.trace_connection(mock_conn)

        assert isinstance(traced, TracedConnection)
        assert tracer.monitor._active_connections == 1


class TestTracedConnection:
    """Tests for TracedConnection."""

    def test_traced_connection_cursor(self) -> None:
        """Test traced connection returns traced cursor."""
        tracer = QueryTracer()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        traced = TracedConnection(mock_conn, tracer)
        cursor = traced.cursor()

        assert isinstance(cursor, TracedCursor)

    def test_traced_connection_close(self) -> None:
        """Test traced connection close updates monitor."""
        tracer = QueryTracer()
        mock_conn = MagicMock()

        traced = TracedConnection(mock_conn, tracer)
        assert tracer.monitor._active_connections == 1

        traced.close()

        mock_conn.close.assert_called_once()
        assert tracer.monitor._active_connections == 0

    def test_traced_connection_context_manager(self) -> None:
        """Test traced connection as context manager."""
        tracer = QueryTracer()
        mock_conn = MagicMock()

        with TracedConnection(mock_conn, tracer):
            assert tracer.monitor._active_connections == 1

        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
        assert tracer.monitor._active_connections == 0
