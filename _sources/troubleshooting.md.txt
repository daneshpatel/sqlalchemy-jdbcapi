# Troubleshooting Guide

Common issues and solutions for SQLAlchemy JDBC/ODBC API.

## Table of Contents

- [JPype Issues](#jpype-issues)
- [JDBC Connection Issues](#jdbc-connection-issues)
- [Driver Issues](#driver-issues)
- [Database-Specific Issues](#database-specific-issues)
- [Performance Issues](#performance-issues)

## JPype Issues

### JPype 1.6.0 Compatibility Error

**Error:**
```
RuntimeError: Can't find org.jpype.jar support library
```

**Cause:** JPype 1.6.0 has a bug where it cannot find its required jar file.

**Solution:** Downgrade to JPype 1.5.0

```bash
# Uninstall current version
pip uninstall -y JPype1

# Install working version
pip install JPype1==1.5.0
```

**Verification:**
```python
import jpype
jpype.startJVM()
print("JVM started successfully")
jpype.shutdownJVM()
```

### JVM Already Started Error

**Error:**
```
JVMNotStartedError: JVM is already running
```

**Cause:** The JVM can only be started once per Python process.

**Solution:** Don't call `start_jvm()` multiple times:

```python
from sqlalchemy_jdbcapi.jdbc import start_jvm, is_jvm_started

# Check before starting
if not is_jvm_started():
    start_jvm(auto_download=True, databases=["postgresql"])

# Now create engines
```

### Java Not Found Error

**Error:**
```
JVMNotFoundException: No JVM shared library file found
```

**Cause:** Java is not installed or not in PATH.

**Solution:** Install Java Runtime:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y openjdk-17-jre
```

**macOS:**
```bash
brew install openjdk@17
```

**Windows:**
Download and install from [Adoptium](https://adoptium.net/)

**Verify Java installation:**
```bash
java -version
# Should show: openjdk version "17.x.x" or similar
```

## JDBC Connection Issues

### Cannot Commit When autoCommit is Enabled

**Error:**
```
PSQLException: Cannot commit when autoCommit is enabled
```

**Cause:** JDBC connections have auto-commit enabled by default.

**Solution:** Disable auto-commit after creating connection:

```python
from sqlalchemy_jdbcapi.jdbc import connect

conn = connect(
    jclassname="org.postgresql.Driver",
    url="jdbc:postgresql://localhost:5432/mydb",
    driver_args=["user", "password"]
)

# Disable auto-commit for transaction support
conn.set_auto_commit(False)

# Now you can use transactions
cursor = conn.cursor()
cursor.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
conn.commit()  # This will work now
```

### Connection Timeout

**Error:**
```
DatabaseError: Connection timeout
```

**Cause:** Database server is not reachable or too slow to respond.

**Solution:** Increase timeout or check network:

```python
from sqlalchemy import create_engine

# Add timeout parameter
engine = create_engine(
    'jdbcapi+postgresql://user:pass@localhost:5432/mydb',
    connect_args={'timeout': 30}  # 30 seconds
)
```

**Check database connectivity:**
```bash
# PostgreSQL
psql -h localhost -p 5432 -U user -d mydb

# MySQL
mysql -h localhost -P 3306 -u user -p mydb

# Test port connectivity
telnet localhost 5432
```

### Authentication Failed

**Error:**
```
DatabaseError: authentication failed for user "username"
```

**Solutions:**

1. **Check credentials:**
   ```python
   # Make sure username and password are correct
   engine = create_engine('jdbcapi+postgresql://user:password@localhost/mydb')
   ```

2. **Check database permissions:**
   ```sql
   -- PostgreSQL
   GRANT ALL PRIVILEGES ON DATABASE mydb TO user;

   -- MySQL
   GRANT ALL PRIVILEGES ON mydb.* TO 'user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Check pg_hba.conf (PostgreSQL):**
   ```
   # Allow local connections
   host    all    all    127.0.0.1/32    md5
   ```

## Driver Issues

### JDBC Driver Not Found

**Error:**
```
No JDBC drivers found in classpath. Set CLASSPATH environment variable or enable auto_download.
```

**Solution 1: Enable auto-download (recommended)**
```python
from sqlalchemy_jdbcapi.jdbc import start_jvm

start_jvm(auto_download=True, databases=["postgresql"])
```

**Solution 2: Manual driver setup**
```bash
# Download driver manually
wget https://jdbc.postgresql.org/download/postgresql-42.7.1.jar

# Set CLASSPATH
export CLASSPATH="/path/to/postgresql-42.7.1.jar"
```

**Solution 3: Place in cache directory**
```bash
# Create cache directory
mkdir -p ~/.sqlalchemy-jdbcapi/drivers/

# Copy driver
cp postgresql-42.7.1.jar ~/.sqlalchemy-jdbcapi/drivers/
```

### Driver Download Failed

**Error:**
```
RuntimeError: Failed to download driver from Maven Central
```

**Cause:** Network connectivity issues or Maven Central is down.

**Solutions:**

1. **Check internet connectivity:**
   ```bash
   curl -I https://repo1.maven.org/maven2/
   ```

2. **Download manually:**
   ```bash
   # PostgreSQL
   wget https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.1/postgresql-42.7.1.jar

   # MySQL
   wget https://repo1.maven.org/maven2/com/mysql/mysql-connector-j/8.3.0/mysql-connector-j-8.3.0.jar

   # Place in cache
   mv *.jar ~/.sqlalchemy-jdbcapi/drivers/
   ```

3. **Use proxy:**
   ```bash
   export HTTP_PROXY=http://proxy.example.com:8080
   export HTTPS_PROXY=http://proxy.example.com:8080
   ```

### ODBC Driver Not Found

**Error:**
```
Error: Data source name not found and no default driver specified
```

**Cause:** ODBC driver is not installed.

**Solutions:**

**PostgreSQL ODBC (Ubuntu/Debian):**
```bash
sudo apt-get install -y unixodbc odbc-postgresql
```

**MySQL ODBC (Ubuntu/Debian):**
```bash
sudo apt-get install -y unixodbc libmyodbc
```

**SQL Server ODBC (Ubuntu/Debian):**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

**Verify ODBC drivers:**
```bash
# List installed drivers
odbcinst -q -d
```

## Database-Specific Issues

### PostgreSQL: Role Does Not Exist

**Error:**
```
PSQLException: FATAL: role "username" does not exist
```

**Solution:**
```sql
-- Create role/user
CREATE ROLE username WITH LOGIN PASSWORD 'password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE mydb TO username;
```

### MySQL: Unknown Database

**Error:**
```
Unknown database 'mydb'
```

**Solution:**
```sql
-- Create database
CREATE DATABASE mydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant access
GRANT ALL PRIVILEGES ON mydb.* TO 'username'@'localhost';
FLUSH PRIVILEGES;
```

### Oracle: TNS Could Not Resolve

**Error:**
```
ORA-12154: TNS:could not resolve the connect identifier specified
```

**Solutions:**

1. **Use host:port/service format:**
   ```python
   engine = create_engine('jdbcapi+oracle://user:pass@localhost:1521/ORCL')
   ```

2. **Configure tnsnames.ora:**
   ```
   MYDB =
     (DESCRIPTION =
       (ADDRESS = (PROTOCOL = TCP)(HOST = localhost)(PORT = 1521))
       (CONNECT_DATA =
         (SERVER = DEDICATED)
         (SERVICE_NAME = ORCL)
       )
     )
   ```

3. **Set TNS_ADMIN environment variable:**
   ```bash
   export TNS_ADMIN=/path/to/tnsnames/directory
   ```

### SQL Server: SSL Connection Required

**Error:**
```
The server was not found or was not accessible
```

**Solution:** Add encryption parameters:
```python
from sqlalchemy import create_engine

engine = create_engine(
    'jdbcapi+mssql://user:pass@localhost:1433/mydb?'
    'encrypt=true&trustServerCertificate=true'
)
```

## Performance Issues

### Slow Connection Initialization

**Symptom:** First connection takes several seconds.

**Causes & Solutions:**

1. **JVM startup time:**
   - Normal for first connection
   - Subsequent connections are faster
   - Consider keeping JVM running

2. **Driver download:**
   - Only happens once
   - Drivers are cached in `~/.sqlalchemy-jdbcapi/drivers/`
   - Pre-download drivers:
     ```python
     from sqlalchemy_jdbcapi.jdbc import start_jvm
     start_jvm(auto_download=True, databases=["postgresql", "mysql"])
     ```

3. **DNS resolution:**
   - Use IP address instead of hostname
   - Configure `/etc/hosts`

### Slow Query Performance

**Solutions:**

1. **Use connection pooling:**
   ```python
   from sqlalchemy import create_engine
   from sqlalchemy.pool import QueuePool

   engine = create_engine(
       'jdbcapi+postgresql://user:pass@localhost/mydb',
       poolclass=QueuePool,
       pool_size=5,
       max_overflow=10
   )
   ```

2. **Disable echo:**
   ```python
   engine = create_engine('jdbcapi+postgresql://...', echo=False)
   ```

3. **Use batch operations:**
   ```python
   # Instead of many individual inserts
   data = [{"name": "Alice"}, {"name": "Bob"}, {"name": "Charlie"}]
   conn.execute(users.insert(), data)
   ```

### Memory Issues with Large Results

**Error:**
```
MemoryError: Unable to allocate array
```

**Solutions:**

1. **Use server-side cursors (PostgreSQL):**
   ```python
   with engine.connect() as conn:
       result = conn.execution_options(stream_results=True).execute(
           text("SELECT * FROM large_table")
       )
       for row in result:
           process(row)
   ```

2. **Fetch in batches:**
   ```python
   cursor = conn.connection.cursor()
   cursor.execute("SELECT * FROM large_table")

   while True:
       rows = cursor.fetchmany(1000)
       if not rows:
           break
       process_batch(rows)
   ```

3. **Use LIMIT and OFFSET:**
   ```python
   batch_size = 1000
   offset = 0

   while True:
       result = conn.execute(
           text(f"SELECT * FROM large_table LIMIT {batch_size} OFFSET {offset}")
       )
       rows = result.fetchall()
       if not rows:
           break
       process_batch(rows)
       offset += batch_size
   ```

## Testing Issues

### Docker Database Connection Failed

**Error:**
```
Connection refused: localhost:5432
```

**Solutions:**

1. **Check container is running:**
   ```bash
   docker ps
   # Should show database container
   ```

2. **Wait for database to be ready:**
   ```bash
   # PostgreSQL
   docker-compose -f docker-compose.test.yml ps
   # Wait until status shows "(healthy)"

   # Or wait manually
   sleep 10
   ```

3. **Check port mapping:**
   ```bash
   docker port test-postgres-14
   # Should show: 5432/tcp -> 0.0.0.0:5432
   ```

4. **Check logs:**
   ```bash
   docker logs test-postgres-14
   ```

### Tests Pass Individually but Fail Together

**Cause:** JVM can only start once per Python process.

**Solution:** Use pytest fixtures:

```python
# conftest.py
import pytest
from sqlalchemy_jdbcapi.jdbc import start_jvm, is_jvm_started

@pytest.fixture(scope="session", autouse=True)
def initialize_jvm():
    """Initialize JVM once for all tests."""
    if not is_jvm_started():
        start_jvm(auto_download=True, databases=["postgresql"])
    yield
```

## Getting Help

If you're still experiencing issues:

1. **Check GitHub Issues:**
   - https://github.com/daneshpatel/sqlalchemy-jdbcapi/issues
   - Search for similar problems

2. **Enable debug logging:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Create detailed issue report:**
   - Python version: `python --version`
   - Package version: `pip show sqlalchemy-jdbcapi`
   - JPype version: `pip show JPype1`
   - Java version: `java -version`
   - Database and version
   - Full error traceback
   - Minimal reproducible example

4. **Check documentation:**
   - [Quick Start Guide](quickstart.md)
   - [Drivers Guide](drivers.md)
   - [Usage Guide](usage.md)
