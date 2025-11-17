# Usage Guide

Comprehensive guide for using sqlalchemy-jdbcapi with JDBC and ODBC connections.

## Table of Contents

- [Installation](#installation)
- [JDBC Support](#jdbc-support)
- [ODBC Support](#odbc-support)
- [Database-Specific Examples](#database-specific-examples)
- [Driver Management](#driver-management)
- [ORM Usage](#orm-usage)
- [Advanced Features](#advanced-features)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)

## Installation

### Basic Installation

```bash
pip install sqlalchemy-jdbcapi
```

### With Optional Dependencies

```bash
# With DataFrame support (pandas, polars, pyarrow)
pip install sqlalchemy-jdbcapi[dataframe]

# With development tools
pip install sqlalchemy-jdbcapi[dev]

# With documentation tools
pip install sqlalchemy-jdbcapi[docs]

# With everything
pip install sqlalchemy-jdbcapi[all]
```

### System Requirements

- **Python**: 3.10, 3.11, 3.12, or 3.13
- **SQLAlchemy**: 2.0.0 or higher
- **Java Runtime**: JDK 8+ (for JDBC support)
- **JPype1**: 1.5.0+ (installed automatically)
- **pyodbc**: 5.0.0+ (for ODBC support, optional)

## JDBC Support

### Overview

JDBC (Java Database Connectivity) support provides access to databases through Java JDBC drivers.

**Advantages:**
- Automatic driver download from Maven Central
- Wide database compatibility
- Mature driver ecosystem
- Official vendor support

**Supported Databases:**
- PostgreSQL 9.6+
- MySQL 5.7+
- MariaDB 10.3+
- Oracle 11g+
- SQL Server 2012+
- IBM DB2 11.5+
- SQLite 3+
- OceanBase 2.4+

### Automatic Driver Download

By default, JDBC drivers are automatically downloaded on first use:

```python
from sqlalchemy import create_engine

# Driver auto-downloads from Maven Central
engine = create_engine("jdbcapi+postgresql://localhost/mydb")
```

Drivers are cached in `~/.sqlalchemy-jdbcapi/drivers/` for reuse.

### Manual Driver Management

#### Environment Variable Method

```bash
# Set CLASSPATH with your JDBC drivers
export CLASSPATH="/path/to/postgresql-42.7.1.jar:/path/to/mysql-connector-j-8.3.0.jar"
```

```python
from sqlalchemy import create_engine

# Will use drivers from CLASSPATH
engine = create_engine("jdbcapi+postgresql://localhost/mydb")
```

#### Programmatic Method

```python
from sqlalchemy_jdbcapi import jdbc

# Download specific driver version
driver = jdbc.JDBCDriver(
    group_id="org.postgresql",
    artifact_id="postgresql",
    version="42.7.1"
)
path = jdbc.download_driver(driver)

# Or get driver path (downloads if needed)
path = jdbc.get_driver_path("postgresql")
```

#### List Cached Drivers

```python
from sqlalchemy_jdbcapi import jdbc

# List all cached drivers
cached_drivers = jdbc.list_cached_drivers()
for driver_path in cached_drivers:
    print(driver_path)

# Clear cache
count = jdbc.clear_driver_cache()
print(f"Deleted {count} drivers")
```

### JDBC Connection Examples

#### PostgreSQL

```python
from sqlalchemy import create_engine, text

engine = create_engine(
    "jdbcapi+postgresql://user:password@localhost:5432/mydb",
    echo=True  # Log SQL statements
)

with engine.connect() as conn:
    result = conn.execute(text("SELECT current_database()"))
    print(result.scalar())
```

#### MySQL

```python
engine = create_engine(
    "jdbcapi+mysql://user:password@localhost:3306/mydb",
    connect_args={
        "useSSL": "false",
        "serverTimezone": "UTC"
    }
)
```

#### SQL Server

```python
engine = create_engine(
    "jdbcapi+mssql://user:password@localhost:1433/mydb",
    connect_args={
        "encrypt": "true",
        "trustServerCertificate": "true"
    }
)
```

#### Oracle

```python
# Using service name
engine = create_engine(
    "jdbcapi+oracle://user:password@localhost:1521/SERVICE_NAME"
)

# Using SID
engine = create_engine(
    "jdbcapi+oracle://user:password@localhost:1521/ORCL"
)
```

## ODBC Support

### Overview

ODBC (Open Database Connectivity) provides an alternative connection method using native ODBC drivers.

**Advantages:**
- Native OS integration
- No JVM required
- Direct driver support
- Better performance for some operations

**Requirements:**
- Install `pyodbc`: `pip install pyodbc`
- Install appropriate ODBC driver for your database

### Installing ODBC Drivers

#### PostgreSQL ODBC

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install odbc-postgresql unixodbc
```

**macOS:**
```bash
brew install psqlodbc unixodbc
```

**Windows:**
Download from https://www.postgresql.org/ftp/odbc/versions/

#### MySQL ODBC

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libmyodbc unixodbc
```

**macOS:**
```bash
brew install mysql-connector-odbc
```

**Windows:**
Download from https://dev.mysql.com/downloads/connector/odbc/

#### SQL Server ODBC

**Linux (Ubuntu/Debian):**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get install msodbcsql18 unixodbc-dev
```

**macOS:**
```bash
brew tap microsoft/mssql-release
brew install msodbcsql18
```

**Windows:**
Download from https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### ODBC Connection Examples

#### PostgreSQL

```python
from sqlalchemy import create_engine

engine = create_engine(
    "odbcapi+postgresql://user:password@localhost:5432/mydb"
)
```

#### MySQL

```python
engine = create_engine(
    "odbcapi+mysql://user:password@localhost:3306/mydb"
)
```

#### SQL Server

```python
engine = create_engine(
    "odbcapi+mssql://user:password@localhost:1433/mydb"
)
```

## Database-Specific Examples

### PostgreSQL Features

```python
from sqlalchemy import create_engine, Table, Column, Integer, String, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True)
    title = Column(String(200))
    tags = Column(ARRAY(String))  # PostgreSQL array type
    metadata = Column(JSONB)  # PostgreSQL JSONB type

engine = create_engine("jdbcapi+postgresql://localhost/mydb")
Base.metadata.create_all(engine)
```

### MySQL AUTO_INCREMENT

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    sku = Column(String(50))

engine = create_engine("jdbcapi+mysql://localhost/mydb")
Base.metadata.create_all(engine)
```

### SQL Server Identity Columns

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(100))

engine = create_engine("jdbcapi+mssql://localhost/mydb")
Base.metadata.create_all(engine)
```

### Oracle Sequences

```python
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, Sequence("employee_id_seq"), primary_key=True)
    name = Column(String(100))

engine = create_engine("jdbcapi+oracle://localhost/SERVICE_NAME")
Base.metadata.create_all(engine)
```

## Driver Management

### Supported JDBC Drivers

| Database | Group ID | Artifact ID | Recommended Version |
|----------|----------|-------------|---------------------|
| PostgreSQL | org.postgresql | postgresql | 42.7.1 |
| MySQL | com.mysql | mysql-connector-j | 8.3.0 |
| MariaDB | org.mariadb.jdbc | mariadb-java-client | 3.3.2 |
| SQL Server | com.microsoft.sqlserver | mssql-jdbc | 12.6.0.jre11 |
| Oracle | com.oracle.database.jdbc | ojdbc11 | 23.3.0.23.09 |
| IBM DB2 | com.ibm.db2 | jcc | 11.5.9.0 |
| SQLite | org.xerial | sqlite-jdbc | 3.45.0.0 |
| OceanBase | com.oceanbase | oceanbase-client | 2.4.9 |

### Custom Driver Download

```python
from sqlalchemy_jdbcapi.jdbc import JDBCDriver, download_driver

# Define custom driver
custom_driver = JDBCDriver(
    group_id="org.postgresql",
    artifact_id="postgresql",
    version="42.6.0"  # Specific version
)

# Download driver
driver_path = download_driver(custom_driver)
print(f"Driver downloaded to: {driver_path}")
```

### Configure Cache Directory

```bash
# Set custom cache directory
export SQLALCHEMY_JDBCAPI_DRIVER_CACHE="/custom/path/drivers"
```

```python
from sqlalchemy_jdbcapi.jdbc import get_driver_path
from pathlib import Path

# Use custom cache directory
driver_path = get_driver_path(
    "postgresql",
    cache_dir=Path("/custom/path/drivers")
)
```

## ORM Usage

### Define Models

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Session
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(String(5000))
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    author = relationship("User", back_populates="posts")

# Create tables
engine = create_engine("jdbcapi+postgresql://localhost/mydb")
Base.metadata.create_all(engine)
```

### CRUD Operations

```python
from sqlalchemy.orm import Session

# Create
with Session(engine) as session:
    user = User(username="alice", email="alice@example.com")
    session.add(user)
    session.commit()
    print(f"Created user ID: {user.id}")

# Read
with Session(engine) as session:
    user = session.query(User).filter_by(username="alice").first()
    print(f"Found user: {user.email}")

# Update
with Session(engine) as session:
    user = session.query(User).filter_by(username="alice").first()
    user.email = "alice.updated@example.com"
    session.commit()

# Delete
with Session(engine) as session:
    user = session.query(User).filter_by(username="alice").first()
    session.delete(user)
    session.commit()
```

### Relationships

```python
from sqlalchemy.orm import Session

with Session(engine) as session:
    # Create user with posts
    user = User(username="bob", email="bob@example.com")
    user.posts = [
        Post(title="First Post", content="Hello World!"),
        Post(title="Second Post", content="SQLAlchemy is great!")
    ]
    session.add(user)
    session.commit()

    # Query with joins
    result = session.query(User).join(User.posts).filter(Post.title == "First Post").first()
    print(f"Author: {result.username}")
    for post in result.posts:
        print(f"  - {post.title}")
```

## Advanced Features

### Table Reflection

```python
from sqlalchemy import create_engine, MetaData, Table, inspect

engine = create_engine("jdbcapi+postgresql://localhost/mydb")

# Reflect specific table
metadata = MetaData()
users_table = Table("users", metadata, autoload_with=engine)

# Access columns
for column in users_table.columns:
    print(f"{column.name}: {column.type}")

# Inspect database
inspector = inspect(engine)

# List all tables
tables = inspector.get_table_names()
print(f"Tables: {tables}")

# Get primary keys
pk = inspector.get_pk_constraint("users")
print(f"Primary key: {pk}")

# Get foreign keys
fks = inspector.get_foreign_keys("posts")
for fk in fks:
    print(f"Foreign key: {fk}")
```

### Transactions

```python
from sqlalchemy import create_engine, text

engine = create_engine("jdbcapi+postgresql://localhost/mydb")

# Explicit transaction
with engine.begin() as conn:
    conn.execute(text("INSERT INTO users (username) VALUES ('alice')"))
    conn.execute(text("INSERT INTO users (username) VALUES ('bob')"))
    # Automatically commits on exit

# Manual transaction control
with engine.connect() as conn:
    trans = conn.begin()
    try:
        conn.execute(text("INSERT INTO users (username) VALUES ('charlie')"))
        trans.commit()
    except:
        trans.rollback()
        raise
```

### Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "jdbcapi+postgresql://localhost/mydb",
    poolclass=QueuePool,
    pool_size=10,  # Number of connections to maintain
    max_overflow=20,  # Maximum overflow connections
    pool_timeout=30,  # Timeout for getting connection from pool
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Test connections before using
)
```

### DataFrame Integration

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("jdbcapi+postgresql://localhost/mydb")

# Write DataFrame to database
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "city": ["New York", "London", "Paris"]
})
df.to_sql("people", engine, if_exists="replace", index=False)

# Read from database to DataFrame
df_read = pd.read_sql("SELECT * FROM people WHERE age > 25", engine)
print(df_read)

# Read with SQLAlchemy query
df_read = pd.read_sql_query(
    "SELECT name, age FROM people ORDER BY age DESC",
    engine
)
```

## Performance Optimization

### Batch Operations

```python
from sqlalchemy.orm import Session

users = [
    User(username=f"user{i}", email=f"user{i}@example.com")
    for i in range(1000)
]

with Session(engine) as session:
    session.bulk_save_objects(users)
    session.commit()
```

### Prepared Statements

```python
from sqlalchemy import create_engine, text

engine = create_engine("jdbcapi+postgresql://localhost/mydb")

# Prepared statement (automatic with SQLAlchemy)
stmt = text("SELECT * FROM users WHERE age > :min_age")

with engine.connect() as conn:
    result = conn.execute(stmt, {"min_age": 25})
    for row in result:
        print(row)
```

### Query Optimization

```python
from sqlalchemy.orm import Session, joinedload

# Eager loading to avoid N+1 queries
with Session(engine) as session:
    users = session.query(User).options(joinedload(User.posts)).all()
    for user in users:
        print(f"{user.username}: {len(user.posts)} posts")
```

## Troubleshooting

### Common Issues and Solutions

#### 1. JVM Not Found (JDBC)

**Error:**
```
JVMNotStartedError: Failed to start JVM
```

**Solution:**
```bash
# Install Java
sudo apt-get install default-jdk  # Linux
brew install openjdk@11  # macOS

# Set JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/default-java
```

#### 2. Driver Not Found

**Error:**
```
RuntimeError: JDBC driver not found
```

**Solution:**
```python
# Enable auto-download
engine = create_engine("jdbcapi+postgresql://localhost/mydb")

# Or set CLASSPATH
# export CLASSPATH="/path/to/driver.jar"
```

#### 3. Connection Timeout

**Error:**
```
OperationalError: Connection timed out
```

**Solution:**
```python
engine = create_engine(
    "jdbcapi+postgresql://localhost/mydb",
    connect_args={"timeout": 60}  # Increase timeout
)
```

#### 4. ODBC Driver Not Configured

**Error:**
```
pyodbc.Error: Driver not found
```

**Solution:**
```bash
# List available ODBC drivers
odbcinst -q -d

# Install missing driver (see ODBC Support section)
```

### Enable Debug Logging

```python
import logging

# Enable SQLAlchemy logging
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Enable jdbcapi logging
logging.getLogger("sqlalchemy_jdbcapi").setLevel(logging.DEBUG)

# Create engine with echo
engine = create_engine(
    "jdbcapi+postgresql://localhost/mydb",
    echo=True  # Log all SQL statements
)
```

### Check Driver Cache

```python
from sqlalchemy_jdbcapi.jdbc import list_cached_drivers, get_driver_cache_dir

cache_dir = get_driver_cache_dir()
print(f"Cache directory: {cache_dir}")

drivers = list_cached_drivers()
print(f"Cached drivers: {len(drivers)}")
for driver in drivers:
    print(f"  - {driver.name}")
```

## Additional Resources

- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Project Repository**: https://github.com/daneshpatel/sqlalchemy-jdbcapi
- **Issue Tracker**: https://github.com/daneshpatel/sqlalchemy-jdbcapi/issues
- **Quick Start Guide**: [QUICKSTART.md](QUICKSTART.md)
- **README**: [README.md](README.md)

## Support

For questions, issues, or feature requests:

1. Check the [QUICKSTART.md](QUICKSTART.md) guide
2. Review [Troubleshooting](#troubleshooting) section
3. Search existing [issues](https://github.com/daneshpatel/sqlalchemy-jdbcapi/issues)
4. Create a new issue with detailed information

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
