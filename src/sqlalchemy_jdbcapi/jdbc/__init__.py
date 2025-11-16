"""
JDBC Bridge Layer for SQLAlchemy.

This module provides a Python DB-API 2.0 compliant interface to JDBC drivers
using JPype for JVM interaction. This replaces the unmaintained JayDeBeApi library
with a modern, type-safe, and feature-rich implementation.
"""

from __future__ import annotations

from .connection import Connection, connect
from .cursor import Cursor
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
from .types import (
    BINARY,
    DATETIME,
    NUMBER,
    ROWID,
    STRING,
    Binary,
    Date,
    DateFromTicks,
    Time,
    TimeFromTicks,
    Timestamp,
    TimestampFromTicks,
)

__all__ = [
    # Core functions
    "connect",
    # Classes
    "Connection",
    "Cursor",
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
    # Types
    "Date",
    "Time",
    "Timestamp",
    "DateFromTicks",
    "TimeFromTicks",
    "TimestampFromTicks",
    "Binary",
    "STRING",
    "BINARY",
    "NUMBER",
    "DATETIME",
    "ROWID",
]

# DB-API 2.0 module attributes
apilevel = "2.0"
threadsafety = 1  # Threads may share the module, but not connections
paramstyle = "qmark"  # Question mark style, e.g. ...WHERE name=?
