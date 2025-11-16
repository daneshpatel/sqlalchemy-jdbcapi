"""
ODBC Bridge Layer for SQLAlchemy.

This module provides a Python DB-API 2.0 compliant interface to ODBC drivers
using pyodbc. This complements the JDBC bridge and provides an alternative
connection method for databases with good ODBC driver support.
"""

from __future__ import annotations

from .connection import Connection, connect
from .exceptions import (
    DatabaseError,
    DataError,
    Error,
    IntegrityError,
    InterfaceError,
    InternalError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    Warning,
)

__all__ = [
    # Core functions
    "connect",
    # Classes
    "Connection",
    # Exceptions
    "Error",
    "Warning",
    "InterfaceError",
    "DatabaseError",
    "InternalError",
    "OperationalError",
    "ProgrammingError",
    "IntegrityError",
    "DataError",
    "NotSupportedError",
]

# DB-API 2.0 module attributes
apilevel = "2.0"
threadsafety = 1  # Threads may share the module, but not connections
paramstyle = "qmark"  # Question mark style, e.g. ...WHERE name=?
