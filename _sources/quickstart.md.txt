# Quick Start Guide

Get started with SQLAlchemy JDBC/ODBC API in 5 minutes!

## Installation

```bash
# Basic installation
pip install sqlalchemy-jdbcapi

# With DataFrame support (pandas, polars, pyarrow)
pip install sqlalchemy-jdbcapi[dataframe]

# With ODBC support
pip install sqlalchemy-jdbcapi[odbc]

# For development
pip install sqlalchemy-jdbcapi[dev]
```

### JDBC Requirements

For JDBC support, you need:

1. **Java Runtime** (JRE 11 or higher)
2. **JPype1** - Python-Java bridge (version 1.5.0)

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

## JDBC with Auto-Download (Recommended!)

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

## Supported Databases

### JDBC Dialects (Auto-Download Supported)

| Database | Connection URL |
|----------|----------------|
| PostgreSQL | `jdbcapi+postgresql://user:pass@host:5432/db` |
| Oracle | `jdbcapi+oracle://user:pass@host:1521/SID` |
| MySQL | `jdbcapi+mysql://user:pass@host:3306/db` |
| MariaDB | `jdbcapi+mariadb://user:pass@host:3306/db` |
| SQL Server | `jdbcapi+mssql://user:pass@host:1433/db` |
| DB2 | `jdbcapi+db2://user:pass@host:50000/db` |
| OceanBase | `jdbcapi+oceanbase://user:pass@host:2881/db` |
| SQLite | `jdbcapi+sqlite:///path/to/db.db` |

### ODBC Dialects (OS-Installed Drivers Required)

| Database | Connection URL |
|----------|----------------|
| PostgreSQL | `odbcapi+postgresql://user:pass@host:5432/db` |
| MySQL | `odbcapi+mysql://user:pass@host:3306/db` |
| SQL Server | `odbcapi+mssql://user:pass@host:1433/db` |
| Oracle | `odbcapi+oracle://user:pass@host:1521/service` |

For detailed driver documentation, see the [Drivers Guide](drivers.md).

## Basic Usage

### Create Engine and Execute Query

```python
from sqlalchemy import create_engine, text

# Create engine
engine = create_engine('jdbcapi+postgresql://user:password@localhost:5432/mydb')

# Execute query
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 1})
    for row in result:
        print(row)
```

### Define Schema and Create Tables

```python
from sqlalchemy import Table, Column, Integer, String, MetaData

metadata = MetaData()
users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
    Column('email', String(100))
)

# Create tables
metadata.create_all(engine)
```

### ORM Support

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100))

# Create tables
Base.metadata.create_all(engine)

# Use ORM
session = Session(engine)
user = User(name='Alice', email='alice@example.com')
session.add(user)
session.commit()
```

## Next Steps

- Read the [Usage Guide](usage.md) for comprehensive examples
- Check the [Drivers Guide](drivers.md) for driver installation
- Explore [SQLAlchemy Integration](sqlalchemy_integration.md) for advanced features
- See [Examples](examples.md) for real-world use cases
