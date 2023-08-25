from sqlalchemy.dialects import registry

__version__ = "1.3.0"

registry.register(
    "jdbcapi.pgjdbc", "sqlalchemy_jdbcapi.pgjdbc", "PGJDBCDialect"
)
registry.register(
    "jdbcapi.oraclejdbc", "sqlalchemy_jdbcapi.oraclejdbc", "OracleJDBCDialect"
)
registry.register(
    "jdbcapi.oceanbasejdbc", "sqlalchemy_jdbcapi.oceanbasejdbc", "OceanBaseJDBCDialect"
)
