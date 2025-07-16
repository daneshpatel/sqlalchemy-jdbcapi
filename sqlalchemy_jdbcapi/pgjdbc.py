from __future__ import absolute_import
from __future__ import unicode_literals

from collections import defaultdict
from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.sql import sqltypes
from sqlalchemy import util, sql
from sqlalchemy.engine import reflection
from .base import BaseDialect, MixedBinary


colspecs = util.update_copy(
    PGDialect.colspecs, {sqltypes.LargeBinary: MixedBinary,},
)


class PGJDBCDialect(BaseDialect, PGDialect):
    jdbc_db_name = "postgresql"
    jdbc_driver_name = "org.postgresql.Driver"
    colspecs = colspecs

    def initialize(self, connection):
        super(PGJDBCDialect, self).initialize(connection)

    def create_connect_args(self, url):
        if url is None:
            return
        # dialects expect jdbc url in the form of
        # "jdbc:postgresql://example.com:1521/db"
        # if sqlalchemy create_engine() url is passed as
        # "postgresql://scott:tiger@example.com/db"
        # it is parsed wrong
        # restore original url
        s: str = str(url)
        # get jdbc url
        jdbc_url: str = s.split("//", 1)[-1]
        # add driver information
        if not jdbc_url.startswith("jdbc"):
            jdbc_url = f"jdbc:{self.jdbc_db_name}://{jdbc_url}"
        kwargs = {
            "jclassname": self.jdbc_driver_name,
            "url": jdbc_url,
            # pass driver args via JVM System settings
            "driver_args": [],
        }
        return ((), kwargs)

    @reflection.cache
    def get_unique_constraints(
        self, connection, table_name, schema=None, **kw
    ):
        table_oid = self.get_table_oid(
            connection, table_name, schema, info_cache=kw.get("info_cache")
        )

        UNIQUE_SQL = """
            SELECT
                cons.conname as name,
                cons.conkey as key,
                a.attnum as col_num,
                a.attname as col_name
            FROM
                pg_catalog.pg_constraint cons
                join pg_attribute a
                  on cons.conrelid = a.attrelid AND
                    a.attnum = ANY(cons.conkey)
            WHERE
                cons.conrelid = :table_oid AND
                cons.contype = 'u'
        """

        t = sql.text(UNIQUE_SQL).columns(col_name=sqltypes.Unicode)
        c = connection.execute(t, table_oid=table_oid)

        uniques = defaultdict(lambda: defaultdict(dict))
        for row in c.fetchall():
            uc = uniques[row.name]
            uc["key"] = (
                row.key.getArray() if hasattr(row.key, "getArray") else row.key
            )
            uc["cols"][row.col_num] = row.col_name

        return [
            {"name": name, "column_names": [uc["cols"][i] for i in uc["key"]]}
            for name, uc in uniques.items()
        ]


dialect = PGJDBCDialect
