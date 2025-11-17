# SQLAlchemy Integration Guide

SQLAlchemy JDBC/ODBC API 2.0 provides **complete SQLAlchemy native dialect integration** with full ORM, reflection, and Inspector API support.

## Features

- ✅ **ORM Support** - Full declarative models with relationships
- ✅ **Table Reflection** - Auto-load existing table structures
- ✅ **Database Inspector** - Explore schema programmatically
- ✅ **ORM Automapping** - Auto-generate models from existing databases
- ✅ **Alembic Migrations** - Database schema version control
- ✅ **Cross-Database Migration** - Copy schemas between different database systems

## ORM Support

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

## Table Reflection & Auto-load

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

## Database Inspector

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

## ORM Automapping

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

## Alembic Migrations

Full support for Alembic database migrations:

### Initialize Alembic

```bash
# Initialize Alembic
alembic init migrations

# Configure alembic.ini
# Set: sqlalchemy.url = jdbcapi+postgresql://user:pass@localhost:5432/mydb
```

### Create Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add user and post tables"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Example Migration

```python
"""Add user and post tables

Revision ID: 001
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('users')
```

## Cross-Database Schema Migration

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

## Reflection Implementation

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

## Connection Pooling

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

## Transaction Management

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

## Batch Operations

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

## Type Hints Support

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

## See Also

- [Usage Guide](usage.md) - Comprehensive usage examples
- [API Reference](api/index.md) - Detailed API documentation
- [Examples](examples.md) - Real-world use cases
