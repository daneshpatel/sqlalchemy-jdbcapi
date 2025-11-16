"""
DataFrame integration for pandas, polars, and Apache Arrow.

This module provides utilities to convert JDBC query results directly
into DataFrames for data science and ML workflows.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .cursor import Cursor

logger = logging.getLogger(__name__)


def cursor_to_pandas(cursor: Cursor) -> Any:
    """
    Convert cursor results to pandas DataFrame.

    Args:
        cursor: Cursor with executed query

    Returns:
        pandas.DataFrame

    Raises:
        ImportError: If pandas is not installed
        ValueError: If cursor has no results

    Example:
        >>> cursor.execute("SELECT * FROM users")
        >>> df = cursor_to_pandas(cursor)
        >>> print(df.head())
    """
    try:
        import pandas as pd
    except ImportError as e:
        raise ImportError(
            "pandas is not installed. Install with: pip install pandas"
        ) from e

    if cursor.description is None:
        raise ValueError("Cursor has no result set")

    # Get column names
    columns = [desc[0] for desc in cursor.description]

    # Fetch all rows
    rows = cursor.fetchall()

    # Create DataFrame
    df = pd.DataFrame(rows, columns=columns)
    logger.debug(f"Created pandas DataFrame with shape {df.shape}")

    return df


def cursor_to_polars(cursor: Cursor) -> Any:
    """
    Convert cursor results to polars DataFrame.

    Args:
        cursor: Cursor with executed query

    Returns:
        polars.DataFrame

    Raises:
        ImportError: If polars is not installed
        ValueError: If cursor has no results

    Example:
        >>> cursor.execute("SELECT * FROM users")
        >>> df = cursor_to_polars(cursor)
        >>> print(df.head())
    """
    try:
        import polars as pl
    except ImportError as e:
        raise ImportError(
            "polars is not installed. Install with: pip install polars"
        ) from e

    if cursor.description is None:
        raise ValueError("Cursor has no result set")

    # Get column names
    columns = [desc[0] for desc in cursor.description]

    # Fetch all rows
    rows = cursor.fetchall()

    # Create DataFrame from dict of lists
    data = {col: [row[i] for row in rows] for i, col in enumerate(columns)}
    df = pl.DataFrame(data)
    logger.debug(f"Created polars DataFrame with shape {df.shape}")

    return df


def cursor_to_arrow(cursor: Cursor) -> Any:
    """
    Convert cursor results to Apache Arrow Table.

    Args:
        cursor: Cursor with executed query

    Returns:
        pyarrow.Table

    Raises:
        ImportError: If pyarrow is not installed
        ValueError: If cursor has no results

    Example:
        >>> cursor.execute("SELECT * FROM users")
        >>> table = cursor_to_arrow(cursor)
        >>> print(table.schema)
    """
    try:
        import pyarrow as pa
    except ImportError as e:
        raise ImportError(
            "pyarrow is not installed. Install with: pip install pyarrow"
        ) from e

    if cursor.description is None:
        raise ValueError("Cursor has no result set")

    # Get column names
    columns = [desc[0] for desc in cursor.description]

    # Fetch all rows
    rows = cursor.fetchall()

    # Convert to Arrow Table
    # Build column arrays
    if not rows:
        # Empty result
        arrays = [pa.array([]) for _ in columns]
    else:
        # Transpose rows to columns
        col_data = [[row[i] for row in rows] for i in range(len(columns))]
        arrays = [pa.array(col) for col in col_data]

    table = pa.Table.from_arrays(arrays, names=columns)
    logger.debug(f"Created Arrow Table with {table.num_rows} rows")

    return table


def cursor_to_dict(cursor: Cursor) -> list[dict[str, Any]]:
    """
    Convert cursor results to list of dictionaries.

    Args:
        cursor: Cursor with executed query

    Returns:
        List of row dictionaries

    Example:
        >>> cursor.execute("SELECT * FROM users")
        >>> rows = cursor_to_dict(cursor)
        >>> print(rows[0])
        {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}
    """
    if cursor.description is None:
        raise ValueError("Cursor has no result set")

    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    return [dict(zip(columns, row)) for row in rows]


# Add convenience methods to Cursor class
def _add_dataframe_methods() -> None:
    """Add DataFrame methods to Cursor class."""
    from .cursor import Cursor

    # Add methods
    Cursor.to_pandas = lambda self: cursor_to_pandas(self)  # type: ignore
    Cursor.to_polars = lambda self: cursor_to_polars(self)  # type: ignore
    Cursor.to_arrow = lambda self: cursor_to_arrow(self)  # type: ignore
    Cursor.to_dict = lambda self: cursor_to_dict(self)  # type: ignore

    logger.debug("Added DataFrame methods to Cursor class")


# Auto-register methods on import
try:
    _add_dataframe_methods()
except Exception as e:
    logger.debug(f"Could not add DataFrame methods: {e}")
