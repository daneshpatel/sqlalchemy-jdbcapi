JDBC Connection for SQLAlchemy.
===============================
.. image:: https://img.shields.io/pypi/dm/sqlalchemy-jdbcapi.svg
        :target: https://pypi.org/project/sqlalchemy-jdbcapi/

The primary purpose of this dialect is to provide JDBC connection using provided driver(JAR).

Installation
------------

Installing the dialect is straightforward::

     python3 -m pip install sqlalchemy-jdbcapi


Usage
-----
Set an environment variable  `export CLASSPATH=<path>/ojdbc8.jar:<path>/postgresql-42.2.9.jre7.jar`

PostgressSQL::

    from sqlalchemy import create_engine
    create_engine('jdbcapi+pgjdbc://{}:{}@{}/{}'.format(username, password, <ip:host>', <database name>))

Oracle::

    create_engine("jdbcapi+oraclejdbc://username:password@HOST:1521/Database")

GenericJDBCConnection::

        Set an environment variable `JDBC_DRIVER_PATH`

Supported databases
-------------------

In theory every database with a suitable JDBC driver should work.

* SQLite
* Hypersonic SQL (HSQLDB)
* IBM DB2
* IBM DB2 for mainframes
* Oracle
* Teradata DB
* Netezza
* Mimer DB
* Microsoft SQL Server
* MySQL
* PostgreSQL
* many more...

Contributing
------------

Please submit `bugs and patches
<https://github.com/daneshpatel/sqlalchemy-jdbcapi/issues>`_.
All contributors will be acknowledged. Thanks!

Changelog
------------
- 1.2.0 - 2020-09-1
  - Issue: PGarray not iterable.

- 1.1.0 - 2020-08-4
  - Initial release.