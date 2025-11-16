"""
Basic usage examples for sqlalchemy-jdbcapi.

This demonstrates the most common usage patterns for JDBC and ODBC connections.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session, mapped_column

# ==============================================================================
# Example 1: JDBC with Auto-Download (Recommended)
# ==============================================================================

def example_jdbc_auto_download():
    """Example using JDBC with automatic driver download."""
    print("=" * 70)
    print("Example 1: JDBC with Auto-Download")
    print("=" * 70)

    # Create engine - driver will be auto-downloaded from Maven Central
    engine = create_engine(
        "jdbcapi+postgresql://user:password@localhost:5432/mydb",
        echo=True,  # Print SQL queries
    )

    # The first connection will:
    # 1. Start JVM if needed
    # 2. Download PostgreSQL JDBC driver from Maven Central
    # 3. Cache driver in ~/.sqlalchemy-jdbcapi/drivers/
    # 4. Establish connection

    with engine.connect() as conn:
        result = conn.execute(select(1))
        print(f"Connected! Result: {result.scalar()}")

    print("\n✓ JDBC with auto-download successful!\n")


# ==============================================================================
# Example 2: JDBC with Manual Driver Path
# ==============================================================================

def example_jdbc_manual_driver():
    """Example using JDBC with manually provided driver."""
    print("=" * 70)
    print("Example 2: JDBC with Manual Driver Path")
    print("=" * 70)

    import os

    # Set CLASSPATH environment variable
    os.environ["CLASSPATH"] = "/path/to/postgresql-42.7.1.jar"

    # Or use JDBC_DRIVER_PATH
    # os.environ["JDBC_DRIVER_PATH"] = "/path/to/postgresql-42.7.1.jar"

    engine = create_engine(
        "jdbcapi+postgresql://user:password@localhost:5432/mydb"
    )

    # Will use driver from CLASSPATH instead of auto-downloading

    print("\n✓ JDBC with manual driver path configured!\n")


# ==============================================================================
# Example 3: ODBC Connection
# ==============================================================================

def example_odbc_connection():
    """Example using ODBC connection."""
    print("=" * 70)
    print("Example 3: ODBC Connection")
    print("=" * 70)

    # Requires: pip install 'sqlalchemy-jdbcapi[odbc]'
    # And ODBC driver installed on system

    engine = create_engine(
        "odbcapi+postgresql://user:password@localhost:5432/mydb"
    )

    # Will use system ODBC drivers (e.g., psqlODBC)
    # Connection string is automatically built from URL

    with engine.connect() as conn:
        result = conn.execute(select(1))
        print(f"Connected via ODBC! Result: {result.scalar()}")

    print("\n✓ ODBC connection successful!\n")


# ==============================================================================
# Example 4: SQLAlchemy ORM Usage
# ==============================================================================

class Base(DeclarativeBase):
    """Base class for ORM models."""

    pass


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True)
    username = mapped_column(String(50), unique=True, nullable=False)
    email = mapped_column(String(100), nullable=False)
    created_at = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User(username='{self.username}')>"


def example_orm_usage():
    """Example using SQLAlchemy ORM."""
    print("=" * 70)
    print("Example 4: SQLAlchemy ORM Usage")
    print("=" * 70)

    # Create engine
    engine = create_engine(
        "jdbcapi+postgresql://user:password@localhost:5432/mydb",
        echo=True,
    )

    # Create tables
    Base.metadata.create_all(engine)

    # Create session
    with Session(engine) as session:
        # INSERT
        new_user = User(
            username="alice",
            email="alice@example.com",
        )
        session.add(new_user)
        session.commit()

        print(f"\n✓ Created user: {new_user}")

        # SELECT
        user = session.execute(
            select(User).filter_by(username="alice")
        ).scalar_one()

        print(f"✓ Retrieved user: {user}")

        # UPDATE
        user.email = "alice.updated@example.com"
        session.commit()

        print(f"✓ Updated user email: {user.email}")

        # DELETE
        session.delete(user)
        session.commit()

        print("✓ Deleted user")

    print("\n✓ ORM operations successful!\n")


# ==============================================================================
# Example 5: Multiple Database Support
# ==============================================================================

def example_multiple_databases():
    """Example supporting multiple databases."""
    print("=" * 70)
    print("Example 5: Multiple Database Support")
    print("=" * 70)

    databases = {
        "postgresql": "jdbcapi+postgresql://user:pass@localhost:5432/db",
        "mysql": "jdbcapi+mysql://user:pass@localhost:3306/db",
        "oracle": "jdbcapi+oracle://user:pass@localhost:1521/db",
        "mssql": "jdbcapi+mssql://user:pass@localhost:1433/db",
        "db2": "jdbcapi+db2://user:pass@localhost:50000/db",
        "sqlite": "jdbcapi+sqlite:///path/to/database.db",
    }

    for db_name, url in databases.items():
        print(f"\n{db_name}: {url}")

        # Each database's driver will be auto-downloaded on first use
        # engine = create_engine(url)
        # with engine.connect() as conn:
        #     result = conn.execute(select(1))

    print("\n✓ All database URLs configured!\n")


# ==============================================================================
# Example 6: Connection Pooling and Performance
# ==============================================================================

def example_connection_pooling():
    """Example with connection pooling configuration."""
    print("=" * 70)
    print("Example 6: Connection Pooling")
    print("=" * 70)

    from sqlalchemy.pool import QueuePool

    engine = create_engine(
        "jdbcapi+postgresql://user:password@localhost:5432/mydb",
        poolclass=QueuePool,
        pool_size=10,  # Number of connections to maintain
        max_overflow=20,  # Additional connections when needed
        pool_timeout=30,  # Timeout for getting connection from pool
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo_pool=True,  # Log pool checkouts/checkins
    )

    print("✓ Connection pool configured:")
    print(f"  - Pool size: 10")
    print(f"  - Max overflow: 20")
    print(f"  - Pool timeout: 30s")
    print(f"  - Connection recycle: 3600s")

    print("\n✓ Connection pooling configured!\n")


# ==============================================================================
# Example 7: Transaction Management
# ==============================================================================

def example_transaction_management():
    """Example with explicit transaction management."""
    print("=" * 70)
    print("Example 7: Transaction Management")
    print("=" * 70)

    engine = create_engine(
        "jdbcapi+postgresql://user:password@localhost:5432/mydb"
    )

    # Automatic transaction management
    with engine.begin() as conn:
        conn.execute(
            select(User.__table__).filter_by(username="alice")
        )
        # Transaction commits automatically on successful exit

    # Manual transaction control
    with Session(engine) as session:
        try:
            user = User(username="bob", email="bob@example.com")
            session.add(user)

            # Explicit commit
            session.commit()

        except Exception as e:
            # Explicit rollback
            session.rollback()
            print(f"Transaction rolled back: {e}")
            raise

    print("\n✓ Transaction management examples shown!\n")


# ==============================================================================
# Example 8: ODBC with Custom Connection String
# ==============================================================================

def example_odbc_custom():
    """Example using ODBC with custom connection parameters."""
    print("=" * 70)
    print("Example 8: ODBC Custom Parameters")
    print("=" * 70)

    # Pass additional ODBC parameters via query string
    engine = create_engine(
        "odbcapi+postgresql://user:password@localhost:5432/mydb"
        "?driver=PostgreSQL Unicode"
        "&sslmode=require"
        "&connect_timeout=10"
    )

    print("✓ ODBC engine with custom parameters:")
    print("  - Driver: PostgreSQL Unicode")
    print("  - SSL Mode: require")
    print("  - Connect Timeout: 10s")

    print("\n✓ ODBC custom configuration shown!\n")


# ==============================================================================
# Main - Run Examples
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SQLAlchemy JDBCAPI - Usage Examples")
    print("=" * 70 + "\n")

    # Note: These examples require actual database instances to run
    # They are shown here for documentation purposes

    examples = [
        ("JDBC Auto-Download", example_jdbc_auto_download),
        ("JDBC Manual Driver", example_jdbc_manual_driver),
        ("ODBC Connection", example_odbc_connection),
        ("ORM Usage", example_orm_usage),
        ("Multiple Databases", example_multiple_databases),
        ("Connection Pooling", example_connection_pooling),
        ("Transaction Management", example_transaction_management),
        ("ODBC Custom", example_odbc_custom),
    ]

    for name, example_func in examples:
        try:
            # example_func()  # Uncomment to run with real database
            print(f"Example: {name} (Requires real database - skipped)")
            print()
        except Exception as e:
            print(f"\n⚠ Example {name} failed: {e}\n")

    print("=" * 70)
    print("All examples shown!")
    print("=" * 70)
    print("\nTo run these examples:")
    print("1. Install: pip install sqlalchemy-jdbcapi")
    print("2. For ODBC: pip install 'sqlalchemy-jdbcapi[odbc]'")
    print("3. Configure database connection URLs")
    print("4. Run: python examples/basic_usage.py")
    print("=" * 70 + "\n")
