"""
ODBC-specific exceptions.

Most exceptions are proxied from pyodbc, but we provide our own hierarchy
for consistency with DB-API 2.0 specification.
"""

from __future__ import annotations


class Error(Exception):
    """Base exception for all ODBC errors."""


class Warning(Exception):  # noqa: A001
    """Exception raised for important warnings."""


class InterfaceError(Error):
    """Exception raised for errors related to the database interface."""


class DatabaseError(Error):
    """Exception raised for errors related to the database."""


class InternalError(DatabaseError):
    """Exception raised for internal database errors."""


class OperationalError(DatabaseError):
    """Exception raised for operational database errors."""


class ProgrammingError(DatabaseError):
    """Exception raised for programming errors."""


class IntegrityError(DatabaseError):
    """Exception raised for database integrity errors."""


class DataError(DatabaseError):
    """Exception raised for data processing errors."""


class NotSupportedError(DatabaseError):
    """Exception raised for unsupported operations."""
