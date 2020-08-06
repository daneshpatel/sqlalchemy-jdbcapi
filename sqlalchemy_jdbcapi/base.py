from sqlalchemy import String, TypeDecorator


class MixedBinary(TypeDecorator):
    impl = String

    def process_result_value(self, value, dialect):
        if isinstance(value, str):
            value = bytes(value, "utf-8")
        elif value is not None:
            value = bytes(value)
        return value


class BaseDialect(object):
    jdbc_db_name = None
    jdbc_driver_name = None
    supports_native_decimal = True
    supports_sane_rowcount = False
    supports_sane_multi_rowcount = False
    supports_unicode_binds = True
    description_encoding = None

    @classmethod
    def dbapi(cls):
        import jaydebeapi

        return jaydebeapi

    def is_disconnect(self, e, connection, cursor):
        if not isinstance(e, self.dbapi.ProgrammingError):
            return False
        e = str(e)
        return "connection is closed" in e or "cursor is closed" in e

    def do_rollback(self, dbapi_connection):
        pass
