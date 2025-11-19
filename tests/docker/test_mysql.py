"""
Functional tests for MySQL using Docker container.
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
class TestMySQLConnection:
    """Test MySQL connection via JDBC."""

    def test_basic_connection(self, mysql_engine):
        """Test basic connection to MySQL."""
        with mysql_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

    def test_version_query(self, mysql_engine):
        """Test querying MySQL version."""
        with mysql_engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            assert version is not None

    def test_create_table(self, mysql_engine):
        """Test creating a table in MySQL."""
        metadata = MetaData()

        test_table = Table(
            "mysql_test_users",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("name", String(100)),
            Column("email", String(255)),
        )

        try:
            metadata.create_all(mysql_engine)

            # Verify table exists
            with mysql_engine.connect() as conn:
                result = conn.execute(
                    text("SHOW TABLES LIKE 'mysql_test_users'")
                )
                assert result.fetchone() is not None
        finally:
            metadata.drop_all(mysql_engine)

    def test_insert_and_select(self, mysql_engine):
        """Test inserting and selecting data."""
        metadata = MetaData()

        users = Table(
            "mysql_insert_users",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("name", String(100)),
        )

        try:
            metadata.create_all(mysql_engine)

            with mysql_engine.connect() as conn:
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
            metadata.drop_all(mysql_engine)

    def test_auto_increment(self, mysql_engine):
        """Test MySQL AUTO_INCREMENT."""
        metadata = MetaData()

        items = Table(
            "mysql_auto_items",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("name", String(100)),
        )

        try:
            metadata.create_all(mysql_engine)

            with mysql_engine.connect() as conn:
                result = conn.execute(items.insert().values(name="Item 1"))
                conn.commit()

                # Get last insert ID
                id_result = conn.execute(text("SELECT LAST_INSERT_ID()"))
                last_id = id_result.fetchone()[0]
                assert last_id >= 1
        finally:
            metadata.drop_all(mysql_engine)


@pytest.mark.docker
class TestMySQLORM:
    """Test MySQL ORM functionality."""

    def test_orm_create_and_query(self, mysql_engine):
        """Test ORM create and query operations."""

        class Base(DeclarativeBase):
            pass

        class User(Base):
            __tablename__ = "mysql_orm_users"

            id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
            name: Mapped[str] = mapped_column(String(100))
            email: Mapped[str] = mapped_column(String(255), nullable=True)

        try:
            Base.metadata.create_all(mysql_engine)

            Session = sessionmaker(bind=mysql_engine)
            with Session() as session:
                user1 = User(name="Alice", email="alice@example.com")
                user2 = User(name="Bob", email="bob@example.com")
                session.add_all([user1, user2])
                session.commit()

                users = session.execute(
                    select(User).order_by(User.id)
                ).scalars().all()

                assert len(users) == 2
                assert users[0].name == "Alice"
                assert users[1].name == "Bob"
        finally:
            Base.metadata.drop_all(mysql_engine)


@pytest.mark.docker
class TestMariaDBConnection:
    """Test MariaDB connection via JDBC."""

    def test_basic_connection(self, mariadb_engine):
        """Test basic connection to MariaDB."""
        with mariadb_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

    def test_version_query(self, mariadb_engine):
        """Test querying MariaDB version."""
        with mariadb_engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            assert "MariaDB" in version or version is not None

    def test_insert_and_select(self, mariadb_engine):
        """Test inserting and selecting data in MariaDB."""
        metadata = MetaData()

        users = Table(
            "mariadb_insert_users",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("name", String(100)),
        )

        try:
            metadata.create_all(mariadb_engine)

            with mariadb_engine.connect() as conn:
                conn.execute(users.insert().values(name="Alice"))
                conn.execute(users.insert().values(name="Bob"))
                conn.commit()

                result = conn.execute(select(users).order_by(users.c.id))
                rows = result.fetchall()

                assert len(rows) == 2
                assert rows[0].name == "Alice"
                assert rows[1].name == "Bob"
        finally:
            metadata.drop_all(mariadb_engine)
