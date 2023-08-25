import re
from abc import ABC
from types import ModuleType

from sqlalchemy import exc, sql
from sqlalchemy.dialects.oracle.base import OracleDialect
from sqlalchemy.engine.url import make_url


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

    def _get_server_version_info(self, connection):
        try:
            ver_sql = sql.text("SELECT BANNER FROM v$version")
            banner = connection.execute(ver_sql).scalar()
            version = re.search("OceanBase ([\\d+\\.]+\\d+)", banner).group(1)
            return tuple(int(x) for x in version.split("."))
        except exc.DBAPIError:
            return None
