"""
Oracle ODBC dialect for SQLAlchemy.

Provides Oracle database support via ODBC.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.dialects.oracle import base as oracle_base

from .odbc_base import ODBCDialect

logger = logging.getLogger(__name__)


class OracleODBCDialect(ODBCDialect, oracle_base.OracleDialect):
    """
    Oracle ODBC dialect.

    Supports Oracle Database via ODBC using the Oracle ODBC driver.

    Recommended ODBC Driver:
        - Oracle Instant Client ODBC (latest)
        - Download: https://www.oracle.com/database/technologies/instant-client/downloads.html

    Connection URL:
        odbcapi+oracle://user:password@host:1521/service_name

    Features:
        - Full Oracle SQL support
        - Sequences
        - Synonyms
        - Database links
        - PL/SQL support
    """

    name = "oracle"
    driver = "odbcapi+oracle"

    # ODBC driver name for Oracle
    pyodbc_driver_name = "Oracle in instantclient_21_13"

    supports_sequences = True
    supports_native_boolean = False  # Oracle doesn't have native BOOLEAN type

    @classmethod
    def import_dbapi(cls) -> Any:
        """Import pyodbc module."""
        import pyodbc

        return pyodbc

    def _get_server_version_info(self, connection: Any) -> tuple[int, ...]:
        """Get Oracle server version."""
        cursor = connection.connection.cursor()
        try:
            cursor.execute("SELECT version FROM v$instance")
            version_string = cursor.fetchone()[0]
            # Parse version like "19.0.0.0.0"
            version_parts = version_string.split(".")
            return tuple(int(p) for p in version_parts[:2])
        except Exception:
            # Fallback for restricted permissions
            try:
                cursor.execute("SELECT * FROM v$version WHERE banner LIKE 'Oracle%'")
                banner = cursor.fetchone()[0]
                # Extract version from banner
                import re

                match = re.search(r"Release (\d+)\.(\d+)", banner)
                if match:
                    return (int(match.group(1)), int(match.group(2)))
            except Exception:
                pass
            return (0, 0)
        finally:
            cursor.close()
