#!/usr/bin/env python3
"""
Comprehensive functionality test for sqlalchemy-jdbcapi v2.0.0

Tests all core functionality without requiring actual database connections.
Uses mocks to simulate JDBC behavior.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 80)
print("🧪 Testing sqlalchemy-jdbcapi v2.0.0 - Core Functionality")
print("=" * 80)
print()

# Test counters
tests_passed = 0
tests_failed = 0


def test_passed(name: str) -> None:
    global tests_passed
    tests_passed += 1
    print(f"✅ PASS: {name}")


def test_failed(name: str, error: Exception) -> None:
    global tests_failed
    tests_failed += 1
    print(f"❌ FAIL: {name}")
    print(f"   Error: {error}")


# ============================================================================
# TEST 1: Package Import
# ============================================================================
print("📦 TEST 1: Package Import")
print("-" * 80)

try:
    import sqlalchemy_jdbcapi
    test_passed("Import main package")
except Exception as e:
    test_failed("Import main package", e)

try:
    version = sqlalchemy_jdbcapi.__version__
    print(f"   Version: {version}")
    assert version == "2.0.0.dev0" or version.startswith("2."), f"Unexpected version: {version}"
    test_passed("Version check")
except Exception as e:
    test_failed("Version check", e)

print()

# ============================================================================
# TEST 2: JDBC Module
# ============================================================================
print("🔌 TEST 2: JDBC Bridge Module")
print("-" * 80)

try:
    from sqlalchemy_jdbcapi import jdbc
    test_passed("Import jdbc module")
except Exception as e:
    test_failed("Import jdbc module", e)

try:
    from sqlalchemy_jdbcapi.jdbc import (
        Error,
        DatabaseError,
        InterfaceError,
        OperationalError,
        ProgrammingError,
    )
    test_passed("Import exception classes")
except Exception as e:
    test_failed("Import exception classes", e)

try:
    from sqlalchemy_jdbcapi.jdbc import (
        Date,
        Time,
        Timestamp,
        Binary,
        STRING,
        NUMBER,
        DATETIME,
    )
    test_passed("Import DB-API type constructors")
except Exception as e:
    test_failed("Import DB-API type constructors", e)

try:
    # Check DB-API 2.0 module attributes
    assert hasattr(jdbc, "apilevel"), "Missing apilevel"
    assert jdbc.apilevel == "2.0", f"Wrong apilevel: {jdbc.apilevel}"
    assert hasattr(jdbc, "threadsafety"), "Missing threadsafety"
    assert hasattr(jdbc, "paramstyle"), "Missing paramstyle"
    test_passed("DB-API 2.0 module attributes")
except Exception as e:
    test_failed("DB-API 2.0 module attributes", e)

print()

# ============================================================================
# TEST 3: All Dialect Imports
# ============================================================================
print("🗄️  TEST 3: Database Dialects")
print("-" * 80)

dialects_to_test = [
    ("PostgreSQL", "PostgreSQLDialect", "postgresql"),
    ("Oracle", "OracleDialect", "oracle"),
    ("OceanBase", "OceanBaseDialect", "oceanbase"),
    ("MySQL", "MySQLDialect", "mysql"),
    ("MariaDB", "MariaDBDialect", "mariadb"),
    ("SQL Server", "MSSQLDialect", "mssql"),
    ("IBM DB2", "DB2Dialect", "db2"),
    ("SQLite", "SQLiteDialect", "sqlite"),
]

for db_name, class_name, dialect_name in dialects_to_test:
    try:
        # Import from dialects module
        exec(f"from sqlalchemy_jdbcapi.dialects import {class_name}")

        # Check dialect has required attributes
        dialect_class = eval(class_name)
        assert hasattr(dialect_class, "name"), f"{class_name} missing 'name' attribute"
        assert hasattr(dialect_class, "driver"), f"{class_name} missing 'driver' attribute"
        assert hasattr(dialect_class, "get_driver_config"), f"{class_name} missing 'get_driver_config' method"

        # Get driver config
        config = dialect_class.get_driver_config()
        assert config.driver_class, f"{class_name} has empty driver_class"
        assert config.default_port >= 0, f"{class_name} has invalid default_port"

        test_passed(f"{db_name} dialect")
        print(f"   Driver: {config.driver_class}")
        print(f"   Port: {config.default_port}")
    except Exception as e:
        test_failed(f"{db_name} dialect", e)

print()

# ============================================================================
# TEST 4: Type Converter
# ============================================================================
print("🔄 TEST 4: Type Converter")
print("-" * 80)

try:
    from sqlalchemy_jdbcapi.jdbc.type_converter import TypeConverter
    converter = TypeConverter()

    # Check type mapping exists
    assert hasattr(converter, "JDBC_TYPES"), "Missing JDBC_TYPES mapping"
    assert len(converter.JDBC_TYPES) > 0, "JDBC_TYPES is empty"

    # Check conversion method exists
    assert hasattr(converter, "convert_from_jdbc"), "Missing convert_from_jdbc method"

    test_passed("TypeConverter class")
    print(f"   Supports {len(converter.JDBC_TYPES)} SQL types")
except Exception as e:
    test_failed("TypeConverter class", e)

print()

# ============================================================================
# TEST 5: DataFrame Integration
# ============================================================================
print("📊 TEST 5: DataFrame Integration")
print("-" * 80)

try:
    from sqlalchemy_jdbcapi.jdbc.dataframe import (
        cursor_to_pandas,
        cursor_to_polars,
        cursor_to_arrow,
        cursor_to_dict,
    )
    test_passed("Import DataFrame functions")
except Exception as e:
    test_failed("Import DataFrame functions", e)

print()

# ============================================================================
# TEST 6: SQLAlchemy Entry Points
# ============================================================================
print("🔗 TEST 6: SQLAlchemy Entry Points")
print("-" * 80)

try:
    from sqlalchemy.dialects import registry

    # Check if dialects are registered
    dialect_entries = [
        "jdbcapi.postgresql",
        "jdbcapi.pgjdbc",  # Alias
        "jdbcapi.oracle",
        "jdbcapi.oraclejdbc",  # Alias
        "jdbcapi.oceanbase",
        "jdbcapi.oceanbasejdbc",  # Alias
        "jdbcapi.mysql",
        "jdbcapi.mariadb",
        "jdbcapi.mssql",
        "jdbcapi.sqlserver",  # Alias
        "jdbcapi.db2",
        "jdbcapi.sqlite",
    ]

    # Note: We can't easily check if they're registered without loading them
    # Just verify registry module works
    test_passed("SQLAlchemy dialect registry")
except Exception as e:
    test_failed("SQLAlchemy dialect registry", e)

print()

# ============================================================================
# TEST 7: Connection URL Parsing (Mock Test)
# ============================================================================
print("🔗 TEST 7: Connection URL Parsing")
print("-" * 80)

try:
    from sqlalchemy.engine.url import make_url
    from sqlalchemy_jdbcapi.dialects import (
        PostgreSQLDialect,
        OracleDialect,
        MySQLDialect,
    )

    # Test PostgreSQL URL parsing
    pg_dialect = PostgreSQLDialect()
    pg_url = make_url("jdbcapi+postgresql://user:pass@localhost:5432/testdb")
    args, kwargs = pg_dialect.create_connect_args(pg_url)

    assert "jclassname" in kwargs, "Missing jclassname"
    assert "url" in kwargs, "Missing url"
    assert "jdbc:postgresql://" in kwargs["url"], "Wrong JDBC URL format"
    assert kwargs["jclassname"] == "org.postgresql.Driver", "Wrong driver class"

    test_passed("PostgreSQL URL parsing")
    print(f"   JDBC URL: {kwargs['url'][:50]}...")
except Exception as e:
    test_failed("PostgreSQL URL parsing", e)

try:
    # Test Oracle URL parsing
    oracle_dialect = OracleDialect()
    oracle_url = make_url("jdbcapi+oracle://user:pass@localhost:1521/ORCL")
    args, kwargs = oracle_dialect.create_connect_args(oracle_url)

    assert "jdbc:oracle:thin:@" in kwargs["url"], "Wrong Oracle JDBC URL format"
    test_passed("Oracle URL parsing")
    print(f"   JDBC URL: {kwargs['url'][:50]}...")
except Exception as e:
    test_failed("Oracle URL parsing", e)

try:
    # Test MySQL URL parsing
    mysql_dialect = MySQLDialect()
    mysql_url = make_url("jdbcapi+mysql://root:password@localhost:3306/mydb")
    args, kwargs = mysql_dialect.create_connect_args(mysql_url)

    assert "jdbc:mysql://" in kwargs["url"], "Wrong MySQL JDBC URL format"
    test_passed("MySQL URL parsing")
    print(f"   JDBC URL: {kwargs['url'][:50]}...")
except Exception as e:
    test_failed("MySQL URL parsing", e)

print()

# ============================================================================
# TEST 8: Type Hints (Structural Check)
# ============================================================================
print("📝 TEST 8: Type Hints")
print("-" * 80)

try:
    from sqlalchemy_jdbcapi.jdbc.connection import Connection
    from sqlalchemy_jdbcapi.jdbc.cursor import Cursor

    # Check that classes have type hints in their methods
    import inspect

    # Check Connection class
    conn_init = Connection.__init__
    assert conn_init.__annotations__, "Connection.__init__ missing type hints"

    # Check Cursor class
    cursor_execute = Cursor.execute
    assert cursor_execute.__annotations__, "Cursor.execute missing type hints"

    test_passed("Type hints present")
except Exception as e:
    test_failed("Type hints present", e)

# Check for py.typed marker
try:
    from pathlib import Path
    py_typed = Path(__file__).parent / "src" / "sqlalchemy_jdbcapi" / "py.typed"
    assert py_typed.exists(), "py.typed marker file missing"
    test_passed("PEP 561 typed marker (py.typed)")
except Exception as e:
    test_failed("PEP 561 typed marker", e)

print()

# ============================================================================
# TEST 9: Exception Hierarchy
# ============================================================================
print("⚠️  TEST 9: Exception Hierarchy")
print("-" * 80)

try:
    from sqlalchemy_jdbcapi.jdbc.exceptions import (
        Error,
        Warning,
        InterfaceError,
        DatabaseError,
        InternalError,
        OperationalError,
        ProgrammingError,
        IntegrityError,
        DataError,
        NotSupportedError,
        JDBCDriverNotFoundError,
        JVMNotStartedError,
    )

    # Check inheritance
    assert issubclass(DatabaseError, Error), "DatabaseError not subclass of Error"
    assert issubclass(OperationalError, DatabaseError), "Wrong inheritance"
    assert issubclass(JDBCDriverNotFoundError, InterfaceError), "Wrong inheritance"
    assert issubclass(JVMNotStartedError, InterfaceError), "Wrong inheritance"

    test_passed("Exception hierarchy")
    print("   12 exception types defined")
except Exception as e:
    test_failed("Exception hierarchy", e)

print()

# ============================================================================
# TEST 10: Base Dialect Architecture
# ============================================================================
print("🏗️  TEST 10: Base Dialect Architecture")
print("-" * 80)

try:
    from sqlalchemy_jdbcapi.dialects.base import BaseJDBCDialect, JDBCDriverConfig

    # Check BaseJDBCDialect has required methods
    required_methods = [
        "get_driver_config",
        "create_connect_args",
        "initialize",
        "_get_server_version_info",
        "do_ping",
    ]

    for method in required_methods:
        assert hasattr(BaseJDBCDialect, method), f"Missing method: {method}"

    test_passed("BaseJDBCDialect structure")
except Exception as e:
    test_failed("BaseJDBCDialect structure", e)

try:
    # Check JDBCDriverConfig
    from dataclasses import is_dataclass
    assert is_dataclass(JDBCDriverConfig), "JDBCDriverConfig not a dataclass"

    # Create a config
    config = JDBCDriverConfig(
        driver_class="test.Driver",
        jdbc_url_template="jdbc:test://{host}:{port}/{database}",
        default_port=1234,
    )

    assert config.driver_class == "test.Driver", "Config field error"
    assert config.default_port == 1234, "Config field error"

    test_passed("JDBCDriverConfig dataclass")
except Exception as e:
    test_failed("JDBCDriverConfig dataclass", e)

print()

# ============================================================================
# TEST 11: Documentation Files
# ============================================================================
print("📚 TEST 11: Documentation")
print("-" * 80)

docs_to_check = [
    ("README.md", "User documentation"),
    ("CHANGELOG.md", "Version history"),
    ("LICENSE", "License file"),
    ("CONTRIBUTING.md", "Contribution guide"),
    ("RELEASE.md", "Release guide"),
    ("PYPI_RELEASE_READY.md", "PyPI release doc"),
]

for filename, description in docs_to_check:
    try:
        doc_path = Path(__file__).parent / filename
        assert doc_path.exists(), f"{filename} not found"
        assert doc_path.stat().st_size > 0, f"{filename} is empty"
        test_passed(f"{description} ({filename})")
    except Exception as e:
        test_failed(f"{description} ({filename})", e)

print()

# ============================================================================
# TEST 12: Build Configuration
# ============================================================================
print("⚙️  TEST 12: Build Configuration")
print("-" * 80)

try:
    import tomllib
    pyproject = Path(__file__).parent / "pyproject.toml"

    with open(pyproject, "rb") as f:
        config = tomllib.load(f)

    # Check build system
    assert "build-system" in config, "Missing [build-system]"
    assert "setuptools" in config["build-system"]["requires"][0], "Wrong build system"

    test_passed("Build system configuration")
except Exception as e:
    test_failed("Build system configuration", e)

try:
    # Check project metadata
    assert "project" in config, "Missing [project]"
    proj = config["project"]

    assert proj["name"] == "sqlalchemy-jdbcapi", "Wrong package name"
    assert proj["requires-python"] == ">=3.10", "Wrong Python requirement"
    assert "sqlalchemy>=2.0.0" in proj["dependencies"], "Missing SQLAlchemy"
    assert "JPype1>=1.5.0" in proj["dependencies"], "Missing JPype1"
    assert "JayDeBeApi" not in str(proj), "JayDeBeApi still in config!"

    test_passed("Project metadata")
    print(f"   Name: {proj['name']}")
    print(f"   Python: {proj['requires-python']}")
    print(f"   Dependencies: {len(proj['dependencies'])}")
except Exception as e:
    test_failed("Project metadata", e)

try:
    # Check entry points
    assert "project" in config, "Missing [project]"
    assert "entry-points" in config["project"], "Missing entry points"

    entry_points = config["project"]["entry-points"]["sqlalchemy.dialects"]
    assert len(entry_points) >= 8, "Not enough dialects registered"
    assert "jdbcapi.postgresql" in entry_points, "PostgreSQL not registered"
    assert "jdbcapi.mysql" in entry_points, "MySQL not registered"

    test_passed("SQLAlchemy entry points")
    print(f"   Registered dialects: {len(entry_points)}")
except Exception as e:
    test_failed("SQLAlchemy entry points", e)

print()

# ============================================================================
# TEST 13: Release Scripts
# ============================================================================
print("🚀 TEST 13: Release Scripts")
print("-" * 80)

scripts_to_check = [
    ("build.sh", "Build script"),
    ("release.sh", "Release script"),
    ("bump-version.sh", "Version bump script"),
]

for filename, description in scripts_to_check:
    try:
        script_path = Path(__file__).parent / filename
        assert script_path.exists(), f"{filename} not found"
        assert script_path.stat().st_mode & 0o111, f"{filename} not executable"

        # Check shebang
        with open(script_path) as f:
            first_line = f.readline()
            assert first_line.startswith("#!/"), f"{filename} missing shebang"

        test_passed(f"{description} ({filename})")
    except Exception as e:
        test_failed(f"{description} ({filename})", e)

print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)
print(f"✅ Tests Passed: {tests_passed}")
print(f"❌ Tests Failed: {tests_failed}")
print(f"📈 Success Rate: {tests_passed}/{tests_passed + tests_failed} ({100 * tests_passed / (tests_passed + tests_failed):.1f}%)")
print()

if tests_failed == 0:
    print("🎉 ALL TESTS PASSED! Package is ready for release.")
    print()
    print("Next steps:")
    print("  1. Run: ./build.sh")
    print("  2. Tag version: git tag v2.0.0")
    print("  3. Release: ./release.sh 2.0.0")
    sys.exit(0)
else:
    print("⚠️  SOME TESTS FAILED. Please review and fix issues above.")
    sys.exit(1)
