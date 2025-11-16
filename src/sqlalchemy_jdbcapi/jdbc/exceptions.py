"""
JDBC Exception hierarchy following DB-API 2.0 specification.
"""

from __future__ import annotations


class Error(Exception):
    """Base class for all JDBC-related errors."""

    pass


class Warning(Exception):
    """Exception raised for important warnings."""

    pass


class InterfaceError(Error):
    """Exception raised for errors related to the database interface."""

    pass


class DatabaseError(Error):
    """Exception raised for errors related to the database."""

    pass


class InternalError(DatabaseError):
    """Exception raised when the database encounters an internal error."""

    pass


class OperationalError(DatabaseError):
    """Exception raised for operational database errors."""

    pass


class ProgrammingError(DatabaseError):
    """Exception raised for programming errors."""

    pass


class IntegrityError(DatabaseError):
    """Exception raised when database integrity is violated."""

    pass


class DataError(DatabaseError):
    """Exception raised for errors related to processed data."""

    pass


class NotSupportedError(DatabaseError):
    """Exception raised when a method or database API is not supported."""

    pass


class JDBCDriverNotFoundError(InterfaceError):
    """Exception raised when JDBC driver cannot be found."""

    pass


class JVMNotStartedError(InterfaceError):
    """Exception raised when JVM is not started."""

    pass
