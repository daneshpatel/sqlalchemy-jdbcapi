"""
Type conversion between JDBC and Python types.
"""

from __future__ import annotations

import datetime
import logging
from typing import Any

logger = logging.getLogger(__name__)


class TypeConverter:
    """
    Handles conversion between JDBC SQL types and Python types.

    Java SQL Types (from java.sql.Types):
    -7  BIT
    -6  TINYINT
    -5  BIGINT
    -4  LONGVARBINARY
    -3  VARBINARY
    -2  BINARY
    -1  LONGVARCHAR
    1   CHAR
    2   NUMERIC
    3   DECIMAL
    4   INTEGER
    5   SMALLINT
    6   FLOAT
    7   REAL
    8   DOUBLE
    12  VARCHAR
    91  DATE
    92  TIME
    93  TIMESTAMP
    2004 BLOB
    2005 CLOB
    2011 NCLOB
    """

    # SQL Type constants (from java.sql.Types)
    JDBC_TYPES = {
        -7: "BIT",
        -6: "TINYINT",
        -5: "BIGINT",
        -4: "LONGVARBINARY",
        -3: "VARBINARY",
        -2: "BINARY",
        -1: "LONGVARCHAR",
        1: "CHAR",
        2: "NUMERIC",
        3: "DECIMAL",
        4: "INTEGER",
        5: "SMALLINT",
        6: "FLOAT",
        7: "REAL",
        8: "DOUBLE",
        12: "VARCHAR",
        91: "DATE",
        92: "TIME",
        93: "TIMESTAMP",
        2004: "BLOB",
        2005: "CLOB",
        2011: "NCLOB",
    }

    def convert_from_jdbc(  # noqa: C901 - Type conversion requires complexity
        self, resultset: Any, column_index: int, sql_type: int
    ) -> Any:
        """
        Convert JDBC result to Python type.

        Args:
            resultset: JDBC ResultSet object
            column_index: 1-based column index
            sql_type: JDBC SQL type code

        Returns:
            Python value
        """
        try:
            # First check if the value is NULL
            # We have to call getObject first to trigger wasNull() properly
            value = resultset.getObject(column_index)
            if value is None or resultset.wasNull():
                return None

            # String types
            if sql_type in (1, 12, -1):  # CHAR, VARCHAR, LONGVARCHAR
                return self._convert_string(resultset, column_index)

            # Numeric types
            if sql_type in (
                -6,
                5,
                4,
                -5,
            ):  # TINYINT, SMALLINT, INTEGER, BIGINT
                return self._convert_int(resultset, column_index)

            if sql_type in (2, 3):  # NUMERIC, DECIMAL
                return self._convert_decimal(resultset, column_index)

            if sql_type in (6, 7, 8):  # FLOAT, REAL, DOUBLE
                return self._convert_float(resultset, column_index)

            # Boolean
            if sql_type == -7:  # BIT
                return self._convert_boolean(resultset, column_index)

            # Date/Time types
            if sql_type == 91:  # DATE
                return self._convert_date(resultset, column_index)

            if sql_type == 92:  # TIME
                return self._convert_time(resultset, column_index)

            if sql_type == 93:  # TIMESTAMP
                return self._convert_timestamp(resultset, column_index)

            # Binary types
            if sql_type in (-4, -3, -2):  # LONGVARBINARY, VARBINARY, BINARY
                return self._convert_binary(resultset, column_index)

            # LOB types
            if sql_type == 2004:  # BLOB
                return self._convert_blob(resultset, column_index)

            if sql_type in (2005, 2011):  # CLOB, NCLOB
                return self._convert_clob(resultset, column_index)

            # Array type (PostgreSQL, Oracle)
            if hasattr(value, "getArray"):
                return self._convert_array(value)

            # Default: return as-is
            logger.debug(
                f"Unknown SQL type {sql_type} "
                f"({self.JDBC_TYPES.get(sql_type, 'UNKNOWN')}), "
                f"returning as-is"
            )
            return value

        except Exception as e:
            logger.warning(
                f"Type conversion failed for column {column_index}, "
                f"type {sql_type}: {e}"
            )
            # Fallback to getObject
            return resultset.getObject(column_index)

    def _convert_string(self, resultset: Any, column_index: int) -> str | None:
        """Convert to Python string."""
        value = resultset.getString(column_index)
        return value if value is not None else None

    def _convert_int(self, resultset: Any, column_index: int) -> int | None:
        """Convert to Python int."""
        value = resultset.getLong(column_index)
        return value if not resultset.wasNull() else None

    def _convert_decimal(self, resultset: Any, column_index: int) -> float | None:
        """Convert decimal to Python float or decimal."""
        value = resultset.getBigDecimal(column_index)
        if value is None or resultset.wasNull():
            return None
        # Convert Java BigDecimal to Python float
        # Could use decimal.Decimal for precision, but float is more common
        return float(str(value))

    def _convert_float(self, resultset: Any, column_index: int) -> float | None:
        """Convert to Python float."""
        value = resultset.getDouble(column_index)
        return value if not resultset.wasNull() else None

    def _convert_boolean(self, resultset: Any, column_index: int) -> bool | None:
        """Convert to Python bool."""
        value = resultset.getBoolean(column_index)
        return value if not resultset.wasNull() else None

    def _convert_date(self, resultset: Any, column_index: int) -> datetime.date | None:
        """Convert to Python date."""
        value = resultset.getDate(column_index)
        if value is None or resultset.wasNull():
            return None

        # Convert java.sql.Date to Python date
        try:
            # Get the timestamp in milliseconds
            timestamp_ms = value.getTime()
            # Convert to seconds
            timestamp_s = timestamp_ms / 1000.0
            # Create Python datetime and extract date
            return datetime.datetime.fromtimestamp(timestamp_s).date()
        except Exception as e:
            logger.warning(f"Date conversion failed: {e}")
            return None

    def _convert_time(self, resultset: Any, column_index: int) -> datetime.time | None:
        """Convert to Python time."""
        value = resultset.getTime(column_index)
        if value is None or resultset.wasNull():
            return None

        try:
            timestamp_ms = value.getTime()
            timestamp_s = timestamp_ms / 1000.0
            return datetime.datetime.fromtimestamp(timestamp_s).time()
        except Exception as e:
            logger.warning(f"Time conversion failed: {e}")
            return None

    def _convert_timestamp(
        self, resultset: Any, column_index: int
    ) -> datetime.datetime | None:
        """Convert to Python datetime."""
        value = resultset.getTimestamp(column_index)
        if value is None or resultset.wasNull():
            return None

        try:
            timestamp_ms = value.getTime()
            timestamp_s = timestamp_ms / 1000.0
            # Get nanoseconds for microsecond precision
            nanos = value.getNanos()
            micros = nanos // 1000
            dt = datetime.datetime.fromtimestamp(timestamp_s)
            # Replace microseconds
            return dt.replace(microsecond=micros % 1000000)
        except Exception as e:
            logger.warning(f"Timestamp conversion failed: {e}")
            return None

    def _convert_binary(self, resultset: Any, column_index: int) -> bytes | None:
        """Convert to Python bytes."""
        value = resultset.getBytes(column_index)
        if value is None or resultset.wasNull():
            return None
        return bytes(value)

    def _convert_blob(self, resultset: Any, column_index: int) -> bytes | None:
        """Convert BLOB to Python bytes."""
        blob = resultset.getBlob(column_index)
        if blob is None or resultset.wasNull():
            return None

        try:
            length = blob.length()
            return bytes(blob.getBytes(1, length))
        except Exception as e:
            logger.warning(f"BLOB conversion failed: {e}")
            return None

    def _convert_clob(self, resultset: Any, column_index: int) -> str | None:
        """Convert CLOB to Python string."""
        clob = resultset.getClob(column_index)
        if clob is None or resultset.wasNull():
            return None

        try:
            length = clob.length()
            return clob.getSubString(1, length)
        except Exception as e:
            # Fallback: try reading as stream
            try:
                reader = clob.getCharacterStream()
                chars = []
                while True:
                    char = reader.read()
                    if char == -1:
                        break
                    chars.append(chr(char))
                return "".join(chars)
            except Exception as e2:
                logger.warning(f"CLOB conversion failed: {e}, {e2}")
                return None

    def _convert_array(self, array: Any) -> list[Any] | None:
        """Convert SQL Array to Python list."""
        try:
            # Call getArray() on the java.sql.Array object
            java_array = array.getArray()
            if java_array is None:
                return None

            # Convert to Python list
            return list(java_array)
        except Exception as e:
            logger.warning(f"Array conversion failed: {e}")
            return None
