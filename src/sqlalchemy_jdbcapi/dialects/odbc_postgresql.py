"""
PostgreSQL ODBC dialect for SQLAlchemy.

Provides PostgreSQL database support via ODBC using the official PostgreSQL ODBC driver.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.dialects.postgresql import base as postgresql_base

from .odbc_base import ODBCDialect

logger = logging.getLogger(__name__)


class PostgreSQLODBCDialect(ODBCDialect, postgresql_base.PGDialect):
    """
    PostgreSQL ODBC dialect.

    Supports PostgreSQL via ODBC using the PostgreSQL Unicode ODBC driver.

    Recommended ODBC Driver:
        - PostgreSQL Unicode (psqlODBC): Latest version
        - Download: https://www.postgresql.org/ftp/odbc/versions/

    Connection URL:
        odbcapi+postgresql://user:password@host:5432/database
    """

    name = "postgresql"
    driver = "odbcapi+postgresql"

    # ODBC driver name for PostgreSQL
    pyodbc_driver_name = "PostgreSQL Unicode"

    default_schema_name = "public"
    supports_sequences = True
    supports_native_boolean = True

    @classmethod
    def import_dbapi(cls) -> Any:
        """Import pyodbc module."""
        import pyodbc

        return pyodbc

    def _get_server_version_info(self, connection: Any) -> tuple[int, ...]:
        """Get PostgreSQL server version."""
        cursor = connection.connection.cursor()
        try:
            cursor.execute("SELECT version()")
            version_string = cursor.fetchone()[0]
            # Parse version like "PostgreSQL 15.4 on ..."
            parts = version_string.split()
            if len(parts) >= 2:
                version_parts = parts[1].split(".")
                return tuple(int(p) for p in version_parts)
            return (0, 0, 0)
        finally:
            cursor.close()
