"""
Async dialect implementations for SQLAlchemy asyncio support.

These dialects wrap the synchronous JDBC dialects to provide async
functionality using SQLAlchemy 2.0+'s async engine infrastructure.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from sqlalchemy.engine import AdaptedConnection
from sqlalchemy.pool import AsyncAdaptedQueuePool

from ..dialects.access import AccessDialect
from ..dialects.avatica import AvaticaDialect, CalciteDialect, PhoenixDialect
from ..dialects.db2 import DB2Dialect
from ..dialects.gbase import GBase8sDialect
from ..dialects.ibm_iseries import IBMiSeriesDialect
from ..dialects.mssql import MSSQLDialect
from ..dialects.mysql import MySQLDialect
from ..dialects.oracle import OracleDialect
from ..dialects.postgresql import PostgreSQLDialect
from ..dialects.sqlite import SQLiteDialect
from ..jdbc.async_connection import AsyncConnection

logger = logging.getLogger(__name__)


class AsyncAdaptedJDBCConnection(AdaptedConnection):
    """
    Adapter for async JDBC connections to work with SQLAlchemy's async pool.

    This wraps an AsyncConnection to provide the interface expected by
    SQLAlchemy's async connection pool.
    """

    __slots__ = ("_execute_mutex", "dbapi_connection")

    def __init__(self, dbapi_connection: AsyncConnection) -> None:
        self.dbapi_connection = dbapi_connection
        self._execute_mutex = asyncio.Lock()

    @property
    def driver_connection(self) -> AsyncConnection:
        """Get the underlying driver connection."""
        return self.dbapi_connection

    def run_async(self, fn):  # type: ignore
        """Run a synchronous function asynchronously."""
        return asyncio.to_thread(fn)

    async def ping(self, dbapi_connection: AsyncConnection) -> bool:
        """Ping the connection to check if it's alive."""
        try:
            cursor = await dbapi_connection.cursor()
            await cursor.execute("SELECT 1")
            await cursor.close()
            return True
        except Exception as e:
            logger.debug(f"Ping failed: {e}")
            return False


class AsyncJDBCDialectMixin:
    """
    Mixin class that adds async support to JDBC dialects.

    This mixin overrides connection creation to use async connections
    and configures the dialect for async operation.
    """

    is_async = True
    supports_statement_cache = True

    @classmethod
    def get_pool_class(cls, url):  # type: ignore  # noqa: ARG003
        """Use async-adapted queue pool for connection pooling."""
        return AsyncAdaptedQueuePool

    @classmethod
    def get_async_dialect_cls(cls, url):  # type: ignore  # noqa: ARG003
        """Return the async dialect class."""
        return cls

    def get_driver_connection(self, connection):  # type: ignore
        """Get the underlying driver connection from an adapted connection."""
        return connection.dbapi_connection

    def connect(self, *args: Any, **kwargs: Any) -> AsyncAdaptedJDBCConnection:
        """
        Create a connection using the async adapter.

        This is called by SQLAlchemy during connection creation.
        The actual async connection is created in create_connect_args.
        """
        # Get connection arguments
        creator = kwargs.get("creator")
        if creator:
            async_conn = creator()
        else:
            # Create connection from args
            connect_args = self.create_connect_args(kwargs.get("url"))
            if connect_args:
                jclassname, url, driver_args = connect_args
                # Create synchronous connection wrapped in async
                from ..jdbc.connection import Connection

                sync_conn = Connection(jclassname, url, driver_args)
                async_conn = AsyncConnection(sync_conn)
            else:
                raise ValueError("No connection arguments provided")

        return AsyncAdaptedJDBCConnection(async_conn)

    def on_connect(self):  # type: ignore
        """Return a callable for connection initialization."""
        # Get the parent's on_connect
        parent_on_connect = super().on_connect()  # type: ignore

        if parent_on_connect is None:
            return None

        def on_connect_wrapper(conn):  # type: ignore
            # For async connections, we need to run initialization in the event loop
            if isinstance(conn, AsyncAdaptedJDBCConnection):
                # Get the underlying sync connection for initialization
                dbapi_conn = conn.dbapi_connection.sync_connection
                parent_on_connect(dbapi_conn)
            else:
                parent_on_connect(conn)

        return on_connect_wrapper


class AsyncJDBCDialect(AsyncJDBCDialectMixin):
    """Base async JDBC dialect."""

    driver = "jdbcapi+async"


class AsyncPostgreSQLDialect(AsyncJDBCDialectMixin, PostgreSQLDialect):
    """Async PostgreSQL dialect using JDBC driver."""

    driver = "jdbcapi+async"
    name = "postgresql+async"


class AsyncOracleDialect(AsyncJDBCDialectMixin, OracleDialect):
    """Async Oracle dialect using JDBC driver."""

    driver = "jdbcapi+async"
    name = "oracle+async"


class AsyncMySQLDialect(AsyncJDBCDialectMixin, MySQLDialect):
    """Async MySQL dialect using JDBC driver."""

    driver = "jdbcapi+async"
    name = "mysql+async"


class AsyncMSSQLDialect(AsyncJDBCDialectMixin, MSSQLDialect):
    """Async SQL Server dialect using JDBC driver."""

    driver = "jdbcapi+async"
    name = "mssql+async"


class AsyncDB2Dialect(AsyncJDBCDialectMixin, DB2Dialect):
    """Async DB2 dialect using JDBC driver."""

    driver = "jdbcapi+async"
    name = "db2+async"


class AsyncSQLiteDialect(AsyncJDBCDialectMixin, SQLiteDialect):
    """Async SQLite dialect using JDBC driver."""

    driver = "jdbcapi+async"
    name = "sqlite+async"


class AsyncGBase8sDialect(AsyncJDBCDialectMixin, GBase8sDialect):
    """Async GBase 8s dialect using JDBC driver."""

    driver = "jdbcapi+async"
    name = "gbase8s+async"


class AsyncIBMiSeriesDialect(AsyncJDBCDialectMixin, IBMiSeriesDialect):
    """Async IBM iSeries dialect using JDBC driver."""

    driver = "jdbcapi+async"
    name = "iseries+async"


class AsyncAccessDialect(AsyncJDBCDialectMixin, AccessDialect):
    """Async Microsoft Access dialect using JDBC driver."""

    driver = "jdbcapi+async"
    name = "access+async"


class AsyncAvaticaDialect(AsyncJDBCDialectMixin, AvaticaDialect):
    """Async Apache Avatica dialect using JDBC driver."""

    driver = "jdbcapi+async"
    name = "avatica+async"


class AsyncPhoenixDialect(AsyncJDBCDialectMixin, PhoenixDialect):
    """Async Apache Phoenix dialect using JDBC driver."""

    driver = "jdbcapi+async"
    name = "phoenix+async"


class AsyncCalciteDialect(AsyncJDBCDialectMixin, CalciteDialect):
    """Async Apache Calcite dialect using JDBC driver."""

    driver = "jdbcapi+async"
    name = "calcite+async"
