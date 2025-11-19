"""
SQLAlchemy asyncio support for JDBC connections.

This module provides async engine and dialect support for SQLAlchemy 2.0+,
allowing use of JDBC connections with async/await syntax.

Example usage:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    # Create async engine
    engine = create_async_engine(
        'jdbcapi+postgresql+async://user:pass@localhost/db'
    )

    # Create async session
    async_session = sessionmaker(engine, class_=AsyncSession)

    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
"""

from __future__ import annotations

from .dialect import (
    AsyncJDBCDialect,
    AsyncDB2Dialect,
    AsyncMSSQLDialect,
    AsyncMySQLDialect,
    AsyncOracleDialect,
    AsyncPostgreSQLDialect,
    AsyncSQLiteDialect,
)

__all__ = [
    "AsyncJDBCDialect",
    "AsyncPostgreSQLDialect",
    "AsyncOracleDialect",
    "AsyncMySQLDialect",
    "AsyncMSSQLDialect",
    "AsyncDB2Dialect",
    "AsyncSQLiteDialect",
]
