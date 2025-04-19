import re
from abc import ABC
from datetime import datetime
from types import ModuleType

import jaydebeapi
from sqlalchemy import exc, sql
from sqlalchemy.dialects.oracle.base import OracleDialect
from sqlalchemy.engine.url import make_url


class OceanBaseCursor(jaydebeapi.Cursor):
    """Defined private Cursor modify the Clob object value return."""
    def __init__(self, connection, converters):
        super(OceanBaseCursor, self).__init__(connection, converters)
        jaydebeapi._unknownSqlTypeConverter = self._unknownSqlTypeConverter

    def _unknownSqlTypeConverter(self, rs, col):
        value = rs.getObject(col)
        if str(type(value)) == "<java class 'com.oceanbase.jdbc.Clob'>":
            string, reader = '', value.getCharacterStream()
            while True:
                char = reader.read()
                if char == -1:
                    break
                string += chr(char)
            value = string
        return value

    def _set_stmt_parms(self, prep_stmt, parameters):
        """Override to handle datetime conversion."""
        for i in range(len(parameters)):
            v = parameters[i]
            if isinstance(v, datetime):
                # Convert Python datetime to Java Timestamp
                import jpype
                Timestamp = jpype.JClass("java.sql.Timestamp")
                v = Timestamp.valueOf(v.strftime('%Y-%m-%d %H:%M:%S.%f'))
            # print (i, parameters[i], type(parameters[i]))
            prep_stmt.setObject(i + 1, v)



class OceanBaseJDBCDialect(OracleDialect, ABC):
    name = 'oceanbase'
    driver = 'com.alipay.oceanbase.jdbc.Driver'

    supports_native_decimal = True
    supports_sane_rowcount = False
    supports_sane_multi_rowcount = False
    supports_unicode_binds = True
    supports_statement_cache = True
    description_encoding = None

    def initialize(self, connection):
        super(OceanBaseJDBCDialect, self).initialize(connection)

    @classmethod
    def dbapi(cls):
        import jaydebeapi
        jaydebeapi.Cursor = OceanBaseCursor
        return jaydebeapi

    @classmethod
    def import_dbapi(cls) -> ModuleType:
        return __import__("jaydebeapi")

    def do_rollback(self, connection):
        pass

    def create_connect_args(self, url):
        url = make_url(url)
        jdbc_url = f"jdbc:{self.name}://{url.host}:{url.port}/{url.database}"

        kwargs = {
            "jclassname": self.driver,
            "url": jdbc_url,
            "driver_args": [url.username, url.password]
        }
        return (), kwargs

    @property
    def _is_oracle_8(self):
        return False

    def _check_max_identifier_length(self, connection):
        return None

    def _get_server_version_info(self, connection):
        try:
            ver_sql = sql.text("SELECT BANNER FROM v$version")
            banner = connection.execute(ver_sql).scalar()
            version = re.search("OceanBase ([\\d+\\.]+\\d+)", banner).group(1)
            return tuple(int(x) for x in version.split("."))
        except exc.DBAPIError:
            return None
