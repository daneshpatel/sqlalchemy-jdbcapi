"""
HikariCP connection pool integration for JDBC connections.

HikariCP is a high-performance JDBC connection pool that provides:
- Extremely fast connection acquisition
- Minimal overhead
- Automatic connection validation
- Leak detection
- Metrics collection
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .exceptions import DatabaseError, InterfaceError
from .jvm import start_jvm

logger = logging.getLogger(__name__)


class HikariConfig:
    """
    Configuration for HikariCP connection pool.

    This class provides a Python-friendly interface to configure HikariCP
    connection pool settings.
    """

    def __init__(
        self,
        jdbc_url: str,
        username: str | None = None,
        password: str | None = None,
        driver_class: str | None = None,
        # Pool sizing
        maximum_pool_size: int = 10,
        minimum_idle: int = 10,  # Best practice: equal to max for fixed-size pool
        # Timeouts (in milliseconds)
        connection_timeout: int = 30000,
        idle_timeout: int = 600000,
        max_lifetime: int = 1800000,
        validation_timeout: int = 5000,
        keepalive_time: int = 0,  # 0 = disabled, should be < max_lifetime
        # Connection validation
        connection_test_query: str | None = None,  # e.g., "SELECT 1"
        connection_init_sql: str | None = None,  # SQL to run on new connections
        # Other settings
        pool_name: str = "JDBCAPIPool",
        auto_commit: bool = False,
        read_only: bool = False,
        catalog: str | None = None,
        schema: str | None = None,
        transaction_isolation: str | None = None,  # e.g., "TRANSACTION_READ_COMMITTED"
        # Leak detection
        leak_detection_threshold: int = 0,
        # Custom properties
        data_source_properties: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize HikariCP configuration.

        Args:
            jdbc_url: JDBC connection URL
            username: Database username
            password: Database password
            driver_class: JDBC driver class name
            maximum_pool_size: Maximum number of connections in the pool
            minimum_idle: Minimum number of idle connections to maintain
            connection_timeout: Maximum time to wait for a connection (ms)
            idle_timeout: Maximum time a connection can sit idle (ms)
            max_lifetime: Maximum lifetime of a connection (ms)
            validation_timeout: Maximum time to wait for connection validation (ms)
            keepalive_time: How often to test idle connections (ms), must be < max_lifetime
            connection_test_query: SQL query to test connection validity (e.g., "SELECT 1")
            connection_init_sql: SQL to run when creating new connections
            pool_name: Name for this pool (for logging/JMX)
            auto_commit: Default auto-commit behavior
            read_only: Set connections as read-only
            catalog: Default catalog for connections
            schema: Default schema for connections
            transaction_isolation: Default transaction isolation level
            leak_detection_threshold: Connection leak detection threshold (ms)
            data_source_properties: Additional data source properties
        """
        self.jdbc_url = jdbc_url
        self.username = username
        self.password = password
        self.driver_class = driver_class
        self.maximum_pool_size = maximum_pool_size
        self.minimum_idle = minimum_idle
        self.connection_timeout = connection_timeout
        self.idle_timeout = idle_timeout
        self.max_lifetime = max_lifetime
        self.validation_timeout = validation_timeout
        self.keepalive_time = keepalive_time
        self.connection_test_query = connection_test_query
        self.connection_init_sql = connection_init_sql
        self.pool_name = pool_name
        self.auto_commit = auto_commit
        self.read_only = read_only
        self.catalog = catalog
        self.schema = schema
        self.transaction_isolation = transaction_isolation
        self.leak_detection_threshold = leak_detection_threshold
        self.data_source_properties = data_source_properties or {}

        # Validate configuration
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate HikariCP configuration values."""
        if self.minimum_idle > self.maximum_pool_size:
            raise ValueError(
                f"minimum_idle ({self.minimum_idle}) cannot be greater than "
                f"maximum_pool_size ({self.maximum_pool_size})"
            )

        if self.keepalive_time > 0 and self.keepalive_time >= self.max_lifetime:
            raise ValueError(
                f"keepalive_time ({self.keepalive_time}ms) must be less than "
                f"max_lifetime ({self.max_lifetime}ms)"
            )

        if self.connection_timeout < 250:
            raise ValueError(
                f"connection_timeout ({self.connection_timeout}ms) must be at least 250ms"
            )

        if self.idle_timeout > 0 and self.idle_timeout < 10000:
            raise ValueError(
                f"idle_timeout ({self.idle_timeout}ms) must be at least 10000ms (10 seconds)"
            )


class HikariConnectionPool:
    """
    HikariCP-based connection pool for JDBC connections.

    Provides high-performance connection pooling with features like:
    - Fast connection acquisition
    - Connection validation
    - Leak detection
    - Metrics collection
    - JMX monitoring

    Example:
        >>> config = HikariConfig(
        ...     jdbc_url='jdbc:postgresql://localhost:5432/mydb',
        ...     username='user',
        ...     password='pass',
        ...     maximum_pool_size=20
        ... )
        >>> pool = HikariConnectionPool(config)
        >>> conn = pool.get_connection()
        >>> # Use connection
        >>> conn.close()  # Returns to pool
        >>> pool.close()  # Shutdown pool
    """

    def __init__(
        self,
        config: HikariConfig,
        jars: list[str] | None = None,
    ) -> None:
        """
        Create a HikariCP connection pool.

        Args:
            config: HikariCP configuration
            jars: Additional JAR files for classpath

        Raises:
            InterfaceError: If JVM or HikariCP cannot be loaded
        """
        self._config = config
        self._hikari_config: Any = None
        self._data_source: Any = None
        self._closed = False

        # Start JVM if needed
        try:
            classpath = (
                [Path(jar) if isinstance(jar, str) else jar for jar in jars]
                if jars
                else None
            )
            start_jvm(classpath=classpath)
        except Exception as e:
            raise InterfaceError(f"Failed to start JVM: {e}") from e

        # Initialize HikariCP
        self._initialize_pool()

    def _initialize_pool(self) -> None:  # noqa: C901
        """Initialize the HikariCP data source."""
        try:
            import jpype

            # Create HikariConfig
            HikariConfigClass = jpype.JClass("com.zaxxer.hikari.HikariConfig")
            self._hikari_config = HikariConfigClass()

            # Set basic configuration
            self._hikari_config.setJdbcUrl(self._config.jdbc_url)

            if self._config.username:
                self._hikari_config.setUsername(self._config.username)
            if self._config.password:
                self._hikari_config.setPassword(self._config.password)
            if self._config.driver_class:
                self._hikari_config.setDriverClassName(self._config.driver_class)

            # Pool sizing
            self._hikari_config.setMaximumPoolSize(self._config.maximum_pool_size)
            self._hikari_config.setMinimumIdle(self._config.minimum_idle)

            # Timeouts
            self._hikari_config.setConnectionTimeout(self._config.connection_timeout)
            self._hikari_config.setIdleTimeout(self._config.idle_timeout)
            self._hikari_config.setMaxLifetime(self._config.max_lifetime)
            self._hikari_config.setValidationTimeout(self._config.validation_timeout)

            # Other settings
            self._hikari_config.setPoolName(self._config.pool_name)
            self._hikari_config.setAutoCommit(self._config.auto_commit)
            self._hikari_config.setReadOnly(self._config.read_only)

            if self._config.catalog:
                self._hikari_config.setCatalog(self._config.catalog)
            if self._config.schema:
                self._hikari_config.setSchema(self._config.schema)

            # Leak detection
            if self._config.leak_detection_threshold > 0:
                self._hikari_config.setLeakDetectionThreshold(
                    self._config.leak_detection_threshold
                )

            # Keepalive time (must be < max_lifetime)
            if self._config.keepalive_time > 0:
                self._hikari_config.setKeepaliveTime(self._config.keepalive_time)

            # Connection test query
            if self._config.connection_test_query:
                self._hikari_config.setConnectionTestQuery(
                    self._config.connection_test_query
                )

            # Connection init SQL
            if self._config.connection_init_sql:
                self._hikari_config.setConnectionInitSql(
                    self._config.connection_init_sql
                )

            # Transaction isolation
            if self._config.transaction_isolation:
                self._hikari_config.setTransactionIsolation(
                    self._config.transaction_isolation
                )

            # Additional data source properties
            for key, value in self._config.data_source_properties.items():
                self._hikari_config.addDataSourceProperty(key, value)

            # Create HikariDataSource
            HikariDataSource = jpype.JClass("com.zaxxer.hikari.HikariDataSource")
            self._data_source = HikariDataSource(self._hikari_config)

            logger.info(
                f"HikariCP pool '{self._config.pool_name}' initialized with "
                f"max_size={self._config.maximum_pool_size}"
            )

        except Exception as e:
            logger.exception(f"Failed to initialize HikariCP: {e}")
            raise InterfaceError(f"Failed to initialize HikariCP: {e}") from e

    def get_connection(self) -> Any:
        """
        Get a connection from the pool.

        Returns:
            JDBC Connection object

        Raises:
            InterfaceError: If pool is closed
            DatabaseError: If connection cannot be obtained
        """
        if self._closed:
            raise InterfaceError("Connection pool is closed")

        try:
            return self._data_source.getConnection()
        except Exception as e:
            raise DatabaseError(f"Failed to get connection from pool: {e}") from e

    def close(self) -> None:
        """Close the connection pool and release all resources."""
        if self._closed:
            return

        try:
            if self._data_source is not None:
                self._data_source.close()
                logger.info(f"HikariCP pool '{self._config.pool_name}' closed")
        except Exception as e:
            logger.warning(f"Error closing HikariCP pool: {e}")
        finally:
            self._data_source = None
            self._closed = True

    @property
    def pool_stats(self) -> dict[str, Any]:
        """
        Get current pool statistics.

        Returns:
            Dictionary with pool metrics
        """
        if self._closed or self._data_source is None:
            return {}

        try:
            pool = self._data_source.getHikariPoolMXBean()
            if pool is None:
                return {}

            return {
                "pool_name": self._config.pool_name,
                "total_connections": int(pool.getTotalConnections()),
                "active_connections": int(pool.getActiveConnections()),
                "idle_connections": int(pool.getIdleConnections()),
                "threads_awaiting_connection": int(pool.getThreadsAwaitingConnection()),
            }
        except Exception as e:
            logger.debug(f"Failed to get pool stats: {e}")
            return {}

    @property
    def is_running(self) -> bool:
        """Check if the pool is running."""
        if self._closed or self._data_source is None:
            return False

        try:
            return self._data_source.isRunning()
        except Exception:
            return False

    def evict_connection(self, connection: Any) -> None:
        """
        Evict a connection from the pool.

        This marks the connection as invalid so it won't be returned to the pool.

        Args:
            connection: The connection to evict
        """
        if self._closed or self._data_source is None:
            return

        try:
            self._data_source.evictConnection(connection)
        except Exception as e:
            logger.debug(f"Failed to evict connection: {e}")

    def suspend_pool(self) -> None:
        """Suspend the connection pool (stop serving connections)."""
        if self._closed or self._data_source is None:
            return

        try:
            pool = self._data_source.getHikariPoolMXBean()
            if pool:
                pool.suspendPool()
                logger.info(f"HikariCP pool '{self._config.pool_name}' suspended")
        except Exception as e:
            logger.warning(f"Failed to suspend pool: {e}")

    def resume_pool(self) -> None:
        """Resume a suspended connection pool."""
        if self._closed or self._data_source is None:
            return

        try:
            pool = self._data_source.getHikariPoolMXBean()
            if pool:
                pool.resumePool()
                logger.info(f"HikariCP pool '{self._config.pool_name}' resumed")
        except Exception as e:
            logger.warning(f"Failed to resume pool: {e}")

    def __enter__(self) -> HikariConnectionPool:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def __del__(self) -> None:
        """Destructor to ensure pool is closed."""
        if not self._closed:
            try:
                self.close()
            except Exception:
                pass
