"""
JDBC Bridge Layer for SQLAlchemy.

This module provides a Python DB-API 2.0 compliant interface to JDBC drivers
using JPype for JVM interaction. This replaces the unmaintained JayDeBeApi library
with a modern, type-safe, and feature-rich implementation.
"""

from __future__ import annotations

from .connection import Connection, connect
from .cursor import Cursor
from .driver_manager import (
    RECOMMENDED_JDBC_DRIVERS,
    JDBCDriver,
    clear_driver_cache,
    download_driver,
    get_driver_cache_dir,
    get_driver_path,
    list_cached_drivers,
)
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
from .jvm import get_classpath, is_jvm_started, shutdown_jvm, start_jvm
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
    # JVM management
    "start_jvm",
    "is_jvm_started",
    "shutdown_jvm",
    "get_classpath",
    # Driver management
    "JDBCDriver",
    "RECOMMENDED_JDBC_DRIVERS",
    "download_driver",
    "get_driver_path",
    "get_driver_cache_dir",
    "list_cached_drivers",
    "clear_driver_cache",
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
