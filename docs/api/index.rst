API Reference
=============

This section provides detailed API documentation for SQLAlchemy JDBC/ODBC API.

.. toctree::
   :maxdepth: 2

   jdbc
   odbc
   dialects

Overview
--------

The library is organized into three main modules:

* **JDBC Module** (:mod:`sqlalchemy_jdbcapi.jdbc`) - Native JDBC bridge implementation
* **ODBC Module** (:mod:`sqlalchemy_jdbcapi.odbc`) - Native ODBC connectivity
* **Dialects Module** (:mod:`sqlalchemy_jdbcapi.dialects`) - SQLAlchemy dialect implementations

Package Structure
-----------------

.. code-block:: text

    sqlalchemy_jdbcapi/
    ├── jdbc/                    # JDBC bridge layer (DB-API 2.0)
    │   ├── connection.py        # Connection class
    │   ├── cursor.py            # Cursor class
    │   ├── exceptions.py        # Exception hierarchy
    │   ├── types.py             # DB-API type objects
    │   ├── type_converter.py    # JDBC ↔ Python type conversion
    │   ├── jvm.py               # JVM management
    │   ├── driver_manager.py    # Driver management
    │   └── dataframe.py         # DataFrame integration
    ├── odbc/                    # ODBC bridge layer
    │   ├── connection.py        # ODBC Connection implementation
    │   └── exceptions.py        # ODBC exceptions
    └── dialects/                # SQLAlchemy dialects
        ├── base.py              # Base dialect
        ├── postgresql.py        # PostgreSQL dialect
        ├── oracle.py            # Oracle dialect
        ├── mysql.py             # MySQL/MariaDB dialects
        ├── mssql.py             # SQL Server dialect
        ├── db2.py               # DB2 dialect
        ├── oceanbase.py         # OceanBase dialect
        ├── sqlite.py            # SQLite dialect
        └── odbc_*.py            # ODBC dialect variants

Main Entry Point
----------------

.. automodule:: sqlalchemy_jdbcapi
   :members:
   :undoc-members:
   :show-inheritance:
