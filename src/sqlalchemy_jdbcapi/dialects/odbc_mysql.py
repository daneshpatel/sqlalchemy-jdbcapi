"""
MySQL/MariaDB ODBC dialect for SQLAlchemy.

Provides MySQL and MariaDB database support via ODBC.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.dialects.mysql import base as mysql_base

from .odbc_base import ODBCDialect

logger = logging.getLogger(__name__)


class MySQLODBCDialect(ODBCDialect, mysql_base.MySQLDialect):
    """
    MySQL ODBC dialect.

    Supports MySQL via ODBC using the MySQL Connector/ODBC driver.

    Recommended ODBC Driver:
        - MySQL Connector/ODBC 8.0+
        - Download: https://dev.mysql.com/downloads/connector/odbc/

    Connection URL:
        odbcapi+mysql://user:password@host:3306/database
    """

    name = "mysql"
    driver = "odbcapi+mysql"

    # ODBC driver name for MySQL
    pyodbc_driver_name = "MySQL ODBC 8.0 Driver"

    supports_native_decimal = True

    @classmethod
    def import_dbapi(cls) -> Any:
        """Import pyodbc module."""
        import pyodbc

        return pyodbc

    def _get_server_version_info(self, connection: Any) -> tuple[int, ...]:
        """Get MySQL server version."""
        cursor = connection.connection.cursor()
        try:
            cursor.execute("SELECT VERSION()")
            version_string = cursor.fetchone()[0]
            # Parse version like "8.0.34" or "10.11.3-MariaDB"
            version_parts = version_string.split("-")[0].split(".")
            return tuple(int(p) for p in version_parts[:3])
        finally:
            cursor.close()


class MariaDBODBCDialect(ODBCDialect, mysql_base.MySQLDialect):
    """
    MariaDB ODBC dialect.

    Supports MariaDB via ODBC using the MariaDB Connector/ODBC driver.

    Recommended ODBC Driver:
        - MariaDB Connector/ODBC 3.1+
        - Download: https://mariadb.com/downloads/connectors/odbc/

    Connection URL:
        odbcapi+mariadb://user:password@host:3306/database
    """

    name = "mariadb"
    driver = "odbcapi+mariadb"

    # ODBC driver name for MariaDB
    pyodbc_driver_name = "MariaDB ODBC 3.1 Driver"

    supports_native_decimal = True
    supports_sequences = True  # MariaDB 10.3+

    @classmethod
    def import_dbapi(cls) -> Any:
        """Import pyodbc module."""
        import pyodbc

        return pyodbc

    def _get_server_version_info(self, connection: Any) -> tuple[int, ...]:
        """Get MariaDB server version."""
        cursor = connection.connection.cursor()
        try:
            cursor.execute("SELECT VERSION()")
            version_string = cursor.fetchone()[0]
            # Parse version like "10.11.3-MariaDB"
            version_parts = version_string.split("-")[0].split(".")
            return tuple(int(p) for p in version_parts[:3])
        finally:
            cursor.close()
