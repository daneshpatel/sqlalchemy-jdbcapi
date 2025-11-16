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
try:
    from ._version import version as __version__
except ImportError:
    __version__ = "2.0.0.dev0"

# Public API
from . import jdbc
from .dialects import (
    DB2Dialect,
    MariaDBDialect,
    MSSQLDialect,
    MySQLDialect,
    OceanBaseDialect,
    OracleDialect,
    PostgreSQLDialect,
    SQLiteDialect,
)

__all__ = [
    # Version
    "__version__",
    # JDBC Module
    "jdbc",
    # Dialects
    "PostgreSQLDialect",
    "OracleDialect",
    "OceanBaseDialect",
    "MySQLDialect",
    "MariaDBDialect",
    "MSSQLDialect",
    "DB2Dialect",
    "SQLiteDialect",
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

except ImportError:
    # SQLAlchemy not installed yet (e.g., during installation)
    pass
