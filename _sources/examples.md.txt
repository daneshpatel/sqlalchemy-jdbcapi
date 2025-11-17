# Examples

This guide provides real-world examples of using SQLAlchemy JDBC/ODBC API.

## Basic Examples

See the [examples directory](https://github.com/daneshpatel/sqlalchemy-jdbcapi/tree/main/examples) for complete, runnable examples:

- **[basic_usage.py](https://github.com/daneshpatel/sqlalchemy-jdbcapi/blob/main/examples/basic_usage.py)** - 8 fundamental usage patterns (JDBC, ODBC, ORM, pooling, transactions)
- **[data_analysis.py](https://github.com/daneshpatel/sqlalchemy-jdbcapi/blob/main/examples/data_analysis.py)** - 8 data science examples (pandas, polars, ETL, analytics, streaming)

## Database-Specific Examples

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

## DataFrame Integration

### Pandas Integration

```python
from sqlalchemy import create_engine

engine = create_engine('jdbcapi+postgresql://user:pass@localhost/mydb')

# Using helper functions
from sqlalchemy_jdbcapi.jdbc.dataframe import cursor_to_pandas

with engine.connect() as conn:
    cursor = conn.connection.cursor()
    cursor.execute("SELECT * FROM large_table WHERE date > '2024-01-01'")

    # Convert to pandas
    df = cursor_to_pandas(cursor)
    print(df.describe())
    print(df.head())
```

### Polars Integration

```python
from sqlalchemy_jdbcapi.jdbc.dataframe import cursor_to_polars

with engine.connect() as conn:
    cursor = conn.connection.cursor()
    cursor.execute("SELECT * FROM users")

    # Convert to polars
    df = cursor_to_polars(cursor)
    print(df.head())
```

### Apache Arrow Integration

```python
from sqlalchemy_jdbcapi.jdbc.dataframe import cursor_to_arrow

with engine.connect() as conn:
    cursor = conn.connection.cursor()
    cursor.execute("SELECT * FROM users")

    # Convert to Arrow
    table = cursor_to_arrow(cursor)
    print(table.schema)
```

### Using Cursor Convenience Methods

```python
with engine.connect() as conn:
    cursor = conn.connection.cursor()
    cursor.execute("SELECT * FROM users")

    # Direct conversion
    df = cursor.to_pandas()    # pandas DataFrame
    df = cursor.to_polars()    # polars DataFrame
    table = cursor.to_arrow()  # Arrow Table
    dicts = cursor.to_dict()   # List of dictionaries
```

## Advanced Patterns

### ETL Pipeline

```python
from sqlalchemy import create_engine
import pandas as pd

# Source database
source_engine = create_engine('jdbcapi+postgresql://user:pass@source-host/source_db')

# Target database
target_engine = create_engine('jdbcapi+oracle://user:pass@target-host:1521/target_db')

# Extract
with source_engine.connect() as conn:
    cursor = conn.connection.cursor()
    cursor.execute("SELECT * FROM sales WHERE date = CURRENT_DATE")
    df = cursor.to_pandas()

# Transform
df['total'] = df['quantity'] * df['price']
df['date_processed'] = pd.Timestamp.now()

# Load
df.to_sql('sales_processed', target_engine, if_exists='append', index=False)
```

### Data Analysis Pipeline

```python
from sqlalchemy import create_engine
import polars as pl

engine = create_engine('jdbcapi+postgresql://user:pass@localhost/analytics_db')

# Fetch data efficiently
with engine.connect() as conn:
    cursor = conn.connection.cursor()
    cursor.execute("""
        SELECT product_id, category, price, quantity, sale_date
        FROM sales
        WHERE sale_date >= CURRENT_DATE - INTERVAL '90 days'
    """)

    # Use Polars for fast analytics
    df = cursor.to_polars()

    # Analyze
    summary = (
        df.group_by(['category'])
        .agg([
            pl.sum('quantity').alias('total_quantity'),
            pl.sum('price').alias('total_revenue'),
            pl.mean('price').alias('avg_price')
        ])
        .sort('total_revenue', descending=True)
    )

    print(summary)
```

### Connection Pooling with Context Managers

```python
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'jdbcapi+postgresql://user:pass@localhost/mydb',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600
)

# Multiple operations with pooled connections
def process_batch(batch_data):
    with engine.connect() as conn:
        with conn.begin():
            for item in batch_data:
                conn.execute(
                    text("INSERT INTO items (name, value) VALUES (:name, :value)"),
                    {"name": item['name'], "value": item['value']}
                )

# Process multiple batches
batches = [batch1, batch2, batch3]
for batch in batches:
    process_batch(batch)
```

## Configuration Examples

See the [examples/README.md](https://github.com/daneshpatel/sqlalchemy-jdbcapi/blob/main/examples/README.md) for:
- Configuration and setup
- Troubleshooting common issues
- Performance optimization
- Best practices

## Testing Examples

See the [tests directory](https://github.com/daneshpatel/sqlalchemy-jdbcapi/tree/main/tests) for:
- Unit test examples
- Integration test patterns
- Docker-based testing setup
- Mocking strategies

## See Also

- [Usage Guide](usage.md) - Comprehensive usage documentation
- [SQLAlchemy Integration](sqlalchemy_integration.md) - Advanced SQLAlchemy features
- [API Reference](api/index.md) - Detailed API documentation
