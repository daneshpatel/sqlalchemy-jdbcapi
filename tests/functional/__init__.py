"""
Functional tests for sqlalchemy-jdbcapi.

These tests require actual database connections and are marked with @pytest.mark.functional.
They are skipped in CI but can be run manually with real database instances.

To run functional tests:
    pytest tests/functional/ -v -m functional

To run network-dependent tests:
    pytest tests/functional/ -v -m network
"""
