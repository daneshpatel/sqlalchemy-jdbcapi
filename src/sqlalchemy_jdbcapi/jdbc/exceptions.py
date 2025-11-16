"""
JDBC Exception hierarchy following DB-API 2.0 specification.
"""

from __future__ import annotations


class Error(Exception):
    """Base class for all JDBC-related errors."""


class Warning(Exception):  # noqa: A001 - DB-API 2.0 requires Warning exception class
    """Exception raised for important warnings."""


class InterfaceError(Error):
    """Exception raised for errors related to the database interface."""


class DatabaseError(Error):
    """Exception raised for errors related to the database."""


class InternalError(DatabaseError):
    """Exception raised when the database encounters an internal error."""


class OperationalError(DatabaseError):
    """Exception raised for operational database errors."""


class ProgrammingError(DatabaseError):
    """Exception raised for programming errors."""


class IntegrityError(DatabaseError):
    """Exception raised when database integrity is violated."""


class DataError(DatabaseError):
    """Exception raised for errors related to processed data."""


class NotSupportedError(DatabaseError):
    """Exception raised when a method or database API is not supported."""


class JDBCDriverNotFoundError(InterfaceError):
    """Exception raised when JDBC driver cannot be found."""


class JVMNotStartedError(InterfaceError):
    """Exception raised when JVM is not started."""
