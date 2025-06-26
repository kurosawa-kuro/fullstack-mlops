"""
Bronze Layer Data Ingestion Module

This module handles the ingestion of raw data into the Bronze layer only.
No data transformation, cleaning, or feature engineering is performed here.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from .database import DWHManager

logger = logging.getLogger(__name__)


def ingest_bronze_data(
    csv_file_path: str,
    dwh_manager: Optional[DWHManager] = None,
) -> Dict[str, Any]:
    """
    Ingest raw data from CSV file into Bronze layer only

    Args:
        csv_file_path: Path to the CSV file containing house data
        dwh_manager: Optional DWHManager instance. If None, creates a new one.

    Returns:
        Dictionary with ingestion results and statistics
    """
    if dwh_manager is None:
        dwh_manager = DWHManager()

    try:
        logger.info(f"Starting Bronze layer data ingestion from: {csv_file_path}")

        # Load CSV data without any transformation
        df = pd.read_csv(csv_file_path)
        logger.info(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")

        # Create Bronze table if it doesn't exist
        _create_bronze_table(dwh_manager)

        # Ingest raw data into Bronze layer
        bronze_stats = _ingest_bronze_data(df, dwh_manager)

        result = {
            "ingestion_status": "success",
            "bronze_data_stats": bronze_stats,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info("Bronze layer data ingestion completed successfully")
        return result

    except Exception as e:
        logger.error(f"Bronze layer data ingestion failed: {e}")
        result = {
            "ingestion_status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
        raise


def _create_bronze_table(dwh_manager: DWHManager) -> None:
    """Create Bronze layer table if it doesn't exist"""

    bronze_table_sql = """
    CREATE TABLE IF NOT EXISTS bronze_raw_house_data (
        id INTEGER PRIMARY KEY,
        price DECIMAL(12,2),
        sqft INTEGER,
        bedrooms INTEGER,
        bathrooms DECIMAL(3,1),
        location VARCHAR(50),
        year_built INTEGER,
        condition VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    dwh_manager.execute_script(bronze_table_sql)
    logger.info("Bronze table created/verified")


def _ingest_bronze_data(df: pd.DataFrame, dwh_manager: DWHManager) -> Dict[str, Any]:
    """
    Ingest raw data into Bronze layer table

    Args:
        df: DataFrame with raw house data
        dwh_manager: DWHManager instance

    Returns:
        Dictionary with ingestion statistics
    """
    try:
        # Clear existing Bronze data
        dwh_manager.execute_query("DELETE FROM bronze_raw_house_data")

        # Prepare data for insertion (no transformation)
        df_bronze = df.copy()
        df_bronze["id"] = range(1, len(df_bronze) + 1)

        # Insert data using DuckDB's efficient bulk insert
        conn = dwh_manager.connect()

        # Convert DataFrame to list of tuples for insertion
        data_tuples = []
        for _, row in df_bronze.iterrows():
            data_tuples.append(
                (
                    int(row["id"]),
                    float(row["price"]) if pd.notna(row["price"]) else None,
                    int(row["sqft"]) if pd.notna(row["sqft"]) else None,
                    int(row["bedrooms"]) if pd.notna(row["bedrooms"]) else None,
                    float(row["bathrooms"]) if pd.notna(row["bathrooms"]) else None,
                    str(row["location"]) if pd.notna(row["location"]) else None,
                    int(row["year_built"]) if pd.notna(row["year_built"]) else None,
                    str(row["condition"]) if pd.notna(row["condition"]) else None,
                )
            )

        # Bulk insert
        conn.executemany(
            """
            INSERT INTO bronze_raw_house_data 
            (id, price, sqft, bedrooms, bathrooms, location, year_built, condition)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            data_tuples,
        )

        # Get statistics
        row_count = dwh_manager.get_table_count("bronze_raw_house_data")

        stats = {
            "rows_inserted": row_count,
            "columns": list(df_bronze.columns),
            "data_types": df_bronze.dtypes.to_dict(),
        }

        logger.info(f"Bronze data ingestion completed: {row_count} rows inserted")
        return stats

    except Exception as e:
        logger.error(f"Failed to ingest Bronze data: {e}")
        raise


def validate_bronze_ingestion(
    dwh_manager: Optional[DWHManager] = None,
) -> Dict[str, Any]:
    """
    Validate the Bronze layer data ingestion

    Args:
        dwh_manager: Optional DWHManager instance. If None, creates a new one.

    Returns:
        Dictionary with validation results
    """
    if dwh_manager is None:
        dwh_manager = DWHManager()

    try:
        validation_results = {"status": "passed", "checks": {}, "errors": []}

        # Check if Bronze table exists
        exists = dwh_manager.table_exists("bronze_raw_house_data")
        validation_results["checks"]["bronze_table_exists"] = exists
        if not exists:
            validation_results["errors"].append("Bronze table does not exist")

        # Check if Bronze table has data
        if exists:
            row_count = dwh_manager.get_table_count("bronze_raw_house_data")
            validation_results["checks"]["bronze_has_data"] = row_count > 0
            if row_count == 0:
                validation_results["errors"].append("Bronze table is empty")

        # Update overall status
        if validation_results["errors"]:
            validation_results["status"] = "failed"

        return validation_results

    except Exception as e:
        logger.error(f"Bronze validation failed: {e}")
        return {"status": "error", "error": str(e), "checks": {}, "errors": [str(e)]}
