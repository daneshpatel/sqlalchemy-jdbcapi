from sqlalchemy.dialects import registry

__version__ = "1.0"

registry.register(
    "jdbcapi.pgjdbc", "sqlalchemy_jdbcapi.pgjdbc", "PGJDBCDialect"
)
