"""
SQLAlchemy JDBC API - Modern JDBC Dialect for SQLAlchemy.

This package provides a modern, type-safe SQLAlchemy dialect for JDBC connections,
supporting multiple databases through a native JPype-based implementation.

Supported Databases:
- PostgreSQL
- Oracle Database
- OceanBase (Oracle mode)
- MySQL
- MariaDB
- Microsoft SQL Server
- IBM DB2
- SQLite (via JDBC)

Features:
- Modern Python 3.10+ with full type hints
- Native JDBC implementation (no JayDeBeApi dependency)
- DataFrame integration (pandas, polars, pyarrow)
- SQLAlchemy 2.0+ compatible
- Comprehensive error handling and logging
- Connection pooling support

Example usage:
    >>> from sqlalchemy import create_engine
    >>> # PostgreSQL
    >>> engine = create_engine('jdbcapi+postgresql://user:pass@localhost/db')
    >>> # Oracle
    >>> engine = create_engine('jdbcapi+oracle://user:pass@localhost:1521/ORCL')
    >>> # MySQL
    >>> engine = create_engine('jdbcapi+mysql://user:pass@localhost/db')
"""

from __future__ import annotations

# Version management
# Version is managed by bump2version
__version__ = "2.1.3"

# Public API
from . import jdbc, xray
from .dialects import (
    # Existing dialects
    DB2Dialect,
    MariaDBDialect,
    MSSQLDialect,
    MySQLDialect,
    OceanBaseDialect,
    OracleDialect,
    PostgreSQLDialect,
    SQLiteDialect,
    # New dialects
    AccessDialect,
    AS400Dialect,
    AvaticaDialect,
    CalciteDialect,
    GBase8sDialect,
    GBaseDialect,
    IBMiDialect,
    IBMiSeriesDialect,
    MSAccessDialect,
    PhoenixDialect,
)

__all__ = [
    # Version
    "__version__",
    # Modules
    "jdbc",
    "xray",
    # Existing Dialects
    "PostgreSQLDialect",
    "OracleDialect",
    "OceanBaseDialect",
    "MySQLDialect",
    "MariaDBDialect",
    "MSSQLDialect",
    "DB2Dialect",
    "SQLiteDialect",
    # New Dialects
    "GBase8sDialect",
    "GBaseDialect",
    "IBMiSeriesDialect",
    "IBMiDialect",
    "AS400Dialect",
    "AccessDialect",
    "MSAccessDialect",
    "AvaticaDialect",
    "PhoenixDialect",
    "CalciteDialect",
]

# SQLAlchemy dialect registration
# This is automatically done via entry_points in pyproject.toml,
# but we can also register them here for programmatic access
try:
    from sqlalchemy.dialects import registry

    # Register all dialects
    registry.register(
        "jdbcapi.postgresql",
        "sqlalchemy_jdbcapi.dialects.postgresql",
        "PostgreSQLDialect",
    )
    registry.register(
        "jdbcapi.pgjdbc",  # Alias for backward compatibility
        "sqlalchemy_jdbcapi.dialects.postgresql",
        "PostgreSQLDialect",
    )
    registry.register(
        "jdbcapi.oracle", "sqlalchemy_jdbcapi.dialects.oracle", "OracleDialect"
    )
    registry.register(
        "jdbcapi.oraclejdbc",  # Alias for backward compatibility
        "sqlalchemy_jdbcapi.dialects.oracle",
        "OracleDialect",
    )
    registry.register(
        "jdbcapi.oceanbase",
        "sqlalchemy_jdbcapi.dialects.oceanbase",
        "OceanBaseDialect",
    )
    registry.register(
        "jdbcapi.oceanbasejdbc",  # Alias for backward compatibility
        "sqlalchemy_jdbcapi.dialects.oceanbase",
        "OceanBaseDialect",
    )
    registry.register(
        "jdbcapi.mysql", "sqlalchemy_jdbcapi.dialects.mysql", "MySQLDialect"
    )
    registry.register(
        "jdbcapi.mariadb", "sqlalchemy_jdbcapi.dialects.mysql", "MariaDBDialect"
    )
    registry.register(
        "jdbcapi.mssql", "sqlalchemy_jdbcapi.dialects.mssql", "MSSQLDialect"
    )
    registry.register(
        "jdbcapi.sqlserver",  # Alias
        "sqlalchemy_jdbcapi.dialects.mssql",
        "MSSQLDialect",
    )
    registry.register("jdbcapi.db2", "sqlalchemy_jdbcapi.dialects.db2", "DB2Dialect")
    registry.register(
        "jdbcapi.sqlite", "sqlalchemy_jdbcapi.dialects.sqlite", "SQLiteDialect"
    )

    # New dialect registrations
    registry.register(
        "jdbcapi.gbase8s", "sqlalchemy_jdbcapi.dialects.gbase", "GBase8sDialect"
    )
    registry.register(
        "jdbcapi.gbase", "sqlalchemy_jdbcapi.dialects.gbase", "GBaseDialect"
    )
    registry.register(
        "jdbcapi.iseries",
        "sqlalchemy_jdbcapi.dialects.ibm_iseries",
        "IBMiSeriesDialect",
    )
    registry.register(
        "jdbcapi.as400", "sqlalchemy_jdbcapi.dialects.ibm_iseries", "AS400Dialect"
    )
    registry.register(
        "jdbcapi.ibmi", "sqlalchemy_jdbcapi.dialects.ibm_iseries", "IBMiDialect"
    )
    registry.register(
        "jdbcapi.access", "sqlalchemy_jdbcapi.dialects.access", "AccessDialect"
    )
    registry.register(
        "jdbcapi.msaccess", "sqlalchemy_jdbcapi.dialects.access", "MSAccessDialect"
    )
    registry.register(
        "jdbcapi.avatica", "sqlalchemy_jdbcapi.dialects.avatica", "AvaticaDialect"
    )
    registry.register(
        "jdbcapi.phoenix", "sqlalchemy_jdbcapi.dialects.avatica", "PhoenixDialect"
    )
    registry.register(
        "jdbcapi.calcite", "sqlalchemy_jdbcapi.dialects.avatica", "CalciteDialect"
    )

    # Async dialect registrations
    registry.register(
        "jdbcapi.postgresql+async",
        "sqlalchemy_jdbcapi.asyncio.dialect",
        "AsyncPostgreSQLDialect",
    )
    registry.register(
        "jdbcapi.oracle+async",
        "sqlalchemy_jdbcapi.asyncio.dialect",
        "AsyncOracleDialect",
    )
    registry.register(
        "jdbcapi.mysql+async",
        "sqlalchemy_jdbcapi.asyncio.dialect",
        "AsyncMySQLDialect",
    )
    registry.register(
        "jdbcapi.mssql+async",
        "sqlalchemy_jdbcapi.asyncio.dialect",
        "AsyncMSSQLDialect",
    )
    registry.register(
        "jdbcapi.db2+async", "sqlalchemy_jdbcapi.asyncio.dialect", "AsyncDB2Dialect"
    )
    registry.register(
        "jdbcapi.sqlite+async",
        "sqlalchemy_jdbcapi.asyncio.dialect",
        "AsyncSQLiteDialect",
    )

except ImportError:
    # SQLAlchemy not installed yet (e.g., during installation)
    pass
