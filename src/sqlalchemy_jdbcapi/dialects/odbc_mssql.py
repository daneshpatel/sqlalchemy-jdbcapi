"""
Microsoft SQL Server ODBC dialect for SQLAlchemy.

Provides SQL Server database support via ODBC.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.dialects.mssql import base as mssql_base

from .odbc_base import ODBCDialect

logger = logging.getLogger(__name__)


class MSSQLODBCDialect(ODBCDialect, mssql_base.MSDialect):
    """
    Microsoft SQL Server ODBC dialect.

    Supports SQL Server via ODBC using the Microsoft ODBC Driver for SQL Server.

    Recommended ODBC Driver:
        - ODBC Driver 18 for SQL Server (latest)
        - ODBC Driver 17 for SQL Server
        - Download: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

    Connection URL:
        odbcapi+mssql://user:password@host:1433/database
        odbcapi+sqlserver://user:password@host:1433/database  (alias)

    Features:
        - Full T-SQL support
        - Window functions
        - CTEs (Common Table Expressions)
        - JSON support (SQL Server 2016+)
        - Sequence support (SQL Server 2012+)
    """

    name = "mssql"
    driver = "odbcapi+mssql"

    # ODBC driver name for SQL Server
    pyodbc_driver_name = "ODBC Driver 18 for SQL Server"

    default_schema_name = "dbo"
    supports_sequences = True  # SQL Server 2012+
    supports_native_boolean = False  # Use BIT instead

    @classmethod
    def import_dbapi(cls) -> Any:
        """Import pyodbc module."""
        import pyodbc

        return pyodbc

    def _get_server_version_info(self, connection: Any) -> tuple[int, ...]:
        """Get SQL Server version."""
        cursor = connection.connection.cursor()
        try:
            cursor.execute("SELECT SERVERPROPERTY('ProductVersion')")
            version_string = cursor.fetchone()[0]
            # Parse version like "15.0.2000.5"
            version_parts = version_string.split(".")
            return tuple(int(p) for p in version_parts[:2])
        finally:
            cursor.close()
