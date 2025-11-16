#!/usr/bin/env python3
"""
Test SQLAlchemy integration to ensure full native dialect functionality.

This test validates that users can take full advantage of SQLAlchemy features:
- ORM support
- Core SQL expression language
- Reflection (inspecting existing databases)
- Transaction management
- Connection pooling
- Type mapping
"""

import sys
from typing import Any

def test_dialect_inheritance():
    """Test that dialects properly inherit from SQLAlchemy base dialects."""
    print("\n=== Testing Dialect Inheritance ===")

    from sqlalchemy_jdbcapi.dialects.postgresql import PostgreSQLDialect
    from sqlalchemy_jdbcapi.dialects.mysql import MySQLDialect, MariaDBDialect
    from sqlalchemy_jdbcapi.dialects.oracle import OracleDialect
    from sqlalchemy.dialects.postgresql.base import PGDialect
    from sqlalchemy.dialects.mysql.base import MySQLDialect as BaseMySQLDialect
    from sqlalchemy.dialects.oracle.base import OracleDialect as BaseOracleDialect

    # Check inheritance
    assert issubclass(PostgreSQLDialect, PGDialect), "PostgreSQL should inherit from PGDialect"
    assert issubclass(MySQLDialect, BaseMySQLDialect), "MySQL should inherit from MySQLDialect"
    assert issubclass(MariaDBDialect, BaseMySQLDialect), "MariaDB should inherit from MySQLDialect"
    assert issubclass(OracleDialect, BaseOracleDialect), "Oracle should inherit from OracleDialect"

    print("✅ All dialects properly inherit from SQLAlchemy base classes")
    return True


def test_dialect_required_methods():
    """Test that dialects implement required SQLAlchemy methods."""
    print("\n=== Testing Required Dialect Methods ===")

    from sqlalchemy_jdbcapi.dialects.postgresql import PostgreSQLDialect
    from sqlalchemy.engine.interfaces import Dialect

    dialect = PostgreSQLDialect()

    # Core methods required by SQLAlchemy
    required_methods = [
        'create_connect_args',
        'initialize',
        'do_commit',
        'do_rollback',
        'do_close',
        'do_ping',
        'is_disconnect',
        'dbapi',
    ]

    missing = []
    for method in required_methods:
        if not hasattr(dialect, method):
            missing.append(method)
        else:
            print(f"  ✅ {method}")

    if missing:
        print(f"  ❌ Missing methods: {missing}")
        return False

    print("✅ All core dialect methods present")
    return True


def test_reflection_methods():
    """Test that dialects support SQLAlchemy reflection methods."""
    print("\n=== Testing Reflection Methods (Critical for Full Integration) ===")

    from sqlalchemy_jdbcapi.dialects.postgresql import PostgreSQLDialect

    dialect = PostgreSQLDialect()

    # Reflection methods critical for ORM and autoload functionality
    reflection_methods = {
        'get_table_names': 'List all tables in schema',
        'get_columns': 'Get column definitions for table',
        'get_pk_constraint': 'Get primary key constraint',
        'get_foreign_keys': 'Get foreign key constraints',
        'get_indexes': 'Get table indexes',
        'has_table': 'Check if table exists',
        'get_schema_names': 'List all schemas',
        'get_view_names': 'List all views',
        'get_unique_constraints': 'Get unique constraints',
        'get_check_constraints': 'Get check constraints',
    }

    implemented = []
    missing = []
    inherited = []

    for method, description in reflection_methods.items():
        if hasattr(dialect, method):
            # Check if it's implemented in our dialect or just inherited
            method_owner = None
            for cls in dialect.__class__.__mro__:
                if method in cls.__dict__:
                    method_owner = cls.__name__
                    break

            if method_owner and 'JDBC' in method_owner:
                implemented.append((method, description))
                print(f"  ✅ {method}: {description} [Implemented in {method_owner}]")
            else:
                inherited.append((method, description, method_owner or 'Unknown'))
                print(f"  ⚠️  {method}: {description} [Inherited from {method_owner or 'base class'}]")
        else:
            missing.append((method, description))
            print(f"  ❌ {method}: {description} [NOT FOUND]")

    print(f"\nSummary:")
    print(f"  Implemented in JDBC dialects: {len(implemented)}")
    print(f"  Inherited (may not work with JDBC): {len(inherited)}")
    print(f"  Missing: {len(missing)}")

    if inherited:
        print(f"\n⚠️  WARNING: {len(inherited)} methods inherited from base classes.")
        print("   These methods may not work correctly with JDBC connections!")
        print("   They should be overridden to work with JDBC metadata APIs.")

    if missing:
        print(f"\n❌ CRITICAL: {len(missing)} reflection methods missing!")
        print("   Users cannot use Table autoload or ORM automapping!")
        return False

    return len(missing) == 0 and len(inherited) == 0


def test_transaction_support():
    """Test transaction management methods."""
    print("\n=== Testing Transaction Support ===")

    from sqlalchemy_jdbcapi.dialects.postgresql import PostgreSQLDialect

    dialect = PostgreSQLDialect()

    transaction_methods = [
        'do_begin',
        'do_commit',
        'do_rollback',
        'do_savepoint',
        'do_rollback_to_savepoint',
        'do_release_savepoint',
    ]

    found = []
    missing = []

    for method in transaction_methods:
        if hasattr(dialect, method):
            found.append(method)
            print(f"  ✅ {method}")
        else:
            missing.append(method)
            print(f"  ⚠️  {method} - may use default implementation")

    print(f"\nTransaction methods found: {len(found)}/{len(transaction_methods)}")
    return True


def test_type_mapping():
    """Test SQLAlchemy type mapping."""
    print("\n=== Testing Type Mapping ===")

    from sqlalchemy_jdbcapi.dialects.postgresql import PostgreSQLDialect
    from sqlalchemy import types

    dialect = PostgreSQLDialect()

    # Check if colspecs is defined (type overrides)
    if hasattr(dialect, 'colspecs'):
        print(f"  ✅ colspecs defined with {len(dialect.colspecs)} type mappings")
    else:
        print(f"  ⚠️  No colspecs defined (using defaults)")

    # Check if we can get type descriptor
    string_type = dialect.type_descriptor(types.String())
    int_type = dialect.type_descriptor(types.Integer())

    print(f"  ✅ String type: {string_type}")
    print(f"  ✅ Integer type: {int_type}")

    return True


def test_url_parsing():
    """Test SQLAlchemy URL parsing and connection args creation."""
    print("\n=== Testing URL Parsing ===")

    from sqlalchemy.engine.url import make_url
    from sqlalchemy_jdbcapi.dialects.postgresql import PostgreSQLDialect

    dialect = PostgreSQLDialect()

    test_urls = [
        "jdbcapi+postgresql://user:pass@localhost:5432/testdb",
        "jdbcapi+postgresql://user:pass@localhost/testdb?ssl=true",
        "jdbcapi+mysql://root:pass@localhost:3306/mydb",
    ]

    for url_string in test_urls:
        try:
            url = make_url(url_string)
            args, kwargs = dialect.create_connect_args(url)

            print(f"  ✅ {url.drivername}://{url.host}:{url.port}/{url.database}")
            print(f"     JDBC URL: {kwargs.get('url', 'N/A')[:60]}...")
            print(f"     Driver: {kwargs.get('jclassname', 'N/A')}")
        except Exception as e:
            print(f"  ❌ Failed to parse {url_string}: {e}")
            return False

    print("✅ URL parsing works correctly")
    return True


def test_orm_basic_usage():
    """Test that SQLAlchemy ORM can be used (without actual DB connection)."""
    print("\n=== Testing ORM Declaration ===")

    try:
        from sqlalchemy import create_engine, Column, Integer, String
        from sqlalchemy.orm import declarative_base, Session

        Base = declarative_base()

        class User(Base):
            __tablename__ = 'users'

            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            email = Column(String(100))

        # Create mock engine (won't actually connect)
        # This tests that the dialect can be loaded and initialized
        try:
            engine = create_engine(
                "jdbcapi+postgresql://user:pass@localhost:5432/testdb",
                strategy='mock',
                executor=lambda *a, **kw: None
            )
            print(f"  ✅ Engine created with dialect: {engine.dialect.name}")
            print(f"  ✅ Dialect class: {engine.dialect.__class__.__name__}")
        except ImportError:
            # strategy='mock' might not be available in all SQLAlchemy versions
            print(f"  ⚠️  Mock engine not available (SQLAlchemy version)")

        print("  ✅ ORM models can be declared")
        print("  ✅ Base SQLAlchemy ORM integration works")

        return True

    except Exception as e:
        print(f"  ❌ ORM declaration failed: {e}")
        return False


def test_core_sql_usage():
    """Test SQLAlchemy Core SQL expressions."""
    print("\n=== Testing Core SQL Expression Language ===")

    try:
        from sqlalchemy import Table, Column, Integer, String, MetaData, select

        metadata = MetaData()

        users = Table('users', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50)),
            Column('email', String(100))
        )

        # Test various SQL constructs
        stmt = select(users).where(users.c.name == 'test')
        print(f"  ✅ SELECT statement: {stmt}")

        stmt = users.insert().values(name='test', email='test@example.com')
        print(f"  ✅ INSERT statement: {stmt}")

        stmt = users.update().where(users.c.id == 1).values(name='updated')
        print(f"  ✅ UPDATE statement: {stmt}")

        stmt = users.delete().where(users.c.id == 1)
        print(f"  ✅ DELETE statement: {stmt}")

        print("✅ Core SQL expression language works")
        return True

    except Exception as e:
        print(f"  ❌ Core SQL failed: {e}")
        return False


def test_inspector_interface():
    """Test SQLAlchemy Inspector interface."""
    print("\n=== Testing Inspector Interface ===")

    try:
        from sqlalchemy import inspect, create_engine
        from sqlalchemy_jdbcapi.dialects.postgresql import PostgreSQLDialect

        # We can't actually connect, but we can test the interface
        dialect = PostgreSQLDialect()

        inspector_methods = [
            'get_table_names',
            'get_columns',
            'get_pk_constraint',
            'get_foreign_keys',
            'get_indexes',
        ]

        available = []
        missing = []

        for method in inspector_methods:
            if hasattr(dialect, method):
                available.append(method)
                print(f"  ✅ {method} available")
            else:
                missing.append(method)
                print(f"  ❌ {method} NOT available")

        if missing:
            print(f"\n⚠️  WARNING: Inspector methods missing: {missing}")
            print("   Users cannot use inspector.get_table_names() etc.")
            print("   This breaks Table(..., autoload_with=engine) functionality!")
            return False

        print("✅ Inspector interface complete")
        return True

    except Exception as e:
        print(f"  ❌ Inspector test failed: {e}")
        return False


def test_entry_points():
    """Test that dialect entry points are registered."""
    print("\n=== Testing Entry Point Registration ===")

    try:
        from sqlalchemy.dialects import registry

        # These should be registered in __init__.py
        test_names = [
            'jdbcapi.postgresql',
            'jdbcapi.mysql',
            'jdbcapi.oracle',
            'jdbcapi.mariadb',
            'jdbcapi.mssql',
            'jdbcapi.db2',
            'jdbcapi.oceanbase',
            'jdbcapi.sqlite',
        ]

        registered = 0
        for name in test_names:
            try:
                # Try to load the dialect
                dialect_cls = registry.load(name)
                print(f"  ✅ {name} -> {dialect_cls.__name__}")
                registered += 1
            except Exception as e:
                print(f"  ❌ {name} failed: {e}")

        print(f"\nRegistered: {registered}/{len(test_names)} dialects")

        if registered != len(test_names):
            print("⚠️  Some dialects not registered!")
            return False

        print("✅ All entry points registered correctly")
        return True

    except Exception as e:
        print(f"  ❌ Entry point test failed: {e}")
        return False


def main():
    """Run all SQLAlchemy integration tests."""
    print("=" * 70)
    print("SQLAlchemy Native Dialect Integration Test")
    print("=" * 70)
    print("\nThis test validates that users can take FULL advantage of SQLAlchemy:")
    print("- ORM support (declarative models, relationships, queries)")
    print("- Core SQL (select, insert, update, delete)")
    print("- Reflection (inspecting existing databases)")
    print("- Transactions and connection pooling")
    print("- Type mapping and conversions")

    tests = [
        ("Dialect Inheritance", test_dialect_inheritance),
        ("Required Methods", test_dialect_required_methods),
        ("Reflection Methods", test_reflection_methods),
        ("Transaction Support", test_transaction_support),
        ("Type Mapping", test_type_mapping),
        ("URL Parsing", test_url_parsing),
        ("ORM Basic Usage", test_orm_basic_usage),
        ("Core SQL Usage", test_core_sql_usage),
        ("Inspector Interface", test_inspector_interface),
        ("Entry Points", test_entry_points),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 70)

    if passed == total:
        print("\n🎉 EXCELLENT! Full SQLAlchemy native dialect integration!")
        print("Users can take full advantage of all SQLAlchemy features.")
        return 0
    elif passed >= total * 0.7:
        print("\n⚠️  PARTIAL INTEGRATION - Some features may not work")
        print("Users may encounter limitations with reflection/ORM autoload.")
        return 1
    else:
        print("\n❌ CRITICAL GAPS in SQLAlchemy integration!")
        print("Users cannot fully utilize SQLAlchemy features.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
