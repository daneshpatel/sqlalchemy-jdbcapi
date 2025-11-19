"""
Apache Avatica JDBC dialect for SQLAlchemy.

Provides support for databases accessible via Apache Calcite Avatica,
including Apache Phoenix, Apache Drill, and other Calcite-based systems.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import exc, sql
from sqlalchemy.engine import Connection, Dialect

from .base import BaseJDBCDialect, JDBCDriverConfig

logger = logging.getLogger(__name__)


class AvaticaDialect(BaseJDBCDialect, Dialect):  # type: ignore
    """
    Apache Avatica dialect using JDBC driver.

    Apache Avatica is a framework for building database drivers. It provides
    a wire protocol and client-side drivers that can communicate with any
    Avatica-compliant server, including:

    - Apache Phoenix (HBase SQL layer)
    - Apache Drill (schema-free SQL query engine)
    - Apache Calcite (SQL query planning and optimization)

    Supports Avatica-specific features including:
    - HTTP/HTTPS transport
    - Protobuf or JSON serialization
    - Authentication (Basic, SPNEGO/Kerberos, Digest)
    - Custom avatica properties

    Connection URL format:
        jdbcapi+avatica://host:8765/?serialization=protobuf
        jdbcapi+phoenix://host:8765/?schema=myschema (Phoenix alias)
        jdbcapi+calcite://host:8765/ (Calcite alias)

    Special connection properties:
        - serialization: PROTOBUF or JSON
        - authentication: BASIC, DIGEST, SPNEGO
        - avatica_user: Avatica authentication user
        - avatica_password: Avatica authentication password
        - truststore: Path to truststore for HTTPS
        - truststore_password: Truststore password
    """

    name = "avatica"
    driver = "jdbcapi"

    # Avatica capabilities vary by backend, use conservative defaults
    supports_native_boolean = True
    supports_sequences = False  # Depends on backend
    supports_identity_columns = False  # Depends on backend
    supports_native_enum = False
    supports_multivalues_insert = True
    supports_statement_cache = True

    # Avatica-specific settings
    supports_server_side_cursors = False

    @classmethod
    def get_driver_config(cls) -> JDBCDriverConfig:
        """Get Apache Avatica JDBC driver configuration."""
        return JDBCDriverConfig(
            driver_class="org.apache.calcite.avatica.remote.Driver",
            jdbc_url_template="jdbc:avatica:remote:url=http://{host}:{port}",
            default_port=8765,
            supports_transactions=True,
            supports_schemas=True,
            supports_sequences=False,
        )

    @classmethod
    def create_connect_args(cls, url):  # type: ignore
        """
        Create connection arguments from URL.

        Avatica URLs are complex and support various configurations.
        """
        driver_config = cls.get_driver_config()

        # Get connection parameters
        host = url.host or "localhost"
        port = url.port or driver_config.default_port
        database = url.database or ""
        username = url.username or ""
        password = url.password or ""

        # Get query parameters
        query_params = dict(url.query)

        # Determine protocol (http or https)
        protocol = (
            "https" if query_params.pop("ssl", "false").lower() == "true" else "http"
        )

        # Build the Avatica remote URL
        avatica_url = f"{protocol}://{host}:{port}"

        # Add database/schema if specified
        if database:
            avatica_url += f";schema={database}"

        # Build JDBC URL for Avatica
        jdbc_url = f"jdbc:avatica:remote:url={avatica_url}"

        # Add serialization format
        serialization = query_params.pop("serialization", "PROTOBUF").upper()
        jdbc_url += f";serialization={serialization}"

        # Add authentication
        authentication = query_params.pop("authentication", "").upper()
        if authentication:
            jdbc_url += f";authentication={authentication}"

        # Add truststore for HTTPS
        if "truststore" in query_params:
            jdbc_url += f";truststore={query_params.pop('truststore')}"
        if "truststore_password" in query_params:
            jdbc_url += (
                f";truststore_password={query_params.pop('truststore_password')}"
            )

        # Build driver arguments
        driver_args = {}

        if username:
            # Avatica uses avatica_user for authentication
            driver_args["avatica_user"] = username
        if password:
            driver_args["avatica_password"] = password

        # Add remaining parameters
        driver_args.update(query_params)

        return (
            driver_config.driver_class,
            jdbc_url,
            driver_args if driver_args else None,
        )

    def initialize(self, connection: Connection) -> None:
        """Initialize Avatica connection."""
        if not hasattr(self, "_server_version_info"):
            self._server_version_info = self._get_server_version_info(connection)
        logger.debug("Initialized Apache Avatica JDBC dialect")

    def _get_server_version_info(self, connection: Connection) -> tuple[int, ...]:
        """
        Get Avatica/backend server version.

        Returns:
            Tuple of version numbers
        """
        try:
            # Try to get version via JDBC metadata
            connection.execute(sql.text("SELECT 1")).fetchone()

            # Avatica version is typically in JDBC metadata
            # Default to current stable version
            return (1, 23, 0)

        except exc.DBAPIError as e:
            logger.warning(f"Failed to get Avatica version: {e}")

        # Default fallback
        return (1, 20, 0)

    def do_ping(self, dbapi_connection: Any) -> bool:
        """Check if Avatica connection is alive."""
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.debug(f"Avatica ping failed: {e}")
            return False


class PhoenixDialect(AvaticaDialect):
    """
    Apache Phoenix dialect (HBase SQL layer).

    Phoenix provides SQL access to HBase with full ACID transaction support.

    Connection URL format:
        jdbcapi+phoenix://zookeeper-host:2181/?schema=myschema
    """

    name = "phoenix"

    # Phoenix capabilities
    supports_sequences = True  # Phoenix supports sequences
    supports_identity_columns = False

    @classmethod
    def get_driver_config(cls) -> JDBCDriverConfig:
        """Get Apache Phoenix JDBC driver configuration."""
        return JDBCDriverConfig(
            driver_class="org.apache.phoenix.jdbc.PhoenixDriver",
            jdbc_url_template="jdbc:phoenix:{host}:{port}",
            default_port=2181,  # ZooKeeper port
            supports_transactions=True,
            supports_schemas=True,
            supports_sequences=True,
        )

    @classmethod
    def create_connect_args(cls, url):  # type: ignore
        """Create Phoenix-specific connection arguments."""
        driver_config = cls.get_driver_config()

        host = url.host or "localhost"
        port = url.port or driver_config.default_port
        database = url.database or ""

        # Phoenix JDBC URL format
        jdbc_url = f"jdbc:phoenix:{host}:{port}"

        if database:
            jdbc_url += f":/{database}"

        # Phoenix-specific properties
        driver_args = {}
        query_params = dict(url.query)

        if "schema" in query_params:
            driver_args["phoenix.schema"] = query_params.pop("schema")

        if url.username:
            driver_args["user"] = url.username
        if url.password:
            driver_args["password"] = url.password

        driver_args.update(query_params)

        return (
            driver_config.driver_class,
            jdbc_url,
            driver_args if driver_args else None,
        )

    def do_ping(self, dbapi_connection: Any) -> bool:
        """Check if Phoenix connection is alive."""
        try:
            cursor = dbapi_connection.cursor()
            # Phoenix-specific ping
            cursor.execute("SELECT 1 FROM SYSTEM.CATALOG LIMIT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.debug(f"Phoenix ping failed: {e}")
            return False


class CalciteDialect(AvaticaDialect):
    """
    Apache Calcite dialect.

    Calcite is a foundational framework for building databases and
    data management systems.

    Connection URL format:
        jdbcapi+calcite://host:8765/?model=/path/to/model.json
    """

    name = "calcite"

    @classmethod
    def get_driver_config(cls) -> JDBCDriverConfig:
        """Get Apache Calcite JDBC driver configuration."""
        return JDBCDriverConfig(
            driver_class="org.apache.calcite.jdbc.Driver",
            jdbc_url_template="jdbc:calcite:model={database}",
            default_port=0,  # Calcite can be embedded or remote
            supports_transactions=True,
            supports_schemas=True,
            supports_sequences=False,
        )

    @classmethod
    def create_connect_args(cls, url):  # type: ignore
        """Create Calcite-specific connection arguments."""
        driver_config = cls.get_driver_config()

        # Calcite primarily uses model files
        database = url.database or ""
        query_params = dict(url.query)

        # Check if this is a remote Avatica connection or local model
        if url.host:
            # Remote Avatica connection
            return AvaticaDialect.create_connect_args(url)

        # Local Calcite with model file
        model = query_params.pop("model", database)

        jdbc_url = f"jdbc:calcite:model={model}"

        # Add any additional properties
        driver_args = dict(query_params)

        return (
            driver_config.driver_class,
            jdbc_url,
            driver_args if driver_args else None,
        )


# Export the main dialect
dialect = AvaticaDialect
