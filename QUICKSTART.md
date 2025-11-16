# Quick Start Guide

Get started with sqlalchemy-jdbcapi in less than 5 minutes!

## Installation

```bash
pip install sqlalchemy-jdbcapi
```

### Requirements

- **Python**: 3.10 or higher
- **Java**: JDK 8 or higher (for JDBC support)
- **SQLAlchemy**: 2.0 or higher

## Choose Your Connection Method

sqlalchemy-jdbcapi supports two connection methods:

1. **JDBC** (Java Database Connectivity) - Recommended for most databases
2. **ODBC** (Open Database Connectivity) - Alternative with native drivers

## Quick Start with JDBC (Auto-Download)

### PostgreSQL Example

```python
from sqlalchemy import create_engine, text

# Create engine - JDBC drivers auto-download on first use!
engine = create_engine("jdbcapi+postgresql://user:password@localhost:5432/mydb")

# Execute a query
with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print(result.fetchone())
```

That's it! The JDBC driver will be automatically downloaded from Maven Central on first use.

### MySQL Example

```python
from sqlalchemy import create_engine

engine = create_engine("jdbcapi+mysql://user:password@localhost:3306/mydb")
```

### SQL Server Example

```python
from sqlalchemy import create_engine

engine = create_engine("jdbcapi+mssql://user:password@localhost:1433/mydb")
```

### Oracle Example

```python
from sqlalchemy import create_engine

engine = create_engine("jdbcapi+oracle://user:password@localhost:1521/service_name")
```

## Quick Start with ODBC

ODBC requires that you install the appropriate ODBC driver for your database first.

### PostgreSQL with ODBC

```python
from sqlalchemy import create_engine

# Requires PostgreSQL ODBC driver installed
engine = create_engine("odbcapi+postgresql://user:password@localhost:5432/mydb")
```

### MySQL with ODBC

```python
from sqlalchemy import create_engine

# Requires MySQL ODBC driver installed
engine = create_engine("odbcapi+mysql://user:password@localhost:3306/mydb")
```

## Using SQLAlchemy ORM

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100))

# Create engine
engine = create_engine("jdbcapi+postgresql://user:password@localhost/mydb")

# Create tables
Base.metadata.create_all(engine)

# Use ORM
with Session(engine) as session:
    # Create
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    session.commit()

    # Query
    users = session.query(User).filter_by(name="Alice").all()
    print(users[0].email)
```

## Table Reflection

```python
from sqlalchemy import create_engine, MetaData, Table

engine = create_engine("jdbcapi+postgresql://user:password@localhost/mydb")
metadata = MetaData()

# Automatically load table structure
users_table = Table("users", metadata, autoload_with=engine)

# Access column information
for column in users_table.columns:
    print(f"{column.name}: {column.type}")
```

## Manual Driver Configuration (Advanced)

If you prefer to manage JDBC drivers manually:

```bash
# Download JDBC driver JAR manually
# Set CLASSPATH environment variable
export CLASSPATH="/path/to/postgresql-42.7.1.jar"
```

```python
from sqlalchemy import create_engine

# Disable auto-download
engine = create_engine(
    "jdbcapi+postgresql://user:password@localhost/mydb",
    connect_args={"auto_download": False}
)
```

## Connection String Format

### JDBC Connection Strings

```
jdbcapi+{database}://{user}:{password}@{host}:{port}/{database_name}
```

Supported databases:
- `jdbcapi+postgresql://` - PostgreSQL
- `jdbcapi+mysql://` - MySQL
- `jdbcapi+mariadb://` - MariaDB
- `jdbcapi+mssql://` - SQL Server
- `jdbcapi+oracle://` - Oracle
- `jdbcapi+db2://` - IBM DB2
- `jdbcapi+sqlite:///` - SQLite
- `jdbcapi+oceanbase://` - OceanBase

### ODBC Connection Strings

```
odbcapi+{database}://{user}:{password}@{host}:{port}/{database_name}
```

Supported databases:
- `odbcapi+postgresql://` - PostgreSQL
- `odbcapi+mysql://` - MySQL
- `odbcapi+mariadb://` - MariaDB
- `odbcapi+mssql://` - SQL Server
- `odbcapi+oracle://` - Oracle

## Common Issues

### JVM Not Found (JDBC)

If you see "JVM not found" error:

```bash
# On Ubuntu/Debian
sudo apt-get install default-jdk

# On macOS
brew install openjdk@11

# On Windows
# Download and install JDK from Oracle or AdoptOpenJDK
```

### ODBC Driver Not Found

Install the appropriate ODBC driver for your database:

**PostgreSQL:**
```bash
# Ubuntu/Debian
sudo apt-get install odbc-postgresql

# macOS
brew install psqlodbc

# Windows
# Download from https://www.postgresql.org/ftp/odbc/versions/
```

**MySQL:**
```bash
# Ubuntu/Debian
sudo apt-get install libmyodbc

# Download from https://dev.mysql.com/downloads/connector/odbc/
```

**SQL Server:**
```bash
# Ubuntu/Debian
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get install msodbcsql18

# macOS
brew install msodbcsql18

# Download from https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

## Next Steps

- Read the [USAGE.md](USAGE.md) for detailed usage examples
- Check [README.md](README.md) for comprehensive documentation
- Review [SQLAlchemy documentation](https://docs.sqlalchemy.org/) for ORM features
- See examples in the `examples/` directory

## Getting Help

- **Documentation**: See [USAGE.md](USAGE.md) and [README.md](README.md)
- **Issues**: Report bugs at https://github.com/daneshpatel/sqlalchemy-jdbcapi/issues
- **SQLAlchemy Help**: https://docs.sqlalchemy.org/

## Performance Tips

1. **Use connection pooling** (enabled by default)
2. **Batch operations** when inserting multiple records
3. **Use prepared statements** (automatic with SQLAlchemy)
4. **Enable statement caching** (enabled by default)

```python
# Configure pool size
engine = create_engine(
    "jdbcapi+postgresql://user:password@localhost/mydb",
    pool_size=10,
    max_overflow=20
)
```

That's all you need to get started! For advanced features, check out [USAGE.md](USAGE.md).
