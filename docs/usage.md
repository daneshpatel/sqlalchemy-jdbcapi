# Usage Guide

Comprehensive guide for using sqlalchemy-jdbcapi with JDBC and ODBC connections.

## Table of Contents

- [Installation](#installation)
- [JDBC Support](#jdbc-support)
- [ODBC Support](#odbc-support)
- [Database-Specific Examples](#database-specific-examples)
- [Driver Management](#driver-management)
- [ORM Usage](#orm-usage)
- [Asyncio Support](#asyncio-support)
- [HikariCP Connection Pooling](#hikaricp-connection-pooling)
- [Database X-Ray Monitoring](#database-x-ray-monitoring)
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
| GBase 8s | com.gbasedbt | gbasedbt-jdbc | 3.5.1 |
| IBM iSeries | com.ibm.as400 | jt400 | 11.1 |
| MS Access | net.sf.ucanaccess | ucanaccess | 5.0.1 |
| Apache Phoenix | org.apache.phoenix | phoenix-client | 5.1.3 |
| Apache Calcite | org.apache.calcite.avatica | avatica-core | 1.23.0 |

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

## Asyncio Support

sqlalchemy-jdbcapi provides full asyncio support for both Core and ORM operations.

### Async Engine Creation

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Create async engine using the async dialect
engine = create_async_engine(
    "jdbcapi+postgresql+async://user:password@localhost:5432/mydb",
    echo=True
)

# Create async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

### Async Core Operations

```python
import asyncio
from sqlalchemy import text

async def main():
    async with engine.begin() as conn:
        # Execute query
        result = await conn.execute(text("SELECT * FROM users"))
        rows = result.fetchall()
        for row in rows:
            print(row)

asyncio.run(main())
```

### Async ORM Operations

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def get_users(session: AsyncSession):
    result = await session.execute(select(User))
    return result.scalars().all()

async def create_user(session: AsyncSession, username: str, email: str):
    user = User(username=username, email=email)
    session.add(user)
    await session.commit()
    return user

async def main():
    async with async_session() as session:
        # Create user
        user = await create_user(session, "alice", "alice@example.com")
        print(f"Created: {user.username}")

        # Get all users
        users = await get_users(session)
        for user in users:
            print(f"User: {user.username}")

asyncio.run(main())
```

### Supported Async Databases

| Database | Async Dialect |
|----------|---------------|
| PostgreSQL | `jdbcapi+postgresql+async` |
| MySQL | `jdbcapi+mysql+async` |
| Oracle | `jdbcapi+oracle+async` |
| SQL Server | `jdbcapi+mssql+async` |
| DB2 | `jdbcapi+db2+async` |
| SQLite | `jdbcapi+sqlite+async` |
| GBase 8s | `jdbcapi+gbase8s+async` |
| IBM iSeries | `jdbcapi+iseries+async` |
| MS Access | `jdbcapi+access+async` |
| Apache Avatica | `jdbcapi+avatica+async` |
| Apache Phoenix | `jdbcapi+phoenix+async` |
| Apache Calcite | `jdbcapi+calcite+async` |

## HikariCP Connection Pooling

HikariCP is a high-performance JDBC connection pool. sqlalchemy-jdbcapi provides native HikariCP integration.

### Basic Usage

```python
from sqlalchemy_jdbcapi.jdbc import HikariConfig, HikariConnectionPool

# Configure the pool
config = HikariConfig(
    jdbc_url="jdbc:postgresql://localhost:5432/mydb",
    username="user",
    password="password",
    maximum_pool_size=10,
    minimum_idle=5,
    connection_timeout=30000,  # 30 seconds
    idle_timeout=600000,       # 10 minutes
    max_lifetime=1800000       # 30 minutes
)

# Create connection pool
pool = HikariConnectionPool(config)

# Get a connection
connection = pool.get_connection()
try:
    # Use connection
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
finally:
    connection.close()  # Returns to pool

# Get pool statistics
stats = pool.pool_stats()
print(f"Active connections: {stats['active_connections']}")
print(f"Idle connections: {stats['idle_connections']}")
print(f"Total connections: {stats['total_connections']}")

# Close the pool when done
pool.close()
```

### Advanced Configuration

```python
config = HikariConfig(
    jdbc_url="jdbc:postgresql://localhost:5432/mydb",
    username="user",
    password="password",
    driver_class="org.postgresql.Driver",

    # Pool sizing
    maximum_pool_size=20,
    minimum_idle=10,  # Should equal max for fixed-size pool

    # Timeouts (milliseconds)
    connection_timeout=30000,
    idle_timeout=600000,
    max_lifetime=1800000,
    keepalive_time=300000,  # Must be < max_lifetime

    # Health checks
    connection_test_query="SELECT 1",
    validation_timeout=5000,

    # Initialization
    connection_init_sql="SET timezone='UTC'",
    transaction_isolation="TRANSACTION_READ_COMMITTED",

    # Pool name for monitoring
    pool_name="MyAppPool"
)
```

### Configuration Validation

HikariCP configuration is automatically validated to prevent runtime errors:

- `minimum_idle` cannot exceed `maximum_pool_size`
- `keepalive_time` must be less than `max_lifetime`
- `connection_timeout` must be at least 250ms
- `idle_timeout` must be at least 10000ms (10 seconds) if set

### Pool Management

```python
# Suspend pool (stop acquiring new connections)
pool.suspend_pool()

# Resume pool
pool.resume_pool()

# Check pool health
if pool.is_running():
    print("Pool is healthy")
```

## Database X-Ray Monitoring

X-Ray provides query monitoring, performance metrics, and tracing capabilities.

### Basic Monitoring

```python
from sqlalchemy_jdbcapi.xray import DatabaseMonitor

# Create monitor
monitor = DatabaseMonitor()

# Record a query
monitor.record_query(
    query="SELECT * FROM users WHERE id = ?",
    execution_time=0.025,  # 25ms
    rows_affected=1
)

# Get statistics for a query
stats = monitor.get_query_stats("SELECT * FROM users WHERE id = ?")
print(f"Total executions: {stats.count}")
print(f"Average time: {stats.avg_time:.3f}s")
print(f"Max time: {stats.max_time:.3f}s")
print(f"Total rows: {stats.total_rows}")

# Get all slow queries
slow_queries = monitor.get_slow_queries(threshold=0.1)  # > 100ms
for query, stats in slow_queries:
    print(f"Slow query: {query}")
    print(f"  Avg time: {stats.avg_time:.3f}s")
```

### Automatic Query Tracing

```python
from sqlalchemy_jdbcapi.xray import QueryTracer, TracedConnection

# Create a tracer
tracer = QueryTracer()

# Wrap your connection
traced_conn = TracedConnection(connection, tracer)

# Use traced connection normally - all queries are automatically recorded
cursor = traced_conn.cursor()
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

# Get the monitor from tracer
monitor = tracer.monitor

# View statistics
for query, stats in monitor.get_all_stats():
    print(f"{query}: {stats.count} executions, avg {stats.avg_time:.3f}s")
```

### Slow Query Callbacks

```python
def on_slow_query(query: str, execution_time: float):
    print(f"SLOW QUERY ALERT: {execution_time:.3f}s")
    print(f"Query: {query}")
    # Log to monitoring system, send alert, etc.

# Set up monitor with callback
monitor = DatabaseMonitor(
    slow_query_threshold=0.1,  # 100ms
    slow_query_callback=on_slow_query
)
```

### Memory Management

X-Ray includes automatic memory management to prevent unbounded growth:

```python
from sqlalchemy_jdbcapi.xray import XRayConfig, DatabaseMonitor

config = XRayConfig(
    slow_query_threshold=1.0,
    max_query_history=1000,      # Max queries in history
    max_query_patterns=500,      # Max unique query patterns to track
    log_queries=False,
    capture_parameters=False     # Disable for production
)

monitor = DatabaseMonitor(config)
```

The monitor automatically:
- Caps query history to prevent memory leaks
- Uses LRU eviction for query patterns exceeding the limit
- Uses reservoir sampling to maintain statistical accuracy with bounded memory

### Query Normalization

X-Ray automatically normalizes queries for better grouping:

```python
# These queries are grouped together:
# "SELECT * FROM users WHERE id = 1"
# "SELECT * FROM users WHERE id = 42"
# Both become: "SELECT * FROM users WHERE id = ?"

stats = monitor.get_query_stats("SELECT * FROM users WHERE id = ?")
```

### Export Metrics

```python
# Get all metrics as dictionary
all_stats = monitor.get_all_stats()

# Export to JSON
import json
metrics = {
    query: {
        "count": stats.count,
        "avg_time": stats.avg_time,
        "max_time": stats.max_time,
        "min_time": stats.min_time,
        "total_rows": stats.total_rows
    }
    for query, stats in all_stats
}
print(json.dumps(metrics, indent=2))
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
