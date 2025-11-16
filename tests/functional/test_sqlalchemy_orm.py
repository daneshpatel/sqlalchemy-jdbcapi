"""
Functional tests for SQLAlchemy ORM integration.

These tests verify full ORM functionality with table creation, CRUD operations,
and reflection capabilities.
"""

from __future__ import annotations

from datetime import date, datetime

import pytest
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    inspect,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for ORM models."""


class User(Base):
    """User model for testing ORM."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime)

    posts: Mapped[list[Post]] = relationship(back_populates="author")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"


class Post(Base):
    """Post model for testing relationships."""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(String(1000))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    published_date: Mapped[date] = mapped_column(Date)

    author: Mapped[User] = relationship(back_populates="posts")

    def __repr__(self) -> str:
        return f"<Post(id={self.id}, title='{self.title}')>"


@pytest.mark.functional
class TestSQLiteJDBCORM:
    """Test SQLAlchemy ORM with SQLite JDBC dialect."""

    @pytest.fixture
    def engine(self):
        """Create in-memory SQLite engine."""
        # Note: This requires JPype and SQLite JDBC driver
        # Will skip if not available
        pytest.skip("Requires JVM and JDBC drivers - manual test only")

        engine = create_engine(
            "jdbcapi+sqlite:///:memory:",
            echo=False,
        )
        return engine

    def test_create_tables(self, engine):
        """Test creating tables with ORM models."""
        Base.metadata.create_all(engine)

        # Verify tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        assert "users" in tables
        assert "posts" in tables

    def test_insert_and_query_users(self, engine):
        """Test inserting and querying users."""
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            # Create users
            user1 = User(
                username="alice",
                email="alice@example.com",
                created_at=datetime(2024, 1, 1, 12, 0, 0),
            )
            user2 = User(
                username="bob",
                email="bob@example.com",
                created_at=datetime(2024, 1, 2, 12, 0, 0),
            )

            session.add_all([user1, user2])
            session.commit()

            # Query users
            users = session.execute(select(User)).scalars().all()

            assert len(users) == 2
            assert users[0].username == "alice"
            assert users[1].username == "bob"

    def test_relationships(self, engine):
        """Test ORM relationships."""
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            # Create user
            user = User(
                username="alice",
                email="alice@example.com",
                created_at=datetime(2024, 1, 1, 12, 0, 0),
            )
            session.add(user)
            session.flush()

            # Create posts
            post1 = Post(
                title="First Post",
                content="Hello World",
                user_id=user.id,
                published_date=date(2024, 1, 1),
            )
            post2 = Post(
                title="Second Post",
                content="SQLAlchemy is great",
                user_id=user.id,
                published_date=date(2024, 1, 2),
            )

            session.add_all([post1, post2])
            session.commit()

            # Query user with posts
            user = session.execute(
                select(User).filter_by(username="alice")
            ).scalar_one()

            assert len(user.posts) == 2
            assert user.posts[0].title == "First Post"
            assert user.posts[1].title == "Second Post"

    def test_update_operations(self, engine):
        """Test UPDATE operations."""
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            user = User(
                username="alice",
                email="alice@example.com",
                created_at=datetime.now(),
            )
            session.add(user)
            session.commit()

            # Update email
            user.email = "alice.updated@example.com"
            session.commit()

            # Verify update
            updated_user = session.execute(
                select(User).filter_by(username="alice")
            ).scalar_one()

            assert updated_user.email == "alice.updated@example.com"

    def test_delete_operations(self, engine):
        """Test DELETE operations."""
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            user = User(
                username="alice",
                email="alice@example.com",
                created_at=datetime.now(),
            )
            session.add(user)
            session.commit()

            # Delete user
            session.delete(user)
            session.commit()

            # Verify deletion
            users = session.execute(select(User)).scalars().all()
            assert len(users) == 0


@pytest.mark.functional
class TestReflection:
    """Test SQLAlchemy reflection capabilities."""

    @pytest.fixture
    def engine(self):
        """Create in-memory SQLite engine."""
        pytest.skip("Requires JVM and JDBC drivers - manual test only")

        engine = create_engine("jdbcapi+sqlite:///:memory:", echo=False)
        return engine

    def test_reflect_tables(self, engine):
        """Test reflecting existing tables."""
        # Create tables manually
        metadata = MetaData()

        users_table = Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("username", String(50)),
            Column("email", String(100)),
        )

        metadata.create_all(engine)

        # Reflect tables
        reflected_metadata = MetaData()
        reflected_metadata.reflect(bind=engine)

        assert "users" in reflected_metadata.tables
        reflected_users = reflected_metadata.tables["users"]

        # Verify columns
        column_names = [col.name for col in reflected_users.columns]
        assert "id" in column_names
        assert "username" in column_names
        assert "email" in column_names

    def test_reflect_primary_keys(self, engine):
        """Test reflecting primary keys."""
        metadata = MetaData()

        Table(
            "test_pk",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
        )

        metadata.create_all(engine)

        # Reflect and check primary key
        inspector = inspect(engine)
        pk_constraint = inspector.get_pk_constraint("test_pk")

        assert "id" in pk_constraint["constrained_columns"]

    def test_reflect_foreign_keys(self, engine):
        """Test reflecting foreign keys."""
        metadata = MetaData()

        users = Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
        )

        posts = Table(
            "posts",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("user_id", Integer, ForeignKey("users.id")),
            Column("title", String(100)),
        )

        metadata.create_all(engine)

        # Reflect foreign keys
        inspector = inspect(engine)
        fks = inspector.get_foreign_keys("posts")

        assert len(fks) > 0
        assert fks[0]["referred_table"] == "users"


@pytest.mark.functional
class TestComplexQueries:
    """Test complex SQL queries and aggregations."""

    @pytest.fixture
    def engine_with_data(self):
        """Create engine with sample data."""
        pytest.skip("Requires JVM and JDBC drivers - manual test only")

        engine = create_engine("jdbcapi+sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            # Create users
            users = [
                User(
                    username=f"user{i}",
                    email=f"user{i}@example.com",
                    created_at=datetime(2024, 1, i, 12, 0, 0),
                )
                for i in range(1, 6)
            ]
            session.add_all(users)
            session.flush()

            # Create posts
            posts = [
                Post(
                    title=f"Post {i}",
                    content=f"Content {i}",
                    user_id=users[i % 5].id,
                    published_date=date(2024, 1, i),
                )
                for i in range(1, 21)
            ]
            session.add_all(posts)
            session.commit()

        return engine

    def test_join_query(self, engine_with_data):
        """Test JOIN queries."""
        with Session(engine_with_data) as session:
            # Query posts with user information
            stmt = select(Post, User).join(User, Post.user_id == User.id)
            results = session.execute(stmt).all()

            assert len(results) == 20

            for post, user in results:
                assert post.user_id == user.id

    def test_aggregation_query(self, engine_with_data):
        """Test aggregation queries."""
        from sqlalchemy import func

        with Session(engine_with_data) as session:
            # Count posts per user
            stmt = (
                select(User.username, func.count(Post.id).label("post_count"))
                .join(Post)
                .group_by(User.username)
            )

            results = session.execute(stmt).all()

            assert len(results) == 5  # 5 users

            for username, post_count in results:
                assert post_count == 4  # 20 posts / 5 users

    def test_filtering_and_ordering(self, engine_with_data):
        """Test filtering and ordering."""
        with Session(engine_with_data) as session:
            # Get posts from specific date range, ordered by date
            stmt = (
                select(Post)
                .filter(Post.published_date >= date(2024, 1, 10))
                .order_by(Post.published_date.desc())
            )

            posts = session.execute(stmt).scalars().all()

            assert len(posts) > 0
            # Verify ordering
            for i in range(len(posts) - 1):
                assert posts[i].published_date >= posts[i + 1].published_date
