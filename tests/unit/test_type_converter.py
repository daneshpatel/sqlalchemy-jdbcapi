"""
Tests for JDBC type conversion.

Covers conversion between JDBC SQL types and Python types.
"""

from __future__ import annotations

import datetime
from unittest.mock import Mock

from sqlalchemy_jdbcapi.jdbc.type_converter import TypeConverter


class TestTypeConverterBasic:
    """Test basic type conversions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = TypeConverter()
        self.mock_resultset = Mock()

    def test_convert_null_value(self):
        """Test converting NULL values."""
        self.mock_resultset.getObject.return_value = None
        self.mock_resultset.wasNull.return_value = True

        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 12)

        assert result is None

    def test_convert_varchar_to_string(self):
        """Test converting VARCHAR to Python string."""
        self.mock_resultset.getObject.return_value = "test"
        self.mock_resultset.wasNull.return_value = False
        self.mock_resultset.getString.return_value = "test"

        # VARCHAR is type 12
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 12)

        assert result == "test"
        self.mock_resultset.getString.assert_called_once_with(1)

    def test_convert_char_to_string(self):
        """Test converting CHAR to Python string."""
        self.mock_resultset.getObject.return_value = "A"
        self.mock_resultset.wasNull.return_value = False
        self.mock_resultset.getString.return_value = "A"

        # CHAR is type 1
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 1)

        assert result == "A"

    def test_convert_longvarchar_to_string(self):
        """Test converting LONGVARCHAR to Python string."""
        self.mock_resultset.getObject.return_value = "long text"
        self.mock_resultset.wasNull.return_value = False
        self.mock_resultset.getString.return_value = "long text"

        # LONGVARCHAR is type -1
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, -1)

        assert result == "long text"


class TestTypeConverterNumeric:
    """Test numeric type conversions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = TypeConverter()
        self.mock_resultset = Mock()
        self.mock_resultset.wasNull.return_value = False

    def test_convert_integer(self):
        """Test converting INTEGER to Python int."""
        self.mock_resultset.getObject.return_value = 42
        self.mock_resultset.getLong.return_value = 42

        # INTEGER is type 4
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 4)

        assert result == 42
        assert isinstance(result, int)

    def test_convert_smallint(self):
        """Test converting SMALLINT to Python int."""
        self.mock_resultset.getObject.return_value = 100
        self.mock_resultset.getLong.return_value = 100

        # SMALLINT is type 5
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 5)

        assert result == 100

    def test_convert_bigint(self):
        """Test converting BIGINT to Python int."""
        self.mock_resultset.getObject.return_value = 9999999999
        self.mock_resultset.getLong.return_value = 9999999999

        # BIGINT is type -5
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, -5)

        assert result == 9999999999

    def test_convert_tinyint(self):
        """Test converting TINYINT to Python int."""
        self.mock_resultset.getObject.return_value = 1
        self.mock_resultset.getLong.return_value = 1

        # TINYINT is type -6
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, -6)

        assert result == 1

    def test_convert_integer_null(self):
        """Test converting NULL integer."""
        self.mock_resultset.getObject.return_value = 0
        self.mock_resultset.getLong.return_value = 0
        self.mock_resultset.wasNull.return_value = True

        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 4)

        # Should return None for NULL
        assert result is None

    def test_convert_numeric_decimal(self):
        """Test converting NUMERIC to Python float."""
        mock_bigdecimal = Mock()
        mock_bigdecimal.__str__ = Mock(return_value="123.45")

        self.mock_resultset.getObject.return_value = mock_bigdecimal
        self.mock_resultset.getBigDecimal.return_value = mock_bigdecimal

        # NUMERIC is type 2
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 2)

        assert result == 123.45
        assert isinstance(result, float)

    def test_convert_decimal(self):
        """Test converting DECIMAL to Python float."""
        mock_bigdecimal = Mock()
        mock_bigdecimal.__str__ = Mock(return_value="99.99")

        self.mock_resultset.getObject.return_value = mock_bigdecimal
        self.mock_resultset.getBigDecimal.return_value = mock_bigdecimal

        # DECIMAL is type 3
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 3)

        assert result == 99.99

    def test_convert_float(self):
        """Test converting FLOAT to Python float."""
        self.mock_resultset.getObject.return_value = 3.14
        self.mock_resultset.getDouble.return_value = 3.14

        # FLOAT is type 6
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 6)

        assert result == 3.14
        assert isinstance(result, float)

    def test_convert_real(self):
        """Test converting REAL to Python float."""
        self.mock_resultset.getObject.return_value = 2.718
        self.mock_resultset.getDouble.return_value = 2.718

        # REAL is type 7
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 7)

        assert result == 2.718

    def test_convert_double(self):
        """Test converting DOUBLE to Python float."""
        self.mock_resultset.getObject.return_value = 1.414
        self.mock_resultset.getDouble.return_value = 1.414

        # DOUBLE is type 8
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 8)

        assert result == 1.414


class TestTypeConverterBoolean:
    """Test boolean type conversions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = TypeConverter()
        self.mock_resultset = Mock()
        self.mock_resultset.wasNull.return_value = False

    def test_convert_bit_true(self):
        """Test converting BIT (true) to Python bool."""
        self.mock_resultset.getObject.return_value = True
        self.mock_resultset.getBoolean.return_value = True

        # BIT is type -7
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, -7)

        assert result is True
        assert isinstance(result, bool)

    def test_convert_bit_false(self):
        """Test converting BIT (false) to Python bool."""
        self.mock_resultset.getObject.return_value = False
        self.mock_resultset.getBoolean.return_value = False

        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, -7)

        assert result is False

    def test_convert_bit_null(self):
        """Test converting NULL BIT value."""
        self.mock_resultset.getObject.return_value = False
        self.mock_resultset.getBoolean.return_value = False
        self.mock_resultset.wasNull.return_value = True

        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, -7)

        # Should return None for NULL
        assert result is None


class TestTypeConverterDateTime:
    """Test date/time type conversions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = TypeConverter()
        self.mock_resultset = Mock()
        self.mock_resultset.wasNull.return_value = False

    def test_convert_date(self):
        """Test converting DATE to Python date."""
        # Mock Java Date
        mock_java_date = Mock()
        mock_java_date.getTime.return_value = (
            1640995200000  # 2022-01-01 in milliseconds
        )

        self.mock_resultset.getObject.return_value = mock_java_date
        self.mock_resultset.getDate.return_value = mock_java_date

        # DATE is type 91
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 91)

        assert isinstance(result, datetime.date)
        # The date conversion should work
        assert result.year == 2022

    def test_convert_time(self):
        """Test converting TIME to Python time."""
        # Mock Java Time
        mock_java_time = Mock()
        mock_java_time.getTime.return_value = 3661000  # 01:01:01 in milliseconds

        self.mock_resultset.getObject.return_value = mock_java_time
        self.mock_resultset.getTime.return_value = mock_java_time

        # TIME is type 92
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 92)

        assert isinstance(result, datetime.time)

    def test_convert_timestamp(self):
        """Test converting TIMESTAMP to Python datetime."""
        # Mock Java Timestamp
        mock_java_timestamp = Mock()
        mock_java_timestamp.getTime.return_value = 1640995200000
        mock_java_timestamp.getNanos.return_value = 0  # No nanosecond precision

        self.mock_resultset.getObject.return_value = mock_java_timestamp
        self.mock_resultset.getTimestamp.return_value = mock_java_timestamp

        # TIMESTAMP is type 93
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 93)

        assert isinstance(result, datetime.datetime)
        assert result.year == 2022

    def test_convert_date_null(self):
        """Test converting NULL date."""
        self.mock_resultset.getObject.return_value = None
        self.mock_resultset.wasNull.return_value = True

        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 91)

        assert result is None


class TestTypeConverterBinary:
    """Test binary type conversions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = TypeConverter()
        self.mock_resultset = Mock()
        self.mock_resultset.wasNull.return_value = False

    def test_convert_binary(self):
        """Test converting BINARY to Python bytes."""
        test_bytes = b"binary data"
        self.mock_resultset.getObject.return_value = test_bytes
        self.mock_resultset.getBytes.return_value = test_bytes

        # BINARY is type -2
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, -2)

        assert result == test_bytes
        assert isinstance(result, bytes)

    def test_convert_varbinary(self):
        """Test converting VARBINARY to Python bytes."""
        test_bytes = b"variable binary"
        self.mock_resultset.getObject.return_value = test_bytes
        self.mock_resultset.getBytes.return_value = test_bytes

        # VARBINARY is type -3
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, -3)

        assert result == test_bytes

    def test_convert_longvarbinary(self):
        """Test converting LONGVARBINARY to Python bytes."""
        test_bytes = b"long variable binary data"
        self.mock_resultset.getObject.return_value = test_bytes
        self.mock_resultset.getBytes.return_value = test_bytes

        # LONGVARBINARY is type -4
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, -4)

        assert result == test_bytes


class TestTypeConverterLOB:
    """Test LOB (Large Object) type conversions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = TypeConverter()
        self.mock_resultset = Mock()
        self.mock_resultset.wasNull.return_value = False

    def test_convert_blob(self):
        """Test converting BLOB to Python bytes."""
        # Mock Java Blob
        mock_blob = Mock()
        mock_blob.length.return_value = 10
        mock_blob.getBytes.return_value = b"blob data!"

        self.mock_resultset.getObject.return_value = mock_blob
        self.mock_resultset.getBlob.return_value = mock_blob

        # BLOB is type 2004
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 2004)

        assert result == b"blob data!"
        assert isinstance(result, bytes)

    def test_convert_clob(self):
        """Test converting CLOB to Python string."""
        # Mock Java Clob
        mock_clob = Mock()
        mock_clob.length.return_value = 10
        mock_clob.getSubString.return_value = "clob text!"

        self.mock_resultset.getObject.return_value = mock_clob
        self.mock_resultset.getClob.return_value = mock_clob

        # CLOB is type 2005
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 2005)

        assert result == "clob text!"
        assert isinstance(result, str)

    def test_convert_nclob(self):
        """Test converting NCLOB to Python string."""
        # Mock Java NClob - NCLOB uses getClob() method same as CLOB
        mock_nclob = Mock()
        mock_nclob.length.return_value = 12
        mock_nclob.getSubString.return_value = "nclob text!!"

        self.mock_resultset.getObject.return_value = mock_nclob
        # NCLOB and CLOB both use getClob()
        self.mock_resultset.getClob.return_value = mock_nclob

        # NCLOB is type 2011
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 2011)

        assert result == "nclob text!!"


class TestTypeConverterArray:
    """Test array type conversions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = TypeConverter()
        self.mock_resultset = Mock()
        self.mock_resultset.wasNull.return_value = False

    def test_convert_array(self):
        """Test converting SQL ARRAY to Python list."""
        # Mock Java Array
        mock_array = Mock()
        mock_array.getArray.return_value = [1, 2, 3, 4, 5]

        self.mock_resultset.getObject.return_value = mock_array

        # Array doesn't have a specific type code, detected by hasattr
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 2003)

        assert result == [1, 2, 3, 4, 5]
        assert isinstance(result, list)


class TestTypeConverterEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = TypeConverter()
        self.mock_resultset = Mock()

    def test_unknown_type_fallback(self):
        """Test fallback to getObject for unknown types."""
        self.mock_resultset.getObject.return_value = "unknown type value"
        self.mock_resultset.wasNull.return_value = False

        # Use an unknown type code
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 9999)

        # Should just return the value as-is
        assert result == "unknown type value"

    def test_conversion_error_fallback(self):
        """Test fallback on conversion error."""
        self.mock_resultset.getObject.return_value = "value"
        self.mock_resultset.wasNull.return_value = False
        self.mock_resultset.getString.side_effect = Exception("Conversion error")

        # Try to convert VARCHAR, but it fails - should fallback to getObject
        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 12)

        # Fallback should return the getObject value
        assert result == "value"

    def test_jdbc_types_mapping(self):
        """Test JDBC type constants mapping."""
        # Just verify some key mappings exist
        assert TypeConverter.JDBC_TYPES[4] == "INTEGER"
        assert TypeConverter.JDBC_TYPES[12] == "VARCHAR"
        assert TypeConverter.JDBC_TYPES[91] == "DATE"
        assert TypeConverter.JDBC_TYPES[2004] == "BLOB"
        assert TypeConverter.JDBC_TYPES[-7] == "BIT"

    def test_decimal_null_handling(self):
        """Test DECIMAL NULL handling."""
        self.mock_resultset.getObject.return_value = None
        self.mock_resultset.getBigDecimal.return_value = None
        self.mock_resultset.wasNull.return_value = True

        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 2)

        assert result is None

    def test_blob_null_handling(self):
        """Test BLOB NULL handling."""
        self.mock_resultset.getObject.return_value = None
        self.mock_resultset.wasNull.return_value = True

        result = self.converter.convert_from_jdbc(self.mock_resultset, 1, 2004)

        assert result is None
