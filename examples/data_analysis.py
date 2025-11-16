"""
Data analysis examples using sqlalchemy-jdbcapi with pandas and polars.

Demonstrates integration with data science tools.
"""

from sqlalchemy import create_engine, text

# ==============================================================================
# Example 1: Pandas Integration
# ==============================================================================

def example_pandas_integration():
    """Example using pandas with JDBC connection."""
    print("=" * 70)
    print("Example 1: Pandas Integration")
    print("=" * 70)

    try:
        import pandas as pd
    except ImportError:
        print("⚠ Pandas not installed. Install with: pip install pandas")
        return

    # Create engine
    engine = create_engine(
        "jdbcapi+postgresql://user:password@localhost:5432/mydb"
    )

    # Read SQL query into DataFrame
    df = pd.read_sql_query(
        "SELECT * FROM users WHERE created_at > '2024-01-01'",
        engine,
    )

    print(f"\n✓ Loaded {len(df)} rows into DataFrame")
    print(f"\nDataFrame info:")
    print(df.info())

    # Write DataFrame to database
    df.to_sql(
        "users_backup",
        engine,
        if_exists="replace",
        index=False,
    )

    print("\n✓ Pandas integration successful!\n")


# ==============================================================================
# Example 2: Polars Integration
# ==============================================================================

def example_polars_integration():
    """Example using polars with JDBC connection."""
    print("=" * 70)
    print("Example 2: Polars Integration")
    print("=" * 70)

    try:
        import polars as pl
    except ImportError:
        print("⚠ Polars not installed. Install with: pip install polars")
        return

    # Create engine
    engine = create_engine(
        "jdbcapi+postgresql://user:password@localhost:5432/mydb"
    )

    # Read SQL query into Polars DataFrame
    query = "SELECT * FROM users"

    with engine.connect() as conn:
        df = pl.read_database(query, conn)

    print(f"\n✓ Loaded {len(df)} rows into Polars DataFrame")
    print(f"\nDataFrame schema:")
    print(df.schema)

    # Polars operations
    filtered_df = df.filter(pl.col("created_at") > "2024-01-01")
    aggregated = filtered_df.group_by("status").agg(pl.count())

    print(f"\n✓ Polars operations complete!")
    print(f"  - Filtered: {len(filtered_df)} rows")
    print(f"  - Aggregated: {len(aggregated)} groups")

    print("\n✓ Polars integration successful!\n")


# ==============================================================================
# Example 3: Data Pipeline with Multiple Databases
# ==============================================================================

def example_data_pipeline():
    """Example data pipeline across multiple databases."""
    print("=" * 70)
    print("Example 3: Data Pipeline")
    print("=" * 70)

    try:
        import pandas as pd
    except ImportError:
        print("⚠ Pandas not installed")
        return

    # Source: PostgreSQL
    source_engine = create_engine(
        "jdbcapi+postgresql://user:pass@localhost:5432/source_db"
    )

    # Target: MySQL
    target_engine = create_engine(
        "jdbcapi+mysql://user:pass@localhost:3306/target_db"
    )

    # Extract from PostgreSQL
    df = pd.read_sql_query(
        """
        SELECT
            user_id,
            username,
            email,
            created_at
        FROM users
        WHERE active = true
        """,
        source_engine,
    )

    print(f"\n✓ Extracted {len(df)} records from PostgreSQL")

    # Transform
    df["email_domain"] = df["email"].str.split("@").str[1]
    df["username_lower"] = df["username"].str.lower()

    print(f"✓ Transformed {len(df)} records")

    # Load into MySQL
    df.to_sql(
        "users_etl",
        target_engine,
        if_exists="replace",
        index=False,
        chunksize=1000,  # Batch inserts
    )

    print(f"✓ Loaded {len(df)} records into MySQL")

    print("\n✓ Data pipeline successful!\n")


# ==============================================================================
# Example 4: Complex Analytics with Window Functions
# ==============================================================================

def example_analytics_queries():
    """Example complex analytics queries."""
    print("=" * 70)
    print("Example 4: Complex Analytics")
    print("=" * 70)

    try:
        import pandas as pd
    except ImportError:
        print("⚠ Pandas not installed")
        return

    engine = create_engine(
        "jdbcapi+postgresql://user:password@localhost:5432/mydb"
    )

    # Complex analytical query with window functions
    query = """
    SELECT
        user_id,
        username,
        order_date,
        order_amount,
        -- Running total
        SUM(order_amount) OVER (
            PARTITION BY user_id
            ORDER BY order_date
        ) AS running_total,
        -- Rank within user
        ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY order_amount DESC
        ) AS order_rank,
        -- Moving average
        AVG(order_amount) OVER (
            PARTITION BY user_id
            ORDER BY order_date
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS moving_avg_3
    FROM orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
    ORDER BY user_id, order_date
    """

    df = pd.read_sql_query(query, engine)

    print(f"\n✓ Analytics query returned {len(df)} rows")
    print(f"\nSample data:")
    print(df.head())

    print("\n✓ Complex analytics successful!\n")


# ==============================================================================
# Example 5: Batch Processing with Chunking
# ==============================================================================

def example_batch_processing():
    """Example processing large datasets in chunks."""
    print("=" * 70)
    print("Example 5: Batch Processing")
    print("=" * 70)

    try:
        import pandas as pd
    except ImportError:
        print("⚠ Pandas not installed")
        return

    engine = create_engine(
        "jdbcapi+postgresql://user:password@localhost:5432/mydb"
    )

    # Process data in chunks to avoid memory issues
    chunk_size = 10000
    total_processed = 0

    query = "SELECT * FROM large_table"

    for chunk in pd.read_sql_query(query, engine, chunksize=chunk_size):
        # Process each chunk
        processed_chunk = chunk.copy()
        processed_chunk["processed"] = True

        # Write processed chunk
        processed_chunk.to_sql(
            "processed_data",
            engine,
            if_exists="append",
            index=False,
        )

        total_processed += len(chunk)
        print(f"✓ Processed {total_processed:,} rows...")

    print(f"\n✓ Batch processing complete! Total: {total_processed:,} rows\n")


# ==============================================================================
# Example 6: Real-time Data Streaming
# ==============================================================================

def example_streaming_data():
    """Example streaming data from database."""
    print("=" * 70)
    print("Example 6: Streaming Data")
    print("=" * 70)

    engine = create_engine(
        "jdbcapi+postgresql://user:password@localhost:5432/mydb"
    )

    # Use server-side cursors for streaming large result sets
    with engine.connect().execution_options(stream_results=True) as conn:
        result = conn.execute(
            text("SELECT * FROM very_large_table")
        )

        # Process results one at a time
        for i, row in enumerate(result, 1):
            # Process row
            if i % 10000 == 0:
                print(f"✓ Streamed {i:,} rows...")

            # Early exit for demo
            if i >= 100000:
                break

    print("\n✓ Streaming data successful!\n")


# ==============================================================================
# Example 7: Data Validation and Quality Checks
# ==============================================================================

def example_data_validation():
    """Example data quality validation."""
    print("=" * 70)
    print("Example 7: Data Validation")
    print("=" * 70)

    try:
        import pandas as pd
    except ImportError:
        print("⚠ Pandas not installed")
        return

    engine = create_engine(
        "jdbcapi+postgresql://user:password@localhost:5432/mydb"
    )

    df = pd.read_sql_query("SELECT * FROM users", engine)

    print("\n✓ Data Quality Report:")
    print("=" * 50)

    # Check for nulls
    null_counts = df.isnull().sum()
    print(f"\n1. Null Values:")
    print(null_counts[null_counts > 0])

    # Check for duplicates
    duplicates = df.duplicated().sum()
    print(f"\n2. Duplicate Rows: {duplicates}")

    # Check data types
    print(f"\n3. Data Types:")
    print(df.dtypes)

    # Check value ranges
    if "created_at" in df.columns:
        print(f"\n4. Date Range:")
        print(f"   Min: {df['created_at'].min()}")
        print(f"   Max: {df['created_at'].max()}")

    # Check for outliers (example: email format)
    if "email" in df.columns:
        invalid_emails = df[~df["email"].str.contains("@", na=False)]
        print(f"\n5. Invalid Emails: {len(invalid_emails)}")

    print("\n✓ Data validation complete!\n")


# ==============================================================================
# Example 8: Export to Multiple Formats
# ==============================================================================

def example_export_formats():
    """Example exporting data to various formats."""
    print("=" * 70)
    print("Example 8: Export to Multiple Formats")
    print("=" * 70)

    try:
        import pandas as pd
    except ImportError:
        print("⚠ Pandas not installed")
        return

    engine = create_engine(
        "jdbcapi+postgresql://user:password@localhost:5432/mydb"
    )

    df = pd.read_sql_query("SELECT * FROM users LIMIT 1000", engine)

    # Export to CSV
    df.to_csv("users_export.csv", index=False)
    print("✓ Exported to CSV")

    # Export to Excel
    df.to_excel("users_export.xlsx", index=False, sheet_name="Users")
    print("✓ Exported to Excel")

    # Export to JSON
    df.to_json("users_export.json", orient="records", indent=2)
    print("✓ Exported to JSON")

    # Export to Parquet
    df.to_parquet("users_export.parquet", index=False)
    print("✓ Exported to Parquet")

    print("\n✓ All exports complete!\n")


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SQLAlchemy JDBCAPI - Data Analysis Examples")
    print("=" * 70 + "\n")

    examples = [
        ("Pandas Integration", example_pandas_integration),
        ("Polars Integration", example_polars_integration),
        ("Data Pipeline", example_data_pipeline),
        ("Complex Analytics", example_analytics_queries),
        ("Batch Processing", example_batch_processing),
        ("Streaming Data", example_streaming_data),
        ("Data Validation", example_data_validation),
        ("Export Formats", example_export_formats),
    ]

    for name, example_func in examples:
        try:
            # example_func()  # Uncomment to run with real database
            print(f"Example: {name} (Requires real database - skipped)")
            print()
        except Exception as e:
            print(f"\n⚠ Example {name} failed: {e}\n")

    print("=" * 70)
    print("All data analysis examples shown!")
    print("=" * 70 + "\n")
