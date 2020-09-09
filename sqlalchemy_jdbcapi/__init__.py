from sqlalchemy.dialects import registry

__version__ = "1.2.1"

registry.register(
    "jdbcapi.pgjdbc", "sqlalchemy_jdbcapi.pgjdbc", "PGJDBCDialect"
)
registry.register(
    "jdbcapi.oraclejdbc", "sqlalchemy_jdbcapi.oraclejdbc", "OracleJDBCDialect"
)
