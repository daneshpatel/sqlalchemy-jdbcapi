from __future__ import absolute_import
from __future__ import unicode_literals

import os
from sqlalchemy.dialects.postgresql.base import PGDialect


class PGJDBCDialect(PGDialect):
    jdbc_db_name = "postgresql"
    jdbc_driver_name = "org.postgresql.Driver"
    supports_native_decimal = True
    supports_sane_rowcount = False
    supports_sane_multi_rowcount = False
    supports_unicode_binds = True
    description_encoding = None

    def __init__(self, *args, **kwargs):
        super(PGJDBCDialect, self).__init__(*args, **kwargs)
        self.jdbc_driver_path = os.environ.get("PG_JDBC_DRIVER_PATH")
        self.jdbc_jar_name = os.environ.get("PG_JDBC_JAR_NAME")

        if self.jdbc_driver_path is None:
            raise Exception(
                "To connect to DATABASE via JDBC, you must set the "
                "PG_JDBC_DRIVER_PATH path to the location of the JDBC driver"
            )

        if self.jdbc_jar_name is None:
            raise Exception(
                "To connect to DATABASE via JDBC, you must set the "
                "PG_JDBC_JAR_NAME environment variable."
            )

    def initialize(self, connection):
        super(PGJDBCDialect, self).initialize(connection)

    def create_connect_args(self, url):
        if url is not None:
            params = super(PGDialect, self).create_connect_args(url)[1]
            driver = self.jdbc_driver_path + self.jdbc_jar_name

            cargs = (
                self.jdbc_driver_name,
                self._create_jdbc_url(url),
                [params["username"], params["password"]],
                driver,
            )

            return (cargs, {})

    def _create_jdbc_url(self, url):
        """Create a JDBC url from a :class:`~sqlalchemy.engine.url.URL`"""
        return "jdbc:%s://%s%s/%s" % (
            self.jdbc_db_name,
            url.host,
            url.port is not None and ":%s" % url.port or "",
            url.database,
        )

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


dialect = PGJDBCDialect
