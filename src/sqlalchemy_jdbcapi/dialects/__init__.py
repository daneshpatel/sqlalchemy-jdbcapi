"""
SQLAlchemy dialects for JDBC connections.

This package provides modern, type-safe dialects for various databases
using JDBC drivers through our native JPype-based implementation.
"""

from __future__ import annotations

from .base import BaseJDBCDialect, JDBCDriverConfig
from .db2 import DB2Dialect
from .mssql import MSSQLDialect
from .mysql import MariaDBDialect, MySQLDialect
from .oceanbase import OceanBaseDialect
from .oracle import OracleDialect
from .postgresql import PostgreSQLDialect
from .sqlite import SQLiteDialect

__all__ = [
    "BaseJDBCDialect",
    "DB2Dialect",
    "JDBCDriverConfig",
    "MSSQLDialect",
    "MariaDBDialect",
    "MySQLDialect",
    "OceanBaseDialect",
    "OracleDialect",
    "PostgreSQLDialect",
    "SQLiteDialect",
]
