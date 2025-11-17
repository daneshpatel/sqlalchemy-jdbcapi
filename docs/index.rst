SQLAlchemy JDBC/ODBC API Documentation
=======================================

.. image:: https://img.shields.io/pypi/v/sqlalchemy-jdbcapi.svg
   :target: https://pypi.org/project/sqlalchemy-jdbcapi/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/sqlalchemy-jdbcapi.svg
   :target: https://pypi.org/project/sqlalchemy-jdbcapi/
   :alt: Python versions

.. image:: https://img.shields.io/pypi/l/sqlalchemy-jdbcapi.svg
   :target: https://github.com/daneshpatel/sqlalchemy-jdbcapi/blob/main/LICENSE
   :alt: License

Modern, type-safe SQLAlchemy dialect for JDBC and ODBC connections with native Python implementation.

Version 2.0 - Major Modernization
----------------------------------

Version 2.0 is a complete modernization of the library with:

*  **Automatic JDBC driver download** from Maven Central (zero configuration!)
*  **ODBC support** for native database connectivity
*  **Full SQLAlchemy native dialect integration** (ORM, reflection, Alembic, Inspector API)
*  **DataFrame integration** (pandas, polars, pyarrow)
* ️ **12 database dialects** (8 JDBC + 4 ODBC)
*  **Modern Python 3.10+** with full type hints
*  **SQLAlchemy 2.0+** compatible
* 🏗 **SOLID architecture** with clean code principles

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   quickstart
   usage
   drivers
   sqlalchemy_integration
   examples
   troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index
   api/jdbc
   api/odbc
   api/dialects

Resources
=========

Development
-----------

* `Contributing Guide <https://github.com/daneshpatel/sqlalchemy-jdbcapi/blob/master/CONTRIBUTING.md>`_
* `Changelog <https://github.com/daneshpatel/sqlalchemy-jdbcapi/blob/master/CHANGELOG.md>`_
* `Code of Conduct <https://github.com/daneshpatel/sqlalchemy-jdbcapi/blob/master/CODE_OF_CONDUCT.md>`_
* `Security Policy <https://github.com/daneshpatel/sqlalchemy-jdbcapi/blob/master/SECURITY.md>`_

Community
---------

* `GitHub Repository <https://github.com/daneshpatel/sqlalchemy-jdbcapi>`_
* `Issue Tracker <https://github.com/daneshpatel/sqlalchemy-jdbcapi/issues>`_
* `Discussions <https://github.com/daneshpatel/sqlalchemy-jdbcapi/discussions>`_
* `PyPI Package <https://pypi.org/project/sqlalchemy-jdbcapi/>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
