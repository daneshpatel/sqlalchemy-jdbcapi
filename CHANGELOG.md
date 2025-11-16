# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-XX-XX

### 🚀 Added - Major Features

- **Native JDBC Implementation**: Replaced JayDeBeApi dependency with our own modern, type-safe JDBC bridge using JPype
- **DataFrame Integration**: Added native support for pandas, polars, and Apache Arrow
  - `cursor.to_pandas()` - Convert results to pandas DataFrame
  - `cursor.to_polars()` - Convert results to polars DataFrame
  - `cursor.to_arrow()` - Convert results to Apache Arrow Table
  - `cursor.to_dict()` - Convert results to list of dictionaries

- **Expanded Database Support**:
  - ✅ PostgreSQL (enhanced)
  - ✅ Oracle Database (enhanced)
  - ✅ OceanBase (Oracle mode)
  - ✨ **NEW**: MySQL with Connector/J 8.0+
  - ✨ **NEW**: MariaDB with native driver
  - ✨ **NEW**: Microsoft SQL Server
  - ✨ **NEW**: IBM DB2 (LUW and z/OS)
  - ✨ **NEW**: SQLite (via JDBC)

- **Modern Python Support**:
  - Python 3.10+ with full type hints (PEP 484, 585, 604)
  - Modern syntax using union types (`str | None` instead of `Optional[str]`)
  - Full type coverage with mypy strict mode
  - PEP 561 typed marker (`py.typed`)

- **Advanced Type Handling**:
  - Comprehensive JDBC type to Python type conversion
  - Support for CLOB, BLOB, Array types
  - Custom type decorators for database-specific types
  - Proper handling of NULL values
  - Date/Time conversion with microsecond precision

- **Architecture Improvements**:
  - SOLID principles throughout the codebase
  - Template Method pattern for dialect base
  - Strategy pattern for type conversion
  - Dependency Injection for configuration
  - Clean separation of concerns

### 💥 Breaking Changes

- **Dropped Python 3.7, 3.8, 3.9 support** - Minimum version is now Python 3.10
- **Removed JayDeBeApi dependency** - Now uses our own JDBC implementation
- **Module restructure** - Moved to `src/` layout:
  - `sqlalchemy_jdbcapi.jdbc` - JDBC bridge layer
  - `sqlalchemy_jdbcapi.dialects` - Database dialects
  - Old imports still work via backward compatibility

- **Changed default dependency** - Now requires `JPype1>=1.5.0` instead of `JayDeBeApi`
- **SQLAlchemy 2.0+ required** - Minimum SQLAlchemy version is 2.0.0

### 🔧 Changed

- **Migrated to pyproject.toml (PEP 621)** - Modern Python packaging
- **Updated all dependencies to latest versions**:
  - SQLAlchemy >= 2.0.0
  - JPype1 >= 1.5.0
  - pytest >= 8.0.0
  - ruff >= 0.2.0 (replaces flake8, black, isort)

- **Improved error handling** with custom exception hierarchy:
  - `JDBCConnectionError`
  - `JDBCDriverNotFoundError`
  - `JVMNotStartedError`
  - All inherit from DB-API 2.0 exceptions

- **Enhanced logging** throughout the codebase
- **Connection URL aliases** for backward compatibility:
  - `jdbcapi+pgjdbc` → `jdbcapi+postgresql`
  - `jdbcapi+oraclejdbc` → `jdbcapi+oracle`
  - `jdbcapi+oceanbasejdbc` → `jdbcapi+oceanbase`

### 🐛 Fixed

- **Version inconsistency** between `setup.py` and `__init__.py`
- **PostgreSQL array handling** in unique constraints with JDBC types
- **Oracle version detection** with proper regex parsing
- **OceanBase timestamp conversion** using Java Timestamp objects
- **Connection leaks** with proper resource cleanup
- **Type conversion edge cases** for NULL and special values

### 🧪 Testing

- **Comprehensive test suite** with pytest:
  - Unit tests for all dialects
  - Mock-based tests for JDBC operations
  - Type checking with mypy
  - 90%+ code coverage goal

- **Test markers**:
  - `@pytest.mark.slow` - For slow tests
  - `@pytest.mark.integration` - For integration tests
  - `@pytest.mark.requires_jvm` - For JVM-dependent tests
  - `@pytest.mark.requires_jdbc` - For JDBC driver-dependent tests

### 📚 Documentation

- **Comprehensive README** with examples for all databases
- **Type hints** throughout the codebase for better IDE support
- **Docstrings** following Google style
- **Architecture documentation** explaining design patterns
- **Migration guide** from v1.x to v2.0

### 🛠️ Development

- **Modern tooling**:
  - `ruff` for linting and formatting (replaces flake8, black, isort)
  - `mypy` with strict mode for type checking
  - `pytest` with coverage reporting
  - `pre-commit` hooks for code quality

- **GitHub Actions CI/CD**:
  - Multi-Python version testing (3.10, 3.11, 3.12, 3.13)
  - Automated linting and type checking
  - Coverage reporting
  - Automated package building

- **Dependency management**:
  - Optional dependencies for DataFrame support
  - Development dependencies separated
  - Documentation dependencies separated

### 📦 Package Structure

```
src/sqlalchemy_jdbcapi/
├── __init__.py              # Main package
├── _version.py              # Version (auto-generated)
├── py.typed                 # PEP 561 marker
├── jdbc/                    # JDBC bridge layer
│   ├── __init__.py
│   ├── connection.py
│   ├── cursor.py
│   ├── exceptions.py
│   ├── types.py
│   ├── type_converter.py
│   ├── jvm.py
│   └── dataframe.py
└── dialects/                # Database dialects
    ├── __init__.py
    ├── base.py             # Base dialect
    ├── postgresql.py
    ├── oracle.py
    ├── oceanbase.py
    ├── mysql.py
    ├── mssql.py
    ├── db2.py
    └── sqlite.py
```

### 🔮 Future Plans (2.1.0+)

- Async support with SQLAlchemy async engine
- Connection pooling enhancements
- Additional database support (Teradata, Netezza, etc.)
- Performance optimizations
- Batch operation improvements
- Prepared statement caching

---

## [1.3.2] - 2023-XX-XX

### Changed
- Version bump for maintenance release

## [1.3.0] - 2023-08-23

### Added
- OceanBase Oracle mode support
- Query parameters as connection parameters for OceanBase

## [1.2.2] - 2020-10-16

### Added
- SSL support from URL

## [1.2.1] - 2020-09-09

### Fixed
- Minor fixes

## [1.2.0] - 2020-09-01

### Fixed
- PostgreSQL array not iterable issue

## [1.1.0] - 2020-08-04

### Added
- Initial release with PostgreSQL and Oracle support

---

## Migration Guide: 1.x → 2.0

### Installation

**Old (1.x)**:
```bash
pip install sqlalchemy-jdbcapi
```

**New (2.0)**:
```bash
# Basic installation
pip install sqlalchemy-jdbcapi

# With DataFrame support
pip install sqlalchemy-jdbcapi[dataframe]

# For development
pip install sqlalchemy-jdbcapi[dev]
```

### Python Version

**Old**: Python 3.7+
**New**: Python 3.10+ (required)

### Usage (mostly compatible)

```python
# v1.x and v2.0 both work
from sqlalchemy import create_engine

# PostgreSQL
engine = create_engine('jdbcapi+pgjdbc://user:pass@host/db')
# Still works! Also:
engine = create_engine('jdbcapi+postgresql://user:pass@host/db')

# Oracle
engine = create_engine('jdbcapi+oraclejdbc://user:pass@host:1521/SID')
# Still works! Also:
engine = create_engine('jdbcapi+oracle://user:pass@host:1521/SID')
```

### New Features in 2.0

```python
# DataFrame integration
from sqlalchemy import create_engine

engine = create_engine('jdbcapi+postgresql://user:pass@host/db')
with engine.connect() as conn:
    result = conn.execute("SELECT * FROM users")

    # New in 2.0
    import pandas as pd
    from sqlalchemy_jdbcapi.jdbc.dataframe import cursor_to_pandas

    # Or use convenience methods
    cursor = conn.connection.cursor()
    cursor.execute("SELECT * FROM users")
    df = cursor.to_pandas()
```

### Dependencies

**Old**:
- JayDeBeApi (unmaintained)
- SQLAlchemy (any version)

**New**:
- JPype1 >= 1.5.0 (maintained, active)
- SQLAlchemy >= 2.0.0
- Optional: pandas, polars, pyarrow for DataFrame support

[2.0.0]: https://github.com/daneshpatel/sqlalchemy-jdbcapi/compare/v1.3.2...v2.0.0
[1.3.2]: https://github.com/daneshpatel/sqlalchemy-jdbcapi/compare/v1.3.0...v1.3.2
[1.3.0]: https://github.com/daneshpatel/sqlalchemy-jdbcapi/compare/v1.2.2...v1.3.0
[1.2.2]: https://github.com/daneshpatel/sqlalchemy-jdbcapi/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/daneshpatel/sqlalchemy-jdbcapi/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/daneshpatel/sqlalchemy-jdbcapi/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/daneshpatel/sqlalchemy-jdbcapi/releases/tag/v1.1.0
