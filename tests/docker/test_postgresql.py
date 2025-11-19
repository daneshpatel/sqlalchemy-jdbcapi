"""
Functional tests for PostgreSQL using Docker container.
"""

from __future__ import annotations

import pytest
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    func,
    select,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


@pytest.mark.docker
class TestPostgreSQLConnection:
    """Test PostgreSQL connection via JDBC."""

    def test_basic_connection(self, postgres_engine):
        """Test basic connection to PostgreSQL."""
        with postgres_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

    def test_version_query(self, postgres_engine):
        """Test querying PostgreSQL version."""
        with postgres_engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            assert "PostgreSQL" in version

    def test_create_table(self, postgres_engine):
        """Test creating a table in PostgreSQL."""
        metadata = MetaData()

        Table(
            "test_users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(100)),
            Column("email", String(255)),
        )

        try:
            metadata.create_all(postgres_engine)

            # Verify table exists
            with postgres_engine.connect() as conn:
                result = conn.execute(
                    text(
                        "SELECT table_name FROM information_schema.tables "
                        "WHERE table_name = 'test_users'"
                    )
                )
                assert result.fetchone() is not None
        finally:
            metadata.drop_all(postgres_engine)

    def test_insert_and_select(self, postgres_engine):
        """Test inserting and selecting data."""
        metadata = MetaData()

        users = Table(
            "test_insert_users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(100)),
        )

        try:
            metadata.create_all(postgres_engine)

            with postgres_engine.connect() as conn:
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
            metadata.drop_all(postgres_engine)

    def test_transaction_rollback(self, postgres_engine):
        """Test transaction rollback."""
        metadata = MetaData()

        users = Table(
            "test_rollback_users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(100)),
        )

        try:
            metadata.create_all(postgres_engine)

            with postgres_engine.connect() as conn:
                # Insert and commit
                conn.execute(users.insert().values(name="Alice"))
                conn.commit()

                # Insert but rollback
                conn.execute(users.insert().values(name="Bob"))
                conn.rollback()

                # Check only Alice exists
                result = conn.execute(select(users))
                rows = result.fetchall()
                assert len(rows) == 1
                assert rows[0].name == "Alice"
        finally:
            metadata.drop_all(postgres_engine)


@pytest.mark.docker
class TestPostgreSQLORM:
    """Test PostgreSQL ORM functionality."""

    def test_orm_create_and_query(self, postgres_engine):
        """Test ORM create and query operations."""

        class Base(DeclarativeBase):
            pass

        class User(Base):
            __tablename__ = "orm_users"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(100))
            email: Mapped[str] = mapped_column(String(255), nullable=True)

        try:
            Base.metadata.create_all(postgres_engine)

            Session = sessionmaker(bind=postgres_engine)
            with Session() as session:
                # Create users
                user1 = User(name="Alice", email="alice@example.com")
                user2 = User(name="Bob", email="bob@example.com")
                session.add_all([user1, user2])
                session.commit()

                # Query users
                users = session.execute(select(User).order_by(User.id)).scalars().all()

                assert len(users) == 2
                assert users[0].name == "Alice"
                assert users[1].name == "Bob"
        finally:
            Base.metadata.drop_all(postgres_engine)

    def test_orm_update(self, postgres_engine):
        """Test ORM update operations."""

        class Base(DeclarativeBase):
            pass

        class User(Base):
            __tablename__ = "orm_update_users"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(100))

        try:
            Base.metadata.create_all(postgres_engine)

            Session = sessionmaker(bind=postgres_engine)
            with Session() as session:
                user = User(name="Alice")
                session.add(user)
                session.commit()

                # Update user
                user.name = "Alice Updated"
                session.commit()

                # Verify update
                updated = session.get(User, user.id)
                assert updated.name == "Alice Updated"
        finally:
            Base.metadata.drop_all(postgres_engine)

    def test_orm_delete(self, postgres_engine):
        """Test ORM delete operations."""

        class Base(DeclarativeBase):
            pass

        class User(Base):
            __tablename__ = "orm_delete_users"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(100))

        try:
            Base.metadata.create_all(postgres_engine)

            Session = sessionmaker(bind=postgres_engine)
            with Session() as session:
                user = User(name="Alice")
                session.add(user)
                session.commit()

                user_id = user.id

                # Delete user
                session.delete(user)
                session.commit()

                # Verify deletion
                deleted = session.get(User, user_id)
                assert deleted is None
        finally:
            Base.metadata.drop_all(postgres_engine)


@pytest.mark.docker
class TestPostgreSQLAdvanced:
    """Test PostgreSQL advanced features."""

    def test_json_type(self, postgres_engine):
        """Test PostgreSQL JSON type."""
        with postgres_engine.connect() as conn:
            result = conn.execute(text("SELECT '{\"name\": \"test\"}'::json->>'name'"))
            assert result.fetchone()[0] == "test"

    def test_array_type(self, postgres_engine):
        """Test PostgreSQL array type."""
        with postgres_engine.connect() as conn:
            result = conn.execute(text("SELECT ARRAY[1, 2, 3]"))
            value = result.fetchone()[0]
            # Result may be list or array depending on driver
            assert 1 in value or value == [1, 2, 3]

    def test_aggregate_functions(self, postgres_engine):
        """Test aggregate functions."""
        metadata = MetaData()

        scores = Table(
            "test_scores",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("score", Integer),
        )

        try:
            metadata.create_all(postgres_engine)

            with postgres_engine.connect() as conn:
                # Insert scores
                conn.execute(
                    scores.insert().values(
                        [
                            {"score": 85},
                            {"score": 90},
                            {"score": 78},
                        ]
                    )
                )
                conn.commit()

                # Calculate average
                result = conn.execute(select(func.avg(scores.c.score)))
                avg = float(result.fetchone()[0])
                assert 84 < avg < 85  # ~84.33
        finally:
            metadata.drop_all(postgres_engine)
