# SQLAlchemy JDBC/ODBC API

[![CI](https://github.com/daneshpatel/sqlalchemy-jdbcapi/workflows/CI/badge.svg)](https://github.com/daneshpatel/sqlalchemy-jdbcapi/actions)
[![PyPI version](https://img.shields.io/pypi/v/sqlalchemy-jdbcapi.svg)](https://pypi.org/project/sqlalchemy-jdbcapi/)
[![Python versions](https://img.shields.io/pypi/pyversions/sqlalchemy-jdbcapi.svg)](https://pypi.org/project/sqlalchemy-jdbcapi/)
[![License](https://img.shields.io/pypi/l/sqlalchemy-jdbcapi.svg)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/sqlalchemy-jdbcapi.svg)](https://pypi.org/project/sqlalchemy-jdbcapi/)

Modern, type-safe SQLAlchemy dialect for JDBC and ODBC connections with native Python implementation.

## Features

-  **Automatic JDBC driver download** from Maven Central (zero configuration!)
-  **ODBC support** for native database connectivity
-  **Full SQLAlchemy integration** (ORM, reflection, Alembic, Inspector API)
-  **DataFrame integration** (pandas, polars, pyarrow)
- ️ **12 database dialects** (PostgreSQL, Oracle, MySQL, MariaDB, SQL Server, DB2, SQLite, OceanBase)
-  **Modern Python 3.10+** with full type hints
-  **SQLAlchemy 2.0+** compatible

## Installation

```bash
# Basic installation
pip install sqlalchemy-jdbcapi

# With DataFrame support
pip install sqlalchemy-jdbcapi[dataframe]

# With ODBC support
pip install sqlalchemy-jdbcapi[odbc]
```

### JDBC Requirements

JDBC requires Java Runtime Environment (JRE) 8+:

```bash
# Check Java installation
java -version

# Install on Ubuntu/Debian
sudo apt-get install default-jre

# Install on macOS
brew install openjdk
```

## Quick Start

### JDBC (Recommended - Auto-Download)

```python
from sqlalchemy import create_engine

# PostgreSQL - driver downloads automatically!
engine = create_engine('jdbcapi+postgresql://user:password@localhost/mydb')

# Oracle
engine = create_engine('jdbcapi+oracle://user:password@localhost:1521/ORCL')

# MySQL
engine = create_engine('jdbcapi+mysql://user:password@localhost/mydb')
```

### ODBC (Alternative - No JVM)

```python
from sqlalchemy import create_engine

# Requires OS-installed ODBC driver
engine = create_engine('odbcapi+postgresql://user:password@localhost/mydb')
```

### Usage Example

```python
from sqlalchemy import create_engine, text

engine = create_engine('jdbcapi+postgresql://user:pass@localhost/db')

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users"))
    for row in result:
        print(row)
```

## Documentation

📖 **[Full Documentation](https://daneshpatel.github.io/sqlalchemy-jdbcapi/)** (Recommended)

### Quick Links

- **[Quick Start Guide](docs/quickstart.md)** - Get started in 5 minutes
- **[Usage Guide](docs/usage.md)** - Comprehensive examples
- **[Drivers Guide](docs/drivers.md)** - Driver installation & configuration
- **[SQLAlchemy Integration](docs/sqlalchemy_integration.md)** - ORM, reflection, Alembic
- **[Examples](docs/examples.md)** - Code examples for all databases
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues & solutions

## Supported Databases

| Database | JDBC | ODBC | Auto-Download |
|----------|------|------|---------------|
| PostgreSQL | ✅ | ✅ | ✅ |
| Oracle | ✅ | ✅ | ✅ |
| MySQL | ✅ | ✅ | ✅ |
| MariaDB | ✅ | ✅ | ✅ |
| SQL Server | ✅ | ✅ | ✅ |
| DB2 | ✅ | ❌ | ✅ |
| SQLite | ✅ | ❌ | ✅ |
| OceanBase | ✅ | ❌ | ✅ |

See **[Drivers Guide](docs/drivers.md)** for detailed configuration.

## What's New in 2.0

Version 2.0 is a complete modernization:

-  Native JDBC implementation (replaced JayDeBeApi)
-  Added ODBC support
-  DataFrame integration (pandas, polars, pyarrow)
-  Full SQLAlchemy native dialect (ORM, reflection, Alembic)
-  Expanded from 3 to 12 database dialects
-  Modern Python 3.10+ with complete type hints
-  SQLAlchemy 2.0+ support

See **[CHANGELOG.md](CHANGELOG.md)** for migration guide.

## Contributing

We welcome contributions! Please see:

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** - Community guidelines
- **[SECURITY.md](SECURITY.md)** - Security policy

## Development

```bash
# Clone repository
git clone https://github.com/daneshpatel/sqlalchemy-jdbcapi.git
cd sqlalchemy-jdbcapi

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting
ruff check src tests
```

See **[Contributing Guide](CONTRIBUTING.md)** for detailed instructions.

## License

This project is licensed under the Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Links

- **[Documentation](https://daneshpatel.github.io/sqlalchemy-jdbcapi/)** - Full documentation
- **[PyPI](https://pypi.org/project/sqlalchemy-jdbcapi/)** - Package on PyPI
- **[GitHub](https://github.com/daneshpatel/sqlalchemy-jdbcapi)** - Source code
- **[Issues](https://github.com/daneshpatel/sqlalchemy-jdbcapi/issues)** - Bug reports & feature requests
- **[Changelog](CHANGELOG.md)** - Version history

## Support

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/daneshpatel/sqlalchemy-jdbcapi/issues)
- **Discussions**: Ask questions on [GitHub Discussions](https://github.com/daneshpatel/sqlalchemy-jdbcapi/discussions)

