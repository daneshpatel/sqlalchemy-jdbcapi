# SQLAlchemy JDBCAPI - Usage Examples

This directory contains comprehensive examples demonstrating how to use sqlalchemy-jdbcapi in various scenarios.

## 📁 Files

### basic_usage.py
Demonstrates fundamental usage patterns:
- JDBC with automatic driver download from Maven Central
- JDBC with manual driver path configuration
- ODBC connections with system drivers
- SQLAlchemy ORM operations (CRUD)
- Supporting multiple databases
- Connection pooling configuration
- Transaction management
- Custom ODBC parameters

### data_analysis.py
Shows integration with data science tools:
- Pandas integration for data analysis
- Polars integration for fast dataframes
- ETL pipeline across multiple databases
- Complex analytics with window functions
- Batch processing with chunking
- Real-time data streaming
- Data validation and quality checks
- Exporting to multiple formats (CSV, Excel, JSON, Parquet)

## 🚀 Quick Start

### Prerequisites

```bash
# Install base package
pip install sqlalchemy-jdbcapi

# For ODBC support
pip install 'sqlalchemy-jdbcapi[odbc]'

# For data analysis examples
pip install 'sqlalchemy-jdbcapi[dataframe]'
```

### Running Examples

**Note**: These examples require actual database connections. You'll need to:

1. Update connection URLs with your database credentials
2. Ensure databases are running and accessible
3. Install required JDBC/ODBC drivers

```bash
# Run basic examples (displays concepts - requires database for actual execution)
python examples/basic_usage.py

# Run data analysis examples
python examples/data_analysis.py
```

## 📖 Example Categories

### 1. JDBC Connections

#### Auto-Download (Recommended)
```python
from sqlalchemy import create_engine

# Driver is automatically downloaded from Maven Central
engine = create_engine(
    "jdbcapi+postgresql://user:password@localhost:5432/mydb"
)
```

#### Manual Driver Path
```python
import os

# Set CLASSPATH with your JDBC driver
os.environ["CLASSPATH"] = "/path/to/postgresql-42.7.1.jar"

engine = create_engine(
    "jdbcapi+postgresql://user:password@localhost:5432/mydb"
)
```

### 2. ODBC Connections

```python
# Requires: pip install 'sqlalchemy-jdbcapi[odbc]'
engine = create_engine(
    "odbcapi+postgresql://user:password@localhost:5432/mydb"
)
```

### 3. ORM Usage

```python
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    # ... column definitions

# Create tables
Base.metadata.create_all(engine)

# Use ORM
with Session(engine) as session:
    user = User(username="alice", email="alice@example.com")
    session.add(user)
    session.commit()
```

### 4. Data Analysis

```python
import pandas as pd

# Read SQL into DataFrame
df = pd.read_sql_query(
    "SELECT * FROM users",
    engine
)

# Write DataFrame to database
df.to_sql("users_backup", engine, if_exists="replace")
```

## 🗄️ Supported Databases

### JDBC Support
- PostgreSQL
- MySQL / MariaDB
- Oracle Database
- SQL Server / Azure SQL
- IBM DB2
- SQLite
- OceanBase

### ODBC Support
- PostgreSQL
- MySQL / MariaDB
- SQL Server / Azure SQL
- Oracle Database

## 🔧 Configuration Examples

### Connection Pooling

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "jdbcapi+postgresql://user:password@localhost:5432/mydb",
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
)
```

### Transaction Management

```python
# Automatic commit
with engine.begin() as conn:
    conn.execute(text("INSERT INTO users ..."))
    # Commits automatically on successful exit

# Manual control
with Session(engine) as session:
    try:
        session.add(user)
        session.commit()
    except Exception:
        session.rollback()
        raise
```

## 📊 Data Pipeline Example

```python
# Extract from PostgreSQL
source_engine = create_engine("jdbcapi+postgresql://...")
df = pd.read_sql_query("SELECT * FROM users", source_engine)

# Transform
df["email_domain"] = df["email"].str.split("@").str[1]

# Load into MySQL
target_engine = create_engine("jdbcapi+mysql://...")
df.to_sql("users_etl", target_engine, if_exists="replace")
```

## 🧪 Testing

Examples include skip markers for tests requiring real databases:

```python
@pytest.mark.functional
def test_with_real_database():
    pytest.skip("Requires real database - manual test only")
    # ... test code
```

## 📝 Notes

- **JDBC drivers** are automatically downloaded from Maven Central on first use
- **ODBC drivers** must be installed on your system
- Connection URLs follow SQLAlchemy's standard URL format
- All examples use context managers for proper resource cleanup

## 🔗 Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [JDBC Driver Documentation](../DRIVERS.md)
- [Quick Start Guide](../QUICKSTART.md)
- [Full Usage Guide](../USAGE.md)

## 💡 Tips

1. **Start with SQLite** for testing - it requires no external database
2. **Use auto-download** for JDBC - it's the easiest way to get started
3. **Enable `echo=True`** during development to see generated SQL
4. **Use connection pooling** for production applications
5. **Batch operations** when processing large datasets
6. **Test with small datasets** before scaling up

## 🆘 Troubleshooting

### JDBC Driver Not Found
```python
# Ensure auto-download is enabled (default)
engine = create_engine(url)  # Auto-downloads on first connect

# Or set CLASSPATH manually
os.environ["CLASSPATH"] = "/path/to/driver.jar"
```

### ODBC Driver Not Found
```bash
# Install system ODBC drivers
# Ubuntu/Debian:
sudo apt-get install odbc-postgresql

# macOS:
brew install psqlodbc

# Windows: Download from vendor website
```

### JVM Already Started Error
```python
# JVM can only be started once per Python process
# Restart Python interpreter if you need different JVM settings
```

## 📄 License

These examples are provided under the same Apache 2.0 license as the main package.
