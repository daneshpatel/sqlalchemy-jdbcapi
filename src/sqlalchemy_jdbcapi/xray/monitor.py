"""
Database monitoring and metrics collection.

Provides real-time monitoring of database performance including:
- Query execution times
- Slow query detection
- Connection statistics
- Error tracking
"""

from __future__ import annotations

import logging
import statistics
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class XRayConfig:
    """Configuration for Database X-Ray monitoring."""

    # Slow query threshold (in seconds)
    slow_query_threshold: float = 1.0

    # Maximum number of queries to keep in history
    max_query_history: int = 1000

    # Maximum number of unique query patterns to track
    # Prevents unbounded memory growth from many unique queries
    max_query_patterns: int = 500

    # Enable detailed query logging
    log_queries: bool = False

    # Enable query parameter capture (be careful with sensitive data)
    capture_parameters: bool = False

    # Enable stack trace capture for queries
    capture_stack_trace: bool = False

    # Metrics aggregation interval (seconds)
    aggregation_interval: int = 60

    # Alert callback for slow queries
    slow_query_callback: Any = None

    # Alert callback for errors
    error_callback: Any = None


@dataclass
class QueryMetrics:
    """Metrics for a single query execution."""

    query: str
    execution_time: float
    timestamp: datetime
    success: bool
    rows_affected: int = 0
    error: str | None = None
    parameters: tuple[Any, ...] | None = None
    stack_trace: str | None = None

    @property
    def is_slow(self) -> bool:
        """Check if this query would be considered slow (>1 second)."""
        return self.execution_time > 1.0


@dataclass
class QueryStats:
    """Aggregated statistics for queries."""

    total_queries: int = 0
    total_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0
    avg_time: float = 0.0
    execution_times: list[float] = field(default_factory=list)
    error_count: int = 0
    slow_query_count: int = 0
    first_seen: datetime | None = None
    last_seen: datetime | None = None

    # Maximum number of execution times to keep for percentile calculations
    # This prevents unbounded memory growth
    _max_samples: int = 1000

    def add_execution(
        self, execution_time: float, is_error: bool = False, is_slow: bool = False
    ) -> None:
        """Add an execution to the statistics."""
        self.total_queries += 1
        self.total_time += execution_time
        self.min_time = min(self.min_time, execution_time)
        self.max_time = max(self.max_time, execution_time)

        # Cap execution_times to prevent memory leak
        # Use reservoir sampling to maintain representative samples
        if len(self.execution_times) < self._max_samples:
            self.execution_times.append(execution_time)
        else:
            # Replace random element to maintain statistical properties
            import random
            idx = random.randint(0, self.total_queries - 1)
            if idx < self._max_samples:
                self.execution_times[idx] = execution_time

        if is_error:
            self.error_count += 1
        if is_slow:
            self.slow_query_count += 1

        now = datetime.now()
        if self.first_seen is None:
            self.first_seen = now
        self.last_seen = now

        # Calculate average
        self.avg_time = self.total_time / self.total_queries

    @property
    def median_time(self) -> float:
        """Get median execution time."""
        if not self.execution_times:
            return 0.0
        return statistics.median(self.execution_times)

    @property
    def p95_time(self) -> float:
        """Get 95th percentile execution time."""
        if not self.execution_times:
            return 0.0
        sorted_times = sorted(self.execution_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[min(index, len(sorted_times) - 1)]

    @property
    def p99_time(self) -> float:
        """Get 99th percentile execution time."""
        if not self.execution_times:
            return 0.0
        sorted_times = sorted(self.execution_times)
        index = int(len(sorted_times) * 0.99)
        return sorted_times[min(index, len(sorted_times) - 1)]

    @property
    def stddev_time(self) -> float:
        """Get standard deviation of execution times."""
        if len(self.execution_times) < 2:
            return 0.0
        return statistics.stdev(self.execution_times)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_queries": self.total_queries,
            "total_time": round(self.total_time, 4),
            "min_time": round(self.min_time, 4) if self.min_time != float("inf") else 0,
            "max_time": round(self.max_time, 4),
            "avg_time": round(self.avg_time, 4),
            "median_time": round(self.median_time, 4),
            "p95_time": round(self.p95_time, 4),
            "p99_time": round(self.p99_time, 4),
            "stddev_time": round(self.stddev_time, 4),
            "error_count": self.error_count,
            "slow_query_count": self.slow_query_count,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
        }


class DatabaseMonitor:
    """
    Database monitoring and metrics collection system.

    Tracks query performance, detects slow queries, and collects
    statistics for database operations.

    Example:
        >>> monitor = DatabaseMonitor(XRayConfig(slow_query_threshold=0.5))
        >>> monitor.record_query("SELECT * FROM users", 0.123, success=True)
        >>> print(monitor.get_summary())
    """

    def __init__(self, config: XRayConfig | None = None) -> None:
        """
        Initialize the database monitor.

        Args:
            config: X-Ray configuration settings
        """
        self.config = config or XRayConfig()
        self._lock = threading.RLock()

        # Query history
        self._query_history: list[QueryMetrics] = []

        # Statistics by query pattern (normalized query)
        self._query_stats: dict[str, QueryStats] = defaultdict(QueryStats)

        # Global statistics
        self._total_queries = 0
        self._total_errors = 0
        self._total_slow_queries = 0
        self._start_time = datetime.now()

        # Connection tracking
        self._active_connections = 0
        self._total_connections = 0
        self._connection_errors = 0

    def record_query(
        self,
        query: str,
        execution_time: float,
        success: bool = True,
        rows_affected: int = 0,
        error: str | None = None,
        parameters: tuple[Any, ...] | None = None,
    ) -> QueryMetrics:
        """
        Record a query execution.

        Args:
            query: SQL query string
            execution_time: Execution time in seconds
            success: Whether the query succeeded
            rows_affected: Number of rows affected
            error: Error message if failed
            parameters: Query parameters (if capture enabled)

        Returns:
            QueryMetrics for this execution
        """
        with self._lock:
            # Create metrics
            metrics = QueryMetrics(
                query=query,
                execution_time=execution_time,
                timestamp=datetime.now(),
                success=success,
                rows_affected=rows_affected,
                error=error,
                parameters=parameters if self.config.capture_parameters else None,
            )

            # Check for slow query
            is_slow = execution_time >= self.config.slow_query_threshold

            # Update global stats
            self._total_queries += 1
            if not success:
                self._total_errors += 1
            if is_slow:
                self._total_slow_queries += 1

            # Update query-specific stats
            normalized = self._normalize_query(query)
            self._query_stats[normalized].add_execution(
                execution_time, not success, is_slow
            )

            # Cleanup old query patterns if we exceed the limit
            if len(self._query_stats) > self.config.max_query_patterns:
                self._cleanup_old_patterns()

            # Add to history (with limit)
            self._query_history.append(metrics)
            if len(self._query_history) > self.config.max_query_history:
                self._query_history.pop(0)

            # Log if configured
            if self.config.log_queries:
                log_msg = f"Query executed in {execution_time:.4f}s: {query[:100]}"
                if is_slow:
                    logger.warning(f"SLOW QUERY: {log_msg}")
                else:
                    logger.debug(log_msg)

            # Callbacks
            if is_slow and self.config.slow_query_callback:
                try:
                    self.config.slow_query_callback(metrics)
                except Exception as e:
                    logger.error(f"Slow query callback failed: {e}")

            if not success and self.config.error_callback:
                try:
                    self.config.error_callback(metrics)
                except Exception as e:
                    logger.error(f"Error callback failed: {e}")

            return metrics

    def record_connection_open(self) -> None:
        """Record a new connection being opened."""
        with self._lock:
            self._active_connections += 1
            self._total_connections += 1

    def record_connection_close(self) -> None:
        """Record a connection being closed."""
        with self._lock:
            self._active_connections = max(0, self._active_connections - 1)

    def record_connection_error(self) -> None:
        """Record a connection error."""
        with self._lock:
            self._connection_errors += 1

    def get_summary(self) -> dict[str, Any]:
        """
        Get a summary of all monitored metrics.

        Returns:
            Dictionary with monitoring summary
        """
        with self._lock:
            uptime = (datetime.now() - self._start_time).total_seconds()

            return {
                "uptime_seconds": round(uptime, 2),
                "queries": {
                    "total": self._total_queries,
                    "errors": self._total_errors,
                    "slow": self._total_slow_queries,
                    "queries_per_second": round(self._total_queries / max(1, uptime), 2),
                    "error_rate": round(
                        self._total_errors / max(1, self._total_queries) * 100, 2
                    ),
                },
                "connections": {
                    "active": self._active_connections,
                    "total": self._total_connections,
                    "errors": self._connection_errors,
                },
                "slow_query_threshold": self.config.slow_query_threshold,
            }

    def get_slow_queries(self, limit: int = 10) -> list[QueryMetrics]:
        """
        Get the slowest queries from history.

        Args:
            limit: Maximum number of queries to return

        Returns:
            List of slowest QueryMetrics
        """
        with self._lock:
            slow = [
                q
                for q in self._query_history
                if q.execution_time >= self.config.slow_query_threshold
            ]
            return sorted(slow, key=lambda x: x.execution_time, reverse=True)[:limit]

    def get_query_stats(self, query_pattern: str | None = None) -> dict[str, Any]:
        """
        Get statistics for queries.

        Args:
            query_pattern: Optional pattern to filter queries

        Returns:
            Dictionary with query statistics
        """
        with self._lock:
            if query_pattern:
                normalized = self._normalize_query(query_pattern)
                if normalized in self._query_stats:
                    return {normalized: self._query_stats[normalized].to_dict()}
                return {}

            return {
                pattern: stats.to_dict()
                for pattern, stats in self._query_stats.items()
            }

    def get_top_queries(
        self, by: str = "total_time", limit: int = 10
    ) -> list[tuple[str, dict[str, Any]]]:
        """
        Get top queries by a specific metric.

        Args:
            by: Metric to sort by (total_time, avg_time, total_queries, error_count)
            limit: Maximum number of queries to return

        Returns:
            List of (query_pattern, stats) tuples
        """
        with self._lock:
            items = [
                (pattern, stats.to_dict())
                for pattern, stats in self._query_stats.items()
            ]

            key_map = {
                "total_time": lambda x: x[1]["total_time"],
                "avg_time": lambda x: x[1]["avg_time"],
                "total_queries": lambda x: x[1]["total_queries"],
                "error_count": lambda x: x[1]["error_count"],
                "max_time": lambda x: x[1]["max_time"],
            }

            key_func = key_map.get(by, key_map["total_time"])
            return sorted(items, key=key_func, reverse=True)[:limit]

    def get_recent_errors(self, limit: int = 10) -> list[QueryMetrics]:
        """
        Get recent query errors.

        Args:
            limit: Maximum number of errors to return

        Returns:
            List of failed QueryMetrics
        """
        with self._lock:
            errors = [q for q in self._query_history if not q.success]
            return errors[-limit:]

    def reset(self) -> None:
        """Reset all monitoring data."""
        with self._lock:
            self._query_history.clear()
            self._query_stats.clear()
            self._total_queries = 0
            self._total_errors = 0
            self._total_slow_queries = 0
            self._start_time = datetime.now()
            self._active_connections = 0
            self._total_connections = 0
            self._connection_errors = 0
            logger.info("Database monitor reset")

    def _normalize_query(self, query: str) -> str:
        """
        Normalize a query for grouping statistics.

        Replaces literal values with placeholders to group similar queries.

        Args:
            query: SQL query string

        Returns:
            Normalized query pattern
        """
        import re

        # Normalize whitespace
        normalized = " ".join(query.split())

        # Replace numeric literals
        normalized = re.sub(r"\b\d+\b", "?", normalized)

        # Replace string literals (single quotes)
        normalized = re.sub(r"'[^']*'", "?", normalized)

        # Replace string literals (double quotes in some databases)
        normalized = re.sub(r'"[^"]*"', "?", normalized)

        # Truncate very long queries
        if len(normalized) > 200:
            normalized = normalized[:200] + "..."

        return normalized

    def _cleanup_old_patterns(self) -> None:
        """
        Remove least recently used query patterns to prevent memory leak.

        Keeps the most active patterns based on last_seen timestamp.
        """
        if len(self._query_stats) <= self.config.max_query_patterns:
            return

        # Sort patterns by last_seen, oldest first
        sorted_patterns = sorted(
            self._query_stats.items(),
            key=lambda x: x[1].last_seen or datetime.min
        )

        # Remove oldest patterns until we're at 90% of max
        target_size = int(self.config.max_query_patterns * 0.9)
        patterns_to_remove = len(self._query_stats) - target_size

        for pattern, _ in sorted_patterns[:patterns_to_remove]:
            del self._query_stats[pattern]

        logger.debug(
            f"Cleaned up {patterns_to_remove} old query patterns, "
            f"{len(self._query_stats)} remaining"
        )

    def export_metrics(self) -> dict[str, Any]:
        """
        Export all metrics for external consumption.

        Returns:
            Complete metrics export
        """
        with self._lock:
            return {
                "summary": self.get_summary(),
                "top_by_time": self.get_top_queries("total_time", 20),
                "top_by_count": self.get_top_queries("total_queries", 20),
                "recent_errors": [
                    {
                        "query": q.query[:100],
                        "error": q.error,
                        "timestamp": q.timestamp.isoformat(),
                    }
                    for q in self.get_recent_errors(10)
                ],
                "slow_queries": [
                    {
                        "query": q.query[:100],
                        "execution_time": q.execution_time,
                        "timestamp": q.timestamp.isoformat(),
                    }
                    for q in self.get_slow_queries(10)
                ],
            }


# Global monitor instance for convenience
_global_monitor: DatabaseMonitor | None = None


def get_global_monitor() -> DatabaseMonitor:
    """Get or create the global database monitor."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = DatabaseMonitor()
    return _global_monitor


def set_global_monitor(monitor: DatabaseMonitor) -> None:
    """Set the global database monitor."""
    global _global_monitor
    _global_monitor = monitor
