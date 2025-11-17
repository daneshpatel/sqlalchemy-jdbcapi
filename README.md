# SQLAlchemy JDBC/ODBC API 2.0

[![CI](https://github.com/daneshpatel/sqlalchemy-jdbcapi/workflows/CI/badge.svg)](https://github.com/daneshpatel/sqlalchemy-jdbcapi/actions)
[![PyPI version](https://img.shields.io/pypi/v/sqlalchemy-jdbcapi.svg)](https://pypi.org/project/sqlalchemy-jdbcapi/)
[![Python versions](https://img.shields.io/pypi/pyversions/sqlalchemy-jdbcapi.svg)](https://pypi.org/project/sqlalchemy-jdbcapi/)
[![License](https://img.shields.io/pypi/l/sqlalchemy-jdbcapi.svg)](https://github.com/daneshpatel/sqlalchemy-jdbcapi/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/sqlalchemy-jdbcapi.svg)](https://pypi.org/project/sqlalchemy-jdbcapi/)
[![Coverage](https://img.shields.io/badge/coverage-65.47%25-yellow.svg)](htmlcov/index.html)

Modern, type-safe SQLAlchemy dialect for JDBC and ODBC connections with native Python implementation.

## 📚 Documentation

- **[Quick Start Guide](docs/quickstart.md)** - Get started in 5 minutes
- **[Usage Guide](docs/usage.md)** - Comprehensive usage examples
- **[Drivers Guide](docs/drivers.md)** - Detailed driver documentation
- **[SQLAlchemy Integration](docs/sqlalchemy_integration.md)** - Full SQLAlchemy features guide
- **[Troubleshooting Guide](docs/troubleshooting.md)** - Common issues and solutions
- **[Contributing](CONTRIBUTING.md)** - Contribution guidelines

##  Version 2.0 - Major Modernization

Version 2.0 is a complete modernization of the library with:
-  **Automatic JDBC driver download** from Maven Central (zero configuration!)
-  **ODBC support** for native database connectivity
-  **Full SQLAlchemy native dialect integration** (ORM, reflection, Alembic, Inspector API)
-  **DataFrame integration** (pandas, polars, pyarrow)
- ️ **12 database dialects** (8 JDBC + 4 ODBC)
-  **Modern Python 3.10+** with full type hints
-  **SQLAlchemy 2.0+** compatible
-  **SOLID architecture** with clean code principles

## ✨ Features

### JDBC Support
- **Automatic Driver Download**: JDBC drivers auto-download from Maven Central (zero configuration!)
- **Native JDBC Bridge**: Our own DB-API 2.0 implementation using JPype (no JayDeBeApi)
- **Manual Driver Support**: Optional manual driver management via CLASSPATH
- **8 Major Databases**: PostgreSQL, MySQL, MariaDB, SQL Server, Oracle, DB2, SQLite, OceanBase

### ODBC Support (NEW!)
- **Native ODBC Connectivity**: Alternative connection method using pyodbc
- **No JVM Required**: Direct database access without Java runtime
- **4 Major Databases**: PostgreSQL, MySQL, SQL Server, Oracle
- **System Integration**: Uses OS-installed ODBC drivers

### SQLAlchemy Integration
- **Full SQLAlchemy Integration**: Complete native dialect with ORM, reflection, Inspector API, and Alembic support
- **Database Reflection**: Auto-load tables, columns, constraints, indexes, foreign keys from existing databases
- **ORM & Automapping**: Full SQLAlchemy ORM support with automatic model generation from existing schemas
- **DataFrame Integration**: Direct conversion to pandas/polars/arrow for data science workflows

### Code Quality
- **Type Safe**: Comprehensive type hints throughout
- **Modern Python**: Python 3.10+ with latest syntax
- **Best Practices**: Ruff formatting, mypy type checking, comprehensive linting
- **Clean Architecture**: SOLID principles and design patterns

> ** What's Different?** Unlike other JDBC bridges, we provide **true SQLAlchemy native dialect integration**. This means you can use all SQLAlchemy features including table autoload, Inspector API, Alembic migrations, and ORM automapping - not just basic SQL execution!

## 📦 Installation

```bash
# Basic installation
pip install sqlalchemy-jdbcapi

# With DataFrame support (pandas, polars, pyarrow)
pip install sqlalchemy-jdbcapi[dataframe]

# For development
pip install sqlalchemy-jdbcapi[dev]
```

### JDBC Requirements

For JDBC support, you need:

1. **Java Runtime** (JRE 11 or higher)
2. **JPype1** - Python-Java bridge

```bash
# Install Java (if not already installed)
# Ubuntu/Debian:
sudo apt-get update && sudo apt-get install -y openjdk-17-jre

# macOS (using Homebrew):
brew install openjdk@17

# Windows: Download from https://adoptium.net/
```

```bash
# Install JPype1 (IMPORTANT: Use version 1.5.0)
pip install JPype1==1.5.0
```

> **⚠️ Important**: JPype1 version 1.6.0 has a known compatibility issue. **Always use version 1.5.0**:
> ```bash
> pip install JPype1==1.5.0
> ```
>
> If you encounter the error `RuntimeError: Can't find org.jpype.jar support library`, downgrade to JPype1 1.5.0.

**JDBC drivers auto-download** from Maven Central on first use - no manual setup required!

## 🗄️ Supported Databases

### JDBC Dialects (Auto-Download Supported)

| Database | Connection URL | Auto-Download |
|----------|----------------|---------------|
| PostgreSQL | `jdbcapi+postgresql://user:pass@host:5432/db` | ✅ |
| Oracle | `jdbcapi+oracle://user:pass@host:1521/SID` | ✅ |
| MySQL | `jdbcapi+mysql://user:pass@host:3306/db` | ✅ |
| MariaDB | `jdbcapi+mariadb://user:pass@host:3306/db` | ✅ |
| SQL Server | `jdbcapi+mssql://user:pass@host:1433/db` | ✅ |
| DB2 | `jdbcapi+db2://user:pass@host:50000/db` | ✅ |
| OceanBase | `jdbcapi+oceanbase://user:pass@host:2881/db` | ✅ |
| SQLite | `jdbcapi+sqlite:///path/to/db.db` | ✅ |

### ODBC Dialects (OS-Installed Drivers Required)

| Database | Connection URL | Install Guide |
|----------|----------------|---------------|
| PostgreSQL | `odbcapi+postgresql://user:pass@host:5432/db` | [See DRIVERS.md](docs/drivers.md#postgresql-odbc) |
| MySQL | `odbcapi+mysql://user:pass@host:3306/db` | [See DRIVERS.md](docs/drivers.md#mysql-odbc) |
| SQL Server | `odbcapi+mssql://user:pass@host:1433/db` | [See DRIVERS.md](docs/drivers.md#microsoft-sql-server-odbc) |
| Oracle | `odbcapi+oracle://user:pass@host:1521/service` | [See DRIVERS.md](docs/drivers.md#oracle-odbc) |

For detailed driver documentation, see **[DRIVERS.md](docs/drivers.md)**.

## 🚀 Quick Start

### JDBC with Auto-Download (Recommended!)

No setup required - drivers auto-download on first use!

**Option 1: Auto-download on connection (simplest)**

```python
from sqlalchemy import create_engine, text

# PostgreSQL - driver auto-downloads from Maven Central
engine = create_engine('jdbcapi+postgresql://user:password@localhost:5432/mydb')

# Execute queries
with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print(result.scalar())
```

**Option 2: Explicit JVM initialization (recommended for production)**

```python
from sqlalchemy_jdbcapi.jdbc import start_jvm
from sqlalchemy import create_engine, text

# Initialize JVM and download drivers BEFORE creating engines
start_jvm(auto_download=True, databases=["postgresql"])

# Now create engine
engine = create_engine('jdbcapi+postgresql://user:password@localhost:5432/mydb')

with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print(result.scalar())
```

**Download multiple database drivers at once:**

```python
from sqlalchemy_jdbcapi.jdbc import start_jvm

# Download drivers for all databases you'll use
start_jvm(auto_download=True, databases=["postgresql", "mysql", "oracle"])
```

Drivers are cached in `~/.sqlalchemy-jdbcapi/drivers/` for future use.

### ODBC (Alternative)

Requires ODBC driver installation (see [DRIVERS.md](docs/drivers.md)):

```python
from sqlalchemy import create_engine

# PostgreSQL via ODBC (no JVM needed!)
engine = create_engine('odbcapi+postgresql://user:password@localhost:5432/mydb')

with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print(result.scalar())
```

### Manual JDBC Driver Setup (Optional)

If you prefer to manage drivers manually:

```bash
# Set CLASSPATH environment variable
export CLASSPATH="/path/to/postgresql-42.7.1.jar"
```

```python
from sqlalchemy import create_engine

# Will use driver from CLASSPATH
engine = create_engine('jdbcapi+postgresql://user:password@localhost/mydb')
```

For detailed usage, see **[Quick Start Guide](docs/quickstart.md)** and **[Usage Guide](docs/usage.md)**.

## 💡 Examples

**📁 Full Examples Available:**
- **[examples/basic_usage.py](examples/basic_usage.py)** - 8 fundamental usage patterns (JDBC, ODBC, ORM, pooling, transactions)
- **[examples/data_analysis.py](examples/data_analysis.py)** - 8 data science examples (pandas, polars, ETL, analytics, streaming)
- **[examples/README.md](examples/README.md)** - Complete guide with configuration and troubleshooting

### PostgreSQL

```python
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData

# Create engine
engine = create_engine('jdbcapi+postgresql://user:pass@localhost:5432/mydb')

# Define schema
metadata = MetaData()
users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
    Column('email', String(100))
)

# Create tables
metadata.create_all(engine)

# Insert data
with engine.connect() as conn:
    conn.execute(users.insert().values(name='Alice', email='alice@example.com'))
    conn.commit()

# Query data
with engine.connect() as conn:
    result = conn.execute(users.select())
    for row in result:
        print(f"User: {row.name}, Email: {row.email}")
```

### Oracle

```python
from sqlalchemy import create_engine, text

# Standard connection
engine = create_engine('jdbcapi+oracle://user:password@localhost:1521/ORCL')

# TNS name connection
engine = create_engine('jdbcapi+oracle://user:password@TNSNAME')

# With query parameters
from sqlalchemy.engine.url import URL

url = URL.create(
    'jdbcapi+oracle',
    username='user',
    password='password',
    host='localhost',
    port=1521,
    database='ORCL',
    query={'ssl': 'true'}
)
engine = create_engine(url)
```

### MySQL / MariaDB

```python
from sqlalchemy import create_engine

# MySQL
engine = create_engine('jdbcapi+mysql://root:password@localhost:3306/mydb')

# MariaDB
engine = create_engine('jdbcapi+mariadb://root:password@localhost:3306/mydb')

# With SSL
engine = create_engine(
    'jdbcapi+mysql://user:pass@localhost:3306/mydb?useSSL=true&requireSSL=true'
)
```

### SQL Server

```python
from sqlalchemy import create_engine

# Standard connection
engine = create_engine('jdbcapi+mssql://user:password@localhost:1433/mydb')

# Windows Authentication (if supported by JDBC driver)
engine = create_engine(
    'jdbcapi+mssql://localhost:1433/mydb?integratedSecurity=true'
)
```

### DB2

```python
from sqlalchemy import create_engine

# DB2 LUW
engine = create_engine('jdbcapi+db2://user:password@localhost:50000/mydb')

# DB2 z/OS (mainframe)
engine = create_engine('jdbcapi+db2://user:password@mainframe:446/DBCG')
```

### OceanBase

```python
from sqlalchemy import create_engine
from urllib.parse import quote

# OceanBase with tenant and cluster
user = quote('username@tenant#cluster')
engine = create_engine(f'jdbcapi+oceanbase://{user}:password@localhost:2881/mydb')
```

## 🎯 Full SQLAlchemy Integration

Version 2.0 provides **complete SQLAlchemy native dialect integration** with full ORM, reflection, and Inspector API support. See [SQLAlchemy Integration Guide](docs/sqlalchemy_integration.md) for comprehensive documentation.

### ORM Support

Use declarative models with full relationship support:

```python
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Session

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100))
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    user_id = Column(Integer, ForeignKey('users.id'))
    author = relationship("User", back_populates="posts")

# Create engine
engine = create_engine('jdbcapi+postgresql://user:pass@localhost:5432/mydb')

# Create tables
Base.metadata.create_all(engine)

# Use ORM
session = Session(engine)
user = User(name='Alice', email='alice@example.com')
user.posts.append(Post(title='My First Post'))
session.add(user)
session.commit()

# Query with relationships
users = session.query(User).join(User.posts).filter(Post.title.like('%First%')).all()
```

### Table Reflection & Auto-load

Automatically load existing table structures from your database:

```python
from sqlalchemy import Table, MetaData, select

metadata = MetaData()

# Auto-load table structure from database
users = Table('users', metadata, autoload_with=engine)

# Now you can use it!
print(users.columns.keys())  # ['id', 'name', 'email']
print(users.primary_key)     # PrimaryKeyConstraint('id')

# Query the reflected table
with engine.connect() as conn:
    stmt = select(users).where(users.c.name == 'Alice')
    result = conn.execute(stmt)
    for row in result:
        print(row)
```

### Database Inspector

Explore your database schema programmatically:

```python
from sqlalchemy import inspect

inspector = inspect(engine)

# List all schemas
schemas = inspector.get_schema_names()
print(f"Schemas: {schemas}")

# List all tables
tables = inspector.get_table_names(schema='public')
print(f"Tables: {tables}")

# Get column information
columns = inspector.get_columns('users', schema='public')
for col in columns:
    print(f"{col['name']}: {col['type']} (nullable={col['nullable']})")

# Get primary keys
pk = inspector.get_pk_constraint('users', schema='public')
print(f"Primary key: {pk['constrained_columns']}")

# Get foreign keys
fks = inspector.get_foreign_keys('posts', schema='public')
for fk in fks:
    print(f"{fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

# Get indexes
indexes = inspector.get_indexes('users', schema='public')
for idx in indexes:
    print(f"Index {idx['name']}: {idx['column_names']} (unique={idx['unique']})")
```

### ORM Automapping

Automatically generate ORM models from existing databases:

```python
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

# Reflect entire database schema
Base = automap_base()
Base.prepare(engine, reflect=True)

# Classes are generated automatically!
User = Base.classes.users
Post = Base.classes.posts

# Use them like regular ORM models
session = Session(engine)
users = session.query(User).all()
for user in users:
    print(f"{user.name}: {len(user.posts)} posts")
```

### Alembic Migrations

Full support for Alembic database migrations:

```bash
# Initialize Alembic
alembic init migrations

# Configure alembic.ini
sqlalchemy.url = jdbcapi+postgresql://user:pass@localhost:5432/mydb

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add user and post tables"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Reflect and Migrate Between Databases

Copy schemas between different database systems:

```python
from sqlalchemy import MetaData, create_engine

# Reflect schema from PostgreSQL
pg_engine = create_engine('jdbcapi+postgresql://user:pass@localhost/source_db')
metadata = MetaData()
metadata.reflect(bind=pg_engine)

# Migrate to Oracle
oracle_engine = create_engine('jdbcapi+oracle://user:pass@localhost:1521/target_db')
metadata.create_all(oracle_engine)

# Copy data
for table in metadata.sorted_tables:
    with pg_engine.connect() as source:
        data = source.execute(table.select()).fetchall()
        if data:
            with oracle_engine.connect() as target:
                target.execute(table.insert(), [dict(row._mapping) for row in data])
                target.commit()
```

## 📊 DataFrame Integration

Version 2.0 adds powerful DataFrame integration for data science workflows:

```python
from sqlalchemy import create_engine

engine = create_engine('jdbcapi+postgresql://user:pass@localhost/mydb')

# Method 1: Using helper functions
from sqlalchemy_jdbcapi.jdbc.dataframe import cursor_to_pandas

with engine.connect() as conn:
    cursor = conn.connection.cursor()
    cursor.execute("SELECT * FROM large_table WHERE date > '2024-01-01'")

    # Convert to pandas
    df = cursor_to_pandas(cursor)
    print(df.describe())

    # Or polars
    from sqlalchemy_jdbcapi.jdbc.dataframe import cursor_to_polars
    df = cursor_to_polars(cursor)
    print(df.head())

    # Or Apache Arrow
    from sqlalchemy_jdbcapi.jdbc.dataframe import cursor_to_arrow
    table = cursor_to_arrow(cursor)
    print(table.schema)
```

```python
# Method 2: Using cursor convenience methods
with engine.connect() as conn:
    cursor = conn.connection.cursor()
    cursor.execute("SELECT * FROM users")

    # Direct conversion
    df = cursor.to_pandas()    # pandas DataFrame
    df = cursor.to_polars()    # polars DataFrame
    table = cursor.to_arrow()  # Arrow Table
    dicts = cursor.to_dict()   # List of dictionaries
```

## 🎯 Advanced Usage

### Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'jdbcapi+postgresql://user:pass@localhost/mydb',
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600
)
```

### Context Managers

```python
from sqlalchemy import create_engine

engine = create_engine('jdbcapi+postgresql://user:pass@localhost/mydb')

# Connection context
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users"))
    # Connection automatically closed

# Transaction context
with engine.begin() as conn:
    conn.execute(text("INSERT INTO users (name) VALUES (:name)"), {"name": "Bob"})
    # Automatically committed (or rolled back on exception)
```

### Batch Operations

```python
from sqlalchemy import create_engine, text

engine = create_engine('jdbcapi+postgresql://user:pass@localhost/mydb')

# Batch insert
data = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35}
]

with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO users (name, age) VALUES (:name, :age)"),
        data
    )
```

### Type Hints Support

```python
from sqlalchemy import create_engine, text, Engine, Connection, Result
from sqlalchemy.engine import Row

engine: Engine = create_engine('jdbcapi+postgresql://user:pass@localhost/mydb')

def get_users(conn: Connection) -> list[Row]:
    result: Result = conn.execute(text("SELECT * FROM users"))
    return list(result)

with engine.connect() as conn:
    users = get_users(conn)
```

## 🏗️ Architecture

### Project Structure

```
src/sqlalchemy_jdbcapi/
├── __init__.py              # Main package
├── jdbc/                    # JDBC bridge layer (DB-API 2.0)
│   ├── connection.py        # Connection class
│   ├── cursor.py            # Cursor class
│   ├── exceptions.py        # Exception hierarchy
│   ├── types.py             # DB-API type objects
│   ├── type_converter.py    # JDBC ↔ Python type conversion
│   ├── jvm.py               # JVM management
│   └── dataframe.py         # DataFrame integration
└── dialects/                # SQLAlchemy dialects
    ├── base.py              # Base dialect (Template Method)
    ├── postgresql.py        # PostgreSQL dialect
    ├── oracle.py            # Oracle dialect
    ├── mysql.py             # MySQL/MariaDB dialects
    ├── mssql.py             # SQL Server dialect
    ├── db2.py               # DB2 dialect
    ├── oceanbase.py         # OceanBase dialect
    └── sqlite.py            # SQLite dialect
```

### Design Patterns Used

- **Template Method**: `BaseJDBCDialect` provides common functionality
- **Strategy**: Type conversion strategies for different SQL types
- **Factory**: Dialect creation and registration
- **Adapter**: SQLAlchemy URL to JDBC connection arguments
- **Dependency Injection**: Driver configuration

### SQLAlchemy Reflection Implementation

All reflection methods are implemented in `BaseJDBCDialect` using JDBC's `DatabaseMetaData` API:

- **`get_table_names()`** - Uses `DatabaseMetaData.getTables()`
- **`get_columns()`** - Uses `DatabaseMetaData.getColumns()`
- **`get_pk_constraint()`** - Uses `DatabaseMetaData.getPrimaryKeys()`
- **`get_foreign_keys()`** - Uses `DatabaseMetaData.getImportedKeys()`
- **`get_indexes()`** - Uses `DatabaseMetaData.getIndexInfo()`
- **`has_table()`** - Uses `DatabaseMetaData.getTables()`
- **`get_schema_names()`** - Uses `DatabaseMetaData.getSchemas()`
- **`get_view_names()`** - Uses `DatabaseMetaData.getTables()` with VIEW type
- **`get_unique_constraints()`** - Extracted from index information
- **`get_check_constraints()`** - Database-specific implementations

These methods enable full SQLAlchemy features:
- ✅ Table autoload (`Table(..., autoload_with=engine)`)
- ✅ Inspector API (`inspect(engine).get_table_names()`)
- ✅ Alembic migrations (`alembic revision --autogenerate`)
- ✅ ORM automapping (`Base.prepare(engine, reflect=True)`)
- ✅ Cross-database schema migration

## 🔧 Development

### Setup Development Environment

```bash
git clone https://github.com/daneshpatel/sqlalchemy-jdbcapi.git
cd sqlalchemy-jdbcapi

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

**Test Suite Statistics:**
- 📊 **168 total tests** (149 unit/integration, 19 functional)
- ✅ **100% passing** (2 skipped - optional pyodbc)
- 📈 **46.77% coverage** (90%+ on JDBC/ODBC core components)
- 🧪 **3 test categories**: Unit, Integration, Functional

```bash
# Run all tests (unit + integration)
pytest

# Run with coverage report
pytest --cov=sqlalchemy_jdbcapi --cov-report=html

# Run functional tests (requires real databases)
pytest tests/functional/ -v -m functional

# Run network tests (requires internet for Maven Central)
pytest tests/functional/ -v -m network

# Run Docker-based integration tests (recommended!)
./run_docker_tests.sh

# Run specific test file
pytest tests/unit/test_dialects.py

# Run with markers
pytest -m "not slow"  # Skip slow tests
pytest -m "not functional"  # Skip functional tests (default)

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Code Quality

```bash
# Format code
ruff format src tests

# Lint code
ruff check src tests

# Type check
mypy src

# Run all pre-commit hooks
pre-commit run --all-files
```

## 📝 Migration from 1.x to 2.0

### Key Changes

1. **Python Version**: Minimum is now Python 3.10
2. **Dependencies**: JayDeBeApi → JPype1 (automatic)
3. **SQLAlchemy**: Now requires SQLAlchemy 2.0+

### Migration Steps

```python
# 1.x code (still works in 2.0!)
from sqlalchemy import create_engine

engine = create_engine('jdbcapi+pgjdbc://user:pass@localhost/db')
# ✅ Still works with backward compatibility

# 2.0 recommended style
engine = create_engine('jdbcapi+postgresql://user:pass@localhost/db')
# ✨ New preferred naming

# New features in 2.0
with engine.connect() as conn:
    cursor = conn.connection.cursor()
    cursor.execute("SELECT * FROM large_dataset")

    # DataFrame integration (new in 2.0)
    df = cursor.to_pandas()
    print(df.head())
```

See [CHANGELOG.md](CHANGELOG.md) for complete migration guide.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

For security vulnerabilities, please see our [Security Policy](SECURITY.md).

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest && ruff check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original library by Danesh Patel and Pavel Henrykhsen
- SQLAlchemy team for the excellent ORM framework
- JPype contributors for the Java-Python bridge
- All contributors who have helped improve this library

## 📚 Links

- **Documentation**: https://sqlalchemy-jdbcapi.readthedocs.io (coming soon)
- **SQLAlchemy Integration Guide**: [docs/sqlalchemy_integration.md](docs/sqlalchemy_integration.md)
- **PyPI**: https://pypi.org/project/sqlalchemy-jdbcapi/
- **GitHub**: https://github.com/daneshpatel/sqlalchemy-jdbcapi
- **Issues**: https://github.com/daneshpatel/sqlalchemy-jdbcapi/issues
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Code of Conduct**: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **Security Policy**: [SECURITY.md](SECURITY.md)

## 💬 Support

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/daneshpatel/sqlalchemy-jdbcapi/issues)
- **Discussions**: Ask questions on [GitHub Discussions](https://github.com/daneshpatel/sqlalchemy-jdbcapi/discussions)

