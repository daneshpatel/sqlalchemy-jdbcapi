from __future__ import absolute_import
from __future__ import unicode_literals

import os
from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.sql import sqltypes
from sqlalchemy import util
from .base import BaseDialect, MixedBinary


colspecs = util.update_copy(
    PGDialect.colspecs, {sqltypes.LargeBinary: MixedBinary,},
)


class PGJDBCDialect(BaseDialect, PGDialect):
    jdbc_db_name = "postgresql"
    jdbc_driver_name = "org.postgresql.Driver"
    colspecs = colspecs

    def __init__(self, *args, **kwargs):
        super(PGJDBCDialect, self).__init__(*args, **kwargs)
        self.jdbc_driver_path = os.environ.get("PG_JDBC_DRIVER_PATH")

        if self.jdbc_driver_path is None:
            raise Exception(
                "To connect to DATABASE via JDBC, you must set the "
                "PG_JDBC_DRIVER_PATH path to the location of the JDBC driver"
            )

    def initialize(self, connection):
        super(PGJDBCDialect, self).initialize(connection)

    def create_connect_args(self, url):
        if url is not None:
            params = super(PGJDBCDialect, self).create_connect_args(url)[1]
            driver = self.jdbc_driver_path

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


dialect = PGJDBCDialect
