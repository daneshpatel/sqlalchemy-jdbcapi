from __future__ import absolute_import
from __future__ import unicode_literals

from sqlalchemy.dialects.mssql.base import MSDialect
from sqlalchemy.sql import sqltypes
from sqlalchemy import util
from .base import BaseDialect, MixedBinary
import re


colspecs = util.update_copy(
    MSDialect.colspecs, {sqltypes.LargeBinary: MixedBinary,},
)


class SQLServerJDBCDialect(BaseDialect, MSDialect):
    jdbc_db_name = "sqlserver"
    jdbc_driver_name = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
    colspecs = colspecs
    jdbc_driver_path = None

    # override this because get_isolation_level isn't cast as a string inside of MSDialect causing an error
    def get_isolation_level(self, connection):
        last_error = None

        views = ("sys.dm_exec_sessions", "sys.dm_pdw_nodes_exec_sessions")
        for view in views:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    """
                  SELECT CASE transaction_isolation_level
                    WHEN 0 THEN NULL
                    WHEN 1 THEN 'READ UNCOMMITTED'
                    WHEN 2 THEN 'READ COMMITTED'
                    WHEN 3 THEN 'REPEATABLE READ'
                    WHEN 4 THEN 'SERIALIZABLE'
                    WHEN 5 THEN 'SNAPSHOT' END AS TRANSACTION_ISOLATION_LEVEL
                    FROM %s
                    where session_id = @@SPID
                  """
                    % view
                )
                val = cursor.fetchone()[0]
            except self.dbapi.Error as err:
                # Python3 scoping rules
                last_error = err
                continue
            else:
                return str(val).upper()
            finally:
                cursor.close()
        else:
            # note that the NotImplementedError is caught by
            # DefaultDialect, so the warning here is all that displays
            util.warn(
                "Could not fetch transaction isolation level, "
                "tried views: %s; final error was: %s" % (views, last_error)
            )
            raise NotImplementedError(
                "Can't fetch isolation level on this particular "
                "SQL Server version. tried views: %s; final error was: %s"
                % (views, last_error)
            )

    # The order of initialize is trying to call this before the cursor has been set up
    def _get_server_version_info(self, connection):
        try:
            cursor = connection.cursor()
        except:
            return
        try:
            cursor.execute(
                """
                SELECT @@VERSION
                """
            )
            val = cursor.fetchone()
        except self.dbapi.Error as err:
            # Python3 scoping rules
            last_error = err
        else:
            version_match=re.fullmatch("""Microsoft SQL Server ([0-9]{4}) \(.+\) \(.+\) - (([0-9]+).[0-9]+.[0-9]+.[0-9]+) \(.+\)\s*\n\t(.*)\n\tCopyright \(.*\) [0-9]{4} Microsoft Corporation\n\t(\S*) Edition \(.+\) on (.*)""",str(val[0]))
            if version_match is None:
                self.server_version_info = None
            else:
                product="Microsoft SQL Server {}".format(version_match.group(1))
                full_version=version_match.group(2)
                major_version=version_match.group(3)
                edition=version_match.group(4)+" Edition"
                os=version_match.group(5)
                self.server_version_info = (int(major_version),)
                self.full_server_verion_info = (major_version, full_version, product, edition,os)
        finally:
            cursor.close()

    def initialize(self, connection):
        # sets up standard initialize stuff
        super(MSDialect, self).initialize(connection)
        # get the server version information using the connection inside of connection
        self._get_server_version_info(connection.connection)
        # do normal post steps
        self._setup_version_attributes()
        self._setup_supports_nvarchar_max(connection)

    def create_connect_args(self, url):
        if url is None:
            return
        if SQLServerJDBCDialect.jdbc_driver_path is None:
            driver_jars=[]
        else:
            driver_jars=[str(SQLServerJDBCDialect.jdbc_driver_path)]
        driver_args=[]
        # dialects expect jdbc url in the form of
        # "jdbc:sqlserver://user:pass@example.com:1521/db"
        # if sqlalchemy create_engine() url is passed as
        # jaydebeapi for mssql expects the user, password in driver arguments
        # and the database to be passed in after the host information with a semicolon
        s: str = str(url)
        # get jdbc url
        jdbc_url: str = s.split("//", 1)[-1]
        user_pass_match=re.fullmatch("(.*):(.*)@(.*)/(.*)",jdbc_url)
        if user_pass_match is not None:
            user=user_pass_match.group(1)
            password=user_pass_match.group(2)
            driver_args.append(user)
            driver_args.append(password)
            host_port=user_pass_match.group(3)
            database=user_pass_match.group(4)
            jdbc_url=host_port+";database={}".format(database)

        # add driver information
        if not jdbc_url.startswith("jdbc"):
            jdbc_url = f"jdbc:{self.jdbc_db_name}://{jdbc_url}"
        kwargs = {
            "jclassname": self.jdbc_driver_name,
            "url": jdbc_url,
            # pass driver args via JVM System settings
            "driver_args": driver_args,
            "jars": driver_jars
        }
        return ((), kwargs)



dialect = SQLServerJDBCDialect
