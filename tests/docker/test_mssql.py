"""
Functional tests for Microsoft SQL Server using Docker container.
"""

from __future__ import annotations

import pytest
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    select,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


@pytest.mark.docker
class TestMSSQLConnection:
    """Test SQL Server connection via JDBC."""

    def test_basic_connection(self, mssql_engine):
        """Test basic connection to SQL Server."""
        with mssql_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

    def test_version_query(self, mssql_engine):
        """Test querying SQL Server version."""
        with mssql_engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION"))
            version = result.fetchone()[0]
            assert "Microsoft SQL Server" in version

    def test_create_table(self, mssql_engine):
        """Test creating a table in SQL Server."""
        metadata = MetaData()

        Table(
            "mssql_test_users",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("name", String(100)),
            Column("email", String(255)),
        )

        try:
            metadata.create_all(mssql_engine)

            # Verify table exists
            with mssql_engine.connect() as conn:
                result = conn.execute(
                    text(
                        "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
                        "WHERE TABLE_NAME = 'mssql_test_users'"
                    )
                )
                assert result.fetchone() is not None
        finally:
            metadata.drop_all(mssql_engine)

    def test_insert_and_select(self, mssql_engine):
        """Test inserting and selecting data."""
        metadata = MetaData()

        users = Table(
            "mssql_insert_users",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("name", String(100)),
        )

        try:
            metadata.create_all(mssql_engine)

            with mssql_engine.connect() as conn:
                # Insert data
                conn.execute(users.insert().values(name="Alice"))
                conn.execute(users.insert().values(name="Bob"))
                conn.commit()

                # Select data
                result = conn.execute(select(users).order_by(users.c.id))
                rows = result.fetchall()

                assert len(rows) == 2
                assert rows[0].name == "Alice"
                assert rows[1].name == "Bob"
        finally:
            metadata.drop_all(mssql_engine)

    def test_identity_column(self, mssql_engine):
        """Test SQL Server IDENTITY column."""
        metadata = MetaData()

        items = Table(
            "mssql_identity_items",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("name", String(100)),
        )

        try:
            metadata.create_all(mssql_engine)

            with mssql_engine.connect() as conn:
                conn.execute(items.insert().values(name="Item 1"))
                conn.commit()

                # Get inserted ID using SCOPE_IDENTITY
                id_result = conn.execute(text("SELECT SCOPE_IDENTITY()"))
                last_id = id_result.fetchone()[0]
                assert last_id >= 1
        finally:
            metadata.drop_all(mssql_engine)


@pytest.mark.docker
class TestMSSQLORM:
    """Test SQL Server ORM functionality."""

    def test_orm_create_and_query(self, mssql_engine):
        """Test ORM create and query operations."""

        class Base(DeclarativeBase):
            pass

        class User(Base):
            __tablename__ = "mssql_orm_users"

            id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
            name: Mapped[str] = mapped_column(String(100))
            email: Mapped[str] = mapped_column(String(255), nullable=True)

        try:
            Base.metadata.create_all(mssql_engine)

            Session = sessionmaker(bind=mssql_engine)
            with Session() as session:
                user1 = User(name="Alice", email="alice@example.com")
                user2 = User(name="Bob", email="bob@example.com")
                session.add_all([user1, user2])
                session.commit()

                users = session.execute(select(User).order_by(User.id)).scalars().all()

                assert len(users) == 2
                assert users[0].name == "Alice"
                assert users[1].name == "Bob"
        finally:
            Base.metadata.drop_all(mssql_engine)


@pytest.mark.docker
class TestMSSQLAdvanced:
    """Test SQL Server advanced features."""

    def test_top_clause(self, mssql_engine):
        """Test SQL Server TOP clause."""
        metadata = MetaData()

        items = Table(
            "mssql_top_items",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("name", String(100)),
        )

        try:
            metadata.create_all(mssql_engine)

            with mssql_engine.connect() as conn:
                # Insert multiple rows
                for i in range(5):
                    conn.execute(items.insert().values(name=f"Item {i + 1}"))
                conn.commit()

                # Select top 2
                result = conn.execute(
                    text("SELECT TOP 2 * FROM mssql_top_items ORDER BY id")
                )
                rows = result.fetchall()
                assert len(rows) == 2
        finally:
            metadata.drop_all(mssql_engine)

    def test_getdate_function(self, mssql_engine):
        """Test SQL Server GETDATE() function."""
        with mssql_engine.connect() as conn:
            result = conn.execute(text("SELECT GETDATE()"))
            dt = result.fetchone()[0]
            assert dt is not None
