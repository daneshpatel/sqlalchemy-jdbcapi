"""
SQLAlchemy dialects for JDBC connections.

This package provides modern, type-safe dialects for various databases
using JDBC drivers through our native JPype-based implementation.
"""

from __future__ import annotations

from .access import AccessDialect, MSAccessDialect
from .avatica import AvaticaDialect, CalciteDialect, PhoenixDialect
from .base import BaseJDBCDialect, JDBCDriverConfig
from .db2 import DB2Dialect
from .gbase import GBase8sDialect, GBaseDialect
from .ibm_iseries import AS400Dialect, IBMiDialect, IBMiSeriesDialect
from .mssql import MSSQLDialect
from .mysql import MariaDBDialect, MySQLDialect
from .oceanbase import OceanBaseDialect
from .oracle import OracleDialect
from .postgresql import PostgreSQLDialect
from .sqlite import SQLiteDialect

__all__ = [
    "BaseJDBCDialect",
    "JDBCDriverConfig",
    # Existing dialects
    "DB2Dialect",
    "MSSQLDialect",
    "MariaDBDialect",
    "MySQLDialect",
    "OceanBaseDialect",
    "OracleDialect",
    "PostgreSQLDialect",
    "SQLiteDialect",
    # New dialects
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
