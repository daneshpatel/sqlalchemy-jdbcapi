# Supported Drivers

Comprehensive guide to JDBC and ODBC drivers supported by sqlalchemy-jdbcapi.

## Table of Contents

- [JDBC Drivers](#jdbc-drivers)
- [ODBC Drivers](#odbc-drivers)
- [Driver Compatibility Matrix](#driver-compatibility-matrix)
- [Installation Instructions](#installation-instructions)

## JDBC Drivers

### Overview

JDBC drivers are automatically downloaded from Maven Central on first use. Manual installation is also supported.

### PostgreSQL

**Recommended Version:** 42.7.1
**Maven Coordinates:** `org.postgresql:postgresql:42.7.1`
**JDBC URL Format:** `jdbcapi+postgresql://user:password@host:5432/database`

**Supported PostgreSQL Versions:**
- PostgreSQL 16.x
- PostgreSQL 15.x
- PostgreSQL 14.x
- PostgreSQL 13.x
- PostgreSQL 12.x
- PostgreSQL 11.x
- PostgreSQL 10.x
- PostgreSQL 9.6+

**Features:**
- Arrays
- JSONB
- UUID
- Full-text search
- Sequences
- Listen/Notify
- COPY command
- SSL/TLS support

**Manual Download:**
```bash
wget https://jdbc.postgresql.org/download/postgresql-42.7.1.jar
export CLASSPATH="/path/to/postgresql-42.7.1.jar:$CLASSPATH"
```

### MySQL

**Recommended Version:** 8.3.0
**Maven Coordinates:** `com.mysql:mysql-connector-j:8.3.0`
**JDBC URL Format:** `jdbcapi+mysql://user:password@host:3306/database`

**Supported MySQL Versions:**
- MySQL 8.0.x
- MySQL 5.7.x
- MySQL 5.6.x

**Features:**
- AUTO_INCREMENT
- Full-text indexes
- JSON data type (MySQL 5.7+)
- Spatial data types
- Multi-statement support
- SSL/TLS support
- Server-side prepared statements

**Manual Download:**
```bash
wget https://repo1.maven.org/maven2/com/mysql/mysql-connector-j/8.3.0/mysql-connector-j-8.3.0.jar
export CLASSPATH="/path/to/mysql-connector-j-8.3.0.jar:$CLASSPATH"
```

**Connection Parameters:**
```python
engine = create_engine(
    "jdbcapi+mysql://user:password@localhost:3306/mydb",
    connect_args={
        "useSSL": "false",
        "serverTimezone": "UTC",
        "allowMultiQueries": "true"
    }
)
```

### MariaDB

**Recommended Version:** 3.3.2
**Maven Coordinates:** `org.mariadb.jdbc:mariadb-java-client:3.3.2`
**JDBC URL Format:** `jdbcapi+mariadb://user:password@host:3306/database`

**Supported MariaDB Versions:**
- MariaDB 11.x
- MariaDB 10.11 LTS
- MariaDB 10.6 LTS
- MariaDB 10.5 LTS
- MariaDB 10.4+

**Features:**
- Sequences (MariaDB 10.3+)
- MySQL compatibility
- Galera Cluster support
- Pipeline batching
- Multi-master replication
- SSL/TLS support

**Manual Download:**
```bash
wget https://repo1.maven.org/maven2/org/mariadb/jdbc/mariadb-java-client/3.3.2/mariadb-java-client-3.3.2.jar
export CLASSPATH="/path/to/mariadb-java-client-3.3.2.jar:$CLASSPATH"
```

### Microsoft SQL Server

**Recommended Version:** 12.6.0.jre11
**Maven Coordinates:** `com.microsoft.sqlserver:mssql-jdbc:12.6.0.jre11`
**JDBC URL Format:** `jdbcapi+mssql://user:password@host:1433/database`

**Supported SQL Server Versions:**
- SQL Server 2022
- SQL Server 2019
- SQL Server 2017
- SQL Server 2016
- SQL Server 2014
- SQL Server 2012
- Azure SQL Database
- Azure SQL Managed Instance

**Features:**
- T-SQL support
- Window functions
- CTEs (Common Table Expressions)
- JSON support (SQL Server 2016+)
- Sequence support (SQL Server 2012+)
- Always Encrypted
- Active Directory authentication
- SSL/TLS support

**Manual Download:**
```bash
wget https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.6.0.jre11/mssql-jdbc-12.6.0.jre11.jar
export CLASSPATH="/path/to/mssql-jdbc-12.6.0.jre11.jar:$CLASSPATH"
```

**Connection Parameters:**
```python
engine = create_engine(
    "jdbcapi+mssql://user:password@localhost:1433/mydb",
    connect_args={
        "encrypt": "true",
        "trustServerCertificate": "true",
        "loginTimeout": "30"
    }
)
```

### Oracle

**Recommended Version:** 23.3.0.23.09
**Maven Coordinates:** `com.oracle.database.jdbc:ojdbc11:23.3.0.23.09`
**JDBC URL Format:** `jdbcapi+oracle://user:password@host:1521/service_name`

**Supported Oracle Versions:**
- Oracle Database 23c
- Oracle Database 21c
- Oracle Database 19c
- Oracle Database 18c
- Oracle Database 12c Release 2
- Oracle Database 12c Release 1
- Oracle Database 11g Release 2

**Features:**
- Sequences
- Synonyms
- Database links
- PL/SQL support
- Oracle RAC
- Advanced Queuing
- Flashback queries
- SSL/TLS support

**Manual Download:**
```bash
# Oracle drivers require accepting license agreement
# Download from: https://www.oracle.com/database/technologies/appdev/jdbc-downloads.html
export CLASSPATH="/path/to/ojdbc11-23.3.0.23.09.jar:$CLASSPATH"
```

**Connection String Variants:**
```python
# Using service name
engine = create_engine("jdbcapi+oracle://user:password@localhost:1521/XEPDB1")

# Using SID
engine = create_engine("jdbcapi+oracle://user:password@localhost:1521/XE")

# Using TNS alias
engine = create_engine("jdbcapi+oracle://user:password@TNSALIAS")
```

### IBM DB2

**Recommended Version:** 11.5.9.0
**Maven Coordinates:** `com.ibm.db2:jcc:11.5.9.0`
**JDBC URL Format:** `jdbcapi+db2://user:password@host:50000/database`

**Supported DB2 Versions:**
- DB2 for Linux, UNIX and Windows 11.5
- DB2 for Linux, UNIX and Windows 11.1
- DB2 for z/OS 12
- DB2 for z/OS 11
- DB2 for i 7.4
- DB2 for i 7.3

**Features:**
- Sequences
- Identity columns
- Temporal tables
- XML support
- pureXML
- Multi-row INSERT
- SSL/TLS support

**Manual Download:**
```bash
# Download from IBM website (requires IBM ID)
# https://www.ibm.com/support/pages/db2-jdbc-driver-versions-and-downloads
export CLASSPATH="/path/to/jcc-11.5.9.0.jar:$CLASSPATH"
```

### SQLite

**Recommended Version:** 3.45.0.0
**Maven Coordinates:** `org.xerial:sqlite-jdbc:3.45.0.0`
**JDBC URL Format:** `jdbcapi+sqlite:///path/to/database.db`

**Supported SQLite Versions:**
- SQLite 3.45.x
- SQLite 3.44.x
- SQLite 3.43.x

**Features:**
- In-memory databases
- Full-text search (FTS5)
- JSON support
- Common Table Expressions
- Window functions
- Partial indexes
- Generated columns

**Manual Download:**
```bash
wget https://repo1.maven.org/maven2/org/xerial/sqlite-jdbc/3.45.0.0/sqlite-jdbc-3.45.0.0.jar
export CLASSPATH="/path/to/sqlite-jdbc-3.45.0.0.jar:$CLASSPATH"
```

**Usage:**
```python
# File-based database
engine = create_engine("jdbcapi+sqlite:////absolute/path/to/database.db")

# Relative path
engine = create_engine("jdbcapi+sqlite:///relative/path/database.db")

# In-memory database
engine = create_engine("jdbcapi+sqlite:///:memory:")
```

### OceanBase

**Recommended Version:** 2.4.9
**Maven Coordinates:** `com.oceanbase:oceanbase-client:2.4.9`
**JDBC URL Format:** `jdbcapi+oceanbase://user@tenant#cluster:password@host:2881/database`

**Supported OceanBase Versions:**
- OceanBase 4.x
- OceanBase 3.x
- OceanBase 2.x

**Features:**
- Oracle compatibility mode
- MySQL compatibility mode
- Custom timestamp handling
- Distributed transactions
- High availability
- Multi-tenancy

**Manual Download:**
```bash
wget https://repo1.maven.org/maven2/com/oceanbase/oceanbase-client/2.4.9/oceanbase-client-2.4.9.jar
export CLASSPATH="/path/to/oceanbase-client-2.4.9.jar:$CLASSPATH"
```

## ODBC Drivers

### Overview

ODBC drivers must be installed manually on your system. Connection strings use the `odbcapi+` prefix.

### PostgreSQL ODBC

**Recommended Driver:** PostgreSQL Unicode (psqlODBC)
**Latest Version:** 16.00.0000 (as of 2024)
**ODBC URL Format:** `odbcapi+postgresql://user:password@host:5432/database`

**Installation:**

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install odbc-postgresql unixodbc unixodbc-dev
```

**Linux (RHEL/CentOS):**
```bash
sudo yum install postgresql-odbc unixODBC unixODBC-devel
```

**macOS:**
```bash
brew install psqlodbc unixodbc
```

**Windows:**
Download from https://www.postgresql.org/ftp/odbc/versions/

**Verify Installation:**
```bash
odbcinst -q -d
```

### MySQL ODBC

**Recommended Driver:** MySQL Connector/ODBC 8.0
**Latest Version:** 8.0.36 (as of 2024)
**ODBC URL Format:** `odbcapi+mysql://user:password@host:3306/database`

**Installation:**

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install libmyodbc unixodbc unixodbc-dev
```

**Linux (RHEL/CentOS):**
```bash
sudo yum install mysql-connector-odbc unixODBC unixODBC-devel
```

**macOS:**
```bash
brew install mysql-connector-odbc
```

**Windows:**
Download from https://dev.mysql.com/downloads/connector/odbc/

### MariaDB ODBC

**Recommended Driver:** MariaDB Connector/ODBC 3.1
**Latest Version:** 3.1.21 (as of 2024)
**ODBC URL Format:** `odbcapi+mariadb://user:password@host:3306/database`

**Installation:**

**Linux:**
```bash
# Download and install from MariaDB repository
wget https://downloads.mariadb.com/Connectors/odbc/connector-odbc-3.1.21/mariadb-connector-odbc-3.1.21-ga-debian-x86_64.tar.gz
tar -xzf mariadb-connector-odbc-3.1.21-ga-debian-x86_64.tar.gz
sudo cp lib/libmaodbc.so /usr/lib/
```

**macOS:**
```bash
brew tap mariadb/mariadb
brew install mariadb-connector-odbc
```

**Windows:**
Download from https://mariadb.com/downloads/connectors/odbc/

### Microsoft SQL Server ODBC

**Recommended Driver:** ODBC Driver 18 for SQL Server
**Latest Version:** 18.3.3.1 (as of 2024)
**ODBC URL Format:** `odbcapi+mssql://user:password@host:1433/database`

**Installation:**

**Linux (Ubuntu/Debian):**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev
```

**Linux (RHEL/CentOS):**
```bash
curl https://packages.microsoft.com/config/rhel/8/prod.repo | sudo tee /etc/yum.repos.d/mssql-release.repo
sudo yum remove unixODBC-utf16 unixODBC-utf16-devel
sudo ACCEPT_EULA=Y yum install -y msodbcsql18 unixODBC-devel
```

**macOS:**
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql18 mssql-tools18
```

**Windows:**
Download from https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### Oracle ODBC

**Recommended Driver:** Oracle Instant Client ODBC
**Latest Version:** 21.13 (as of 2024)
**ODBC URL Format:** `odbcapi+oracle://user:password@host:1521/service_name`

**Installation:**

**Linux:**
```bash
# Download Oracle Instant Client from oracle.com
# Extract files
unzip instantclient-basic-linux.x64-21.13.0.0.0dbru.zip
unzip instantclient-odbc-linux.x64-21.13.0.0.0dbru.zip

# Install
sudo sh -c "echo /opt/oracle/instantclient_21_13 > /etc/ld.so.conf.d/oracle-instantclient.conf"
sudo ldconfig

# Configure ODBC
cd /opt/oracle/instantclient_21_13
./odbc_update_ini.sh / /opt/oracle/instantclient_21_13
```

**macOS:**
Download from https://www.oracle.com/database/technologies/instant-client/macos-intel-x86-downloads.html

**Windows:**
Download from https://www.oracle.com/database/technologies/instant-client/winx64-64-downloads.html

## Driver Compatibility Matrix

### JDBC Driver Compatibility

| Database | JDBC Driver Version | Minimum DB Version | Maximum DB Version | Auto-Download | Production Ready |
|----------|--------------------|--------------------|--------------------|--------------|--------------------|
| PostgreSQL | 42.7.1 | 9.6 | 16.x | ✅ | ✅ |
| MySQL | 8.3.0 | 5.6 | 8.0 | ✅ | ✅ |
| MariaDB | 3.3.2 | 10.3 | 11.x | ✅ | ✅ |
| SQL Server | 12.6.0 | 2012 | 2022 | ✅ | ✅ |
| Oracle | 23.3.0 | 11g R2 | 23c | ✅ | ✅ |
| IBM DB2 | 11.5.9.0 | 11.1 | 11.5 | ✅ | ✅ |
| SQLite | 3.45.0.0 | 3.40 | 3.45 | ✅ | ✅ |
| OceanBase | 2.4.9 | 2.4 | 4.x | ✅ | ✅ |

### ODBC Driver Compatibility

| Database | ODBC Driver | Minimum DB Version | Maximum DB Version | Auto-Install | Production Ready |
|----------|-------------|--------------------|--------------------|--------------|-----------------|
| PostgreSQL | psqlODBC 16.0 | 9.6 | 16.x | ❌ | ✅ |
| MySQL | Connector/ODBC 8.0 | 5.6 | 8.0 | ❌ | ✅ |
| MariaDB | Connector/ODBC 3.1 | 10.3 | 11.x | ❌ | ✅ |
| SQL Server | ODBC Driver 18 | 2012 | 2022 | ❌ | ✅ |
| Oracle | Instant Client 21 | 11g R2 | 23c | ❌ | ✅ |

### SQLAlchemy Version Compatibility

| SQLAlchemy Version | Supported | Recommended |
|--------------------|-----------|-------------|
| 2.0.0 - 2.0.x | ✅ | ✅ |
| 1.4.x | ❌ | ❌ |
| 1.3.x and earlier | ❌ | ❌ |

### Python Version Compatibility

| Python Version | JDBC Support | ODBC Support | Recommended |
|----------------|--------------|--------------|-------------|
| 3.13 | ✅ | ✅ | ✅ |
| 3.12 | ✅ | ✅ | ✅ |
| 3.11 | ✅ | ✅ | ✅ |
| 3.10 | ✅ | ✅ | ✅ |
| 3.9 | ❌ | ❌ | ❌ |
| 3.8 and earlier | ❌ | ❌ | ❌ |

## Installation Instructions

### Quick Install with Auto-Download (JDBC)

```python
from sqlalchemy import create_engine

# Drivers auto-download on first use
engine = create_engine("jdbcapi+postgresql://localhost/mydb")
```

### Manual JDBC Driver Installation

```bash
# Download driver
wget https://jdbc.postgresql.org/download/postgresql-42.7.1.jar

# Set CLASSPATH
export CLASSPATH="/path/to/postgresql-42.7.1.jar:$CLASSPATH"

# Or add to shell profile
echo 'export CLASSPATH="/path/to/postgresql-42.7.1.jar:$CLASSPATH"' >> ~/.bashrc
```

### ODBC Driver Configuration

After installing ODBC driver, verify:

```bash
# List installed ODBC drivers
odbcinst -q -d

# Test ODBC connection
isql -v DSN_NAME username password
```

## Troubleshooting

### Check Driver Versions

**JDBC:**
```python
from sqlalchemy_jdbcapi.jdbc import list_cached_drivers

for driver in list_cached_drivers():
    print(driver)
```

**ODBC:**
```bash
odbcinst -q -d
```

### Update Drivers

**JDBC:**
```python
from sqlalchemy_jdbcapi.jdbc import download_driver, JDBCDriver

# Force download latest version
driver = JDBCDriver(
    group_id="org.postgresql",
    artifact_id="postgresql",
    version="42.7.1"
)
download_driver(driver, force=True)
```

**ODBC:**
Follow installation instructions for your platform to update.

## Additional Resources

- **PostgreSQL JDBC**: https://jdbc.postgresql.org/
- **MySQL Connector/J**: https://dev.mysql.com/downloads/connector/j/
- **MariaDB Connector/J**: https://mariadb.com/kb/en/about-mariadb-connector-j/
- **SQL Server JDBC**: https://learn.microsoft.com/en-us/sql/connect/jdbc/
- **Oracle JDBC**: https://www.oracle.com/database/technologies/appdev/jdbc-downloads.html
- **IBM DB2 JDBC**: https://www.ibm.com/support/pages/db2-jdbc-driver-versions-and-downloads
- **SQLite JDBC**: https://github.com/xerial/sqlite-jdbc
- **pyodbc Documentation**: https://github.com/mkleehammer/pyodbc/wiki

## Support

For driver-related issues:

1. Check driver compatibility matrix
2. Verify installation with provided commands
3. Review [USAGE.md](USAGE.md) for examples
4. Report issues at https://github.com/daneshpatel/sqlalchemy-jdbcapi/issues
