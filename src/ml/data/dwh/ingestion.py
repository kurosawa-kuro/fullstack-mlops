"""
Data Ingestion Module

This module handles the ingestion of raw data into the data warehouse,
including data validation, transformation, and loading into the appropriate tables.
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from .database import DWHManager
from .schema import create_schema

logger = logging.getLogger(__name__)


def ingest_house_data(
    csv_file_path: str,
    dwh_manager: Optional[DWHManager] = None,
    create_schema_if_not_exists: bool = True
) -> Dict[str, Any]:
    """
    Ingest house data from CSV file into the data warehouse
    
    Args:
        csv_file_path: Path to the CSV file containing house data
        dwh_manager: Optional DWHManager instance. If None, creates a new one.
        create_schema_if_not_exists: Whether to create schema if it doesn't exist
        
    Returns:
        Dictionary with ingestion results and statistics
    """
    if dwh_manager is None:
        dwh_manager = DWHManager()
    
    try:
        logger.info(f"Starting data ingestion from: {csv_file_path}")
        
        # Create schema if requested and doesn't exist
        if create_schema_if_not_exists:
            if not dwh_manager.table_exists("raw_house_data"):
                logger.info("Schema does not exist, creating...")
                try:
                    create_schema(dwh_manager)
                    # スキーマ作成後の確認
                    tables = dwh_manager.list_tables()
                    logger.info(f"Schema created successfully. Available tables: {tables}")
                except Exception as e:
                    logger.error(f"Failed to create schema: {e}")
                    raise
        
        # Load and validate CSV data
        df = _load_and_validate_csv(csv_file_path)
        
        # Ingest raw data
        raw_stats = _ingest_raw_data(df, dwh_manager)
        
        # Transform and load into fact table
        fact_stats = _transform_and_load_fact_data(df, dwh_manager)
        
        # Generate summary statistics
        summary_stats = _generate_summary_statistics(dwh_manager)
        
        result = {
            "ingestion_status": "success",
            "raw_data_stats": raw_stats,
            "fact_data_stats": fact_stats,
            "summary_statistics": summary_stats,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("Data ingestion completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Data ingestion failed: {e}")
        result = {
            "ingestion_status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        raise


def _load_and_validate_csv(csv_file_path: str) -> pd.DataFrame:
    """
    Load and validate CSV data
    
    Args:
        csv_file_path: Path to the CSV file
        
    Returns:
        Validated DataFrame
    """
    try:
        # Load CSV file
        df = pd.read_csv(csv_file_path)
        logger.info(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        
        # Validate required columns
        required_columns = ['price', 'sqft', 'bedrooms', 'bathrooms', 'location', 'year_built', 'condition']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Validate data types
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['sqft'] = pd.to_numeric(df['sqft'], errors='coerce')
        df['bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce')
        df['bathrooms'] = pd.to_numeric(df['bathrooms'], errors='coerce')
        df['year_built'] = pd.to_numeric(df['year_built'], errors='coerce')
        
        # Remove rows with invalid data
        initial_count = len(df)
        df = df.dropna()
        final_count = len(df)
        
        if final_count < initial_count:
            logger.warning(f"Removed {initial_count - final_count} rows with invalid data")
        
        # Validate data ranges
        df = df[
            (df['price'] > 0) &
            (df['sqft'] > 0) &
            (df['bedrooms'] > 0) &
            (df['bathrooms'] > 0) &
            (df['year_built'] >= 1900) &
            (df['year_built'] <= datetime.now().year)
        ]
        
        logger.info(f"Data validation completed. Final dataset: {len(df)} rows")
        return df
        
    except Exception as e:
        logger.error(f"Failed to load and validate CSV: {e}")
        raise


def _ingest_raw_data(df: pd.DataFrame, dwh_manager: DWHManager) -> Dict[str, Any]:
    """
    Ingest raw data into the staging table
    
    Args:
        df: DataFrame with house data
        dwh_manager: DWHManager instance
        
    Returns:
        Dictionary with ingestion statistics
    """
    try:
        # Clear existing raw data
        dwh_manager.execute_query("DELETE FROM raw_house_data")
        
        # Prepare data for insertion
        df_raw = df.copy()
        df_raw['id'] = range(1, len(df_raw) + 1)
        
        # Insert data using DuckDB's efficient bulk insert
        conn = dwh_manager.connect()
        conn.execute("DELETE FROM raw_house_data")
        
        # Convert DataFrame to list of tuples for insertion
        data_tuples = []
        for _, row in df_raw.iterrows():
            data_tuples.append((
                int(row['id']),
                float(row['price']),
                int(row['sqft']),
                int(row['bedrooms']),
                float(row['bathrooms']),
                str(row['location']),
                int(row['year_built']),
                str(row['condition'])
            ))
        
        # Bulk insert
        conn.executemany("""
            INSERT INTO raw_house_data 
            (id, price, sqft, bedrooms, bathrooms, location, year_built, condition)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, data_tuples)
        
        # Get statistics
        row_count = dwh_manager.get_table_count("raw_house_data")
        
        stats = {
            "rows_inserted": row_count,
            "columns": list(df_raw.columns),
            "data_types": df_raw.dtypes.to_dict()
        }
        
        logger.info(f"Raw data ingestion completed: {row_count} rows inserted")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to ingest raw data: {e}")
        raise


def _transform_and_load_fact_data(df: pd.DataFrame, dwh_manager: DWHManager) -> Dict[str, Any]:
    """
    Transform raw data and load into fact table
    
    Args:
        df: DataFrame with house data
        dwh_manager: DWHManager instance
        
    Returns:
        Dictionary with transformation statistics
    """
    try:
        # Clear existing fact data
        dwh_manager.execute_query("DELETE FROM fact_house_transactions")
        
        # デバッグ: テーブルスキーマを確認
        table_info = dwh_manager.get_table_info("fact_house_transactions")
        logger.debug(f"fact_house_transactions schema: {table_info.to_dict('records')}")
        
        # Get dimension mappings
        location_mapping = _get_location_mapping(dwh_manager)
        condition_mapping = _get_condition_mapping(dwh_manager)
        year_mapping = _get_year_mapping(dwh_manager)
        
        # Transform data
        df_fact = df.copy()
        df_fact['house_id'] = range(1, len(df_fact) + 1)
        df_fact['location_id'] = df_fact['location'].map(location_mapping)
        df_fact['condition_id'] = df_fact['condition'].map(condition_mapping)
        df_fact['year_built_id'] = df_fact['year_built'].map(year_mapping)
        
        # デバッグ: 変換後のデータを確認
        logger.debug(f"Transformed data sample (first 3 rows):")
        logger.debug(f"Columns: {list(df_fact.columns)}")
        for i in range(min(3, len(df_fact))):
            row = df_fact.iloc[i]
            logger.debug(f"Row {i}: house_id={row['house_id']}, location_id={row['location_id']}, condition_id={row['condition_id']}, year_built_id={row['year_built_id']}")
        
        # Remove rows with missing dimension mappings
        initial_count = len(df_fact)
        df_fact = df_fact.dropna(subset=['location_id', 'condition_id', 'year_built_id'])
        final_count = len(df_fact)
        
        if final_count < initial_count:
            logger.warning(
                f"Removed {initial_count - final_count} rows with missing dimension mappings"
            )
        
        logger.info(f"Final transformed data: {len(df_fact)} rows")
        
        # Insert into fact table
        conn = dwh_manager.connect()
        
        data_tuples = []
        for i, row in df_fact.iterrows():
            transaction_id = i + 1  # transaction_id (1から開始)
            house_id = int(row['house_id'])
            location_id = int(row['location_id'])
            condition_id = int(row['condition_id'])
            year_built_id = int(row['year_built_id'])
            price = float(row['price'])
            sqft = int(row['sqft'])
            bedrooms = int(row['bedrooms'])
            bathrooms = float(row['bathrooms'])
            
            # デバッグ情報を追加
            if i < 3:  # 最初の3行のみログ出力
                logger.debug(f"Row {i}: transaction_id={transaction_id}, house_id={house_id}, location_id={location_id}, condition_id={condition_id}, year_built_id={year_built_id}")
            
            data_tuples.append((
                transaction_id,
                house_id,
                location_id,
                condition_id,
                year_built_id,
                price,
                sqft,
                bedrooms,
                bathrooms
            ))
        
        logger.info(f"Prepared {len(data_tuples)} rows for fact_house_transactions insertion")
        
        conn.executemany("""
            INSERT INTO fact_house_transactions 
            (transaction_id, house_id, location_id, condition_id, year_built_id, price, sqft, bedrooms, bathrooms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data_tuples)
        
        # Get statistics
        row_count = dwh_manager.get_table_count("fact_house_transactions")
        
        stats = {
            "rows_inserted": row_count,
            "rows_processed": len(df),
            "rows_with_missing_dimensions": initial_count - final_count
        }
        
        logger.info(f"Fact data transformation completed: {row_count} rows inserted")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to transform and load fact data: {e}")
        raise


def _get_location_mapping(dwh_manager: DWHManager) -> Dict[str, int]:
    """Get location name to ID mapping"""
    query = "SELECT location_name, location_id FROM dim_locations WHERE is_active = TRUE"
    result = dwh_manager.execute_query(query)
    return dict(zip(result['location_name'], result['location_id']))


def _get_condition_mapping(dwh_manager: DWHManager) -> Dict[str, int]:
    """Get condition name to ID mapping"""
    query = "SELECT condition_name, condition_id FROM dim_conditions WHERE is_active = TRUE"
    result = dwh_manager.execute_query(query)
    return dict(zip(result['condition_name'], result['condition_id']))


def _get_year_mapping(dwh_manager: DWHManager) -> Dict[int, int]:
    """Get year value to ID mapping"""
    query = "SELECT year_value, year_id FROM dim_years WHERE is_active = TRUE"
    result = dwh_manager.execute_query(query)
    return dict(zip(result['year_value'], result['year_id']))


def _generate_summary_statistics(dwh_manager: DWHManager) -> Dict[str, Any]:
    """
    Generate summary statistics from the data warehouse
    
    Args:
        dwh_manager: DWHManager instance
        
    Returns:
        Dictionary with summary statistics
    """
    try:
        # Get summary statistics from view
        summary_query = "SELECT * FROM v_summary_statistics"
        summary_df = dwh_manager.execute_query(summary_query)
        
        # Get location analytics
        location_query = "SELECT * FROM v_location_analytics"
        location_df = dwh_manager.execute_query(location_query)
        
        # Get condition analytics
        condition_query = "SELECT * FROM v_condition_analytics"
        condition_df = dwh_manager.execute_query(condition_query)
        
        stats = {
            "summary": summary_df.to_dict('records')[0] if len(summary_df) > 0 else {},
            "location_analytics": location_df.to_dict('records'),
            "condition_analytics": condition_df.to_dict('records')
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to generate summary statistics: {e}")
        return {}


def validate_ingestion(dwh_manager: Optional[DWHManager] = None) -> Dict[str, Any]:
    """
    Validate the data ingestion by checking data integrity and consistency
    
    Args:
        dwh_manager: Optional DWHManager instance. If None, creates a new one.
        
    Returns:
        Dictionary with validation results
    """
    if dwh_manager is None:
        dwh_manager = DWHManager()
    
    try:
        validation_results = {
            "status": "passed",
            "checks": {},
            "errors": []
        }
        
        # Check if tables exist
        required_tables = ["raw_house_data", "fact_house_transactions", "dim_locations", "dim_conditions", "dim_years"]
        for table in required_tables:
            exists = dwh_manager.table_exists(table)
            validation_results["checks"][f"table_exists_{table}"] = exists
            if not exists:
                validation_results["errors"].append(f"Required table {table} does not exist")
        
        # Check data consistency
        if dwh_manager.table_exists("raw_house_data") and dwh_manager.table_exists("fact_house_transactions"):
            raw_count = dwh_manager.get_table_count("raw_house_data")
            fact_count = dwh_manager.get_table_count("fact_house_transactions")
            
            validation_results["checks"]["data_consistency"] = raw_count == fact_count
            if raw_count != fact_count:
                validation_results["errors"].append(f"Data inconsistency: raw_count={raw_count}, fact_count={fact_count}")
        
        # Check for orphaned records
        orphaned_query = """
        SELECT COUNT(*) as orphaned_count
        FROM fact_house_transactions f
        LEFT JOIN dim_locations l ON f.location_id = l.location_id
        LEFT JOIN dim_conditions c ON f.condition_id = c.condition_id
        LEFT JOIN dim_years y ON f.year_built_id = y.year_id
        WHERE l.location_id IS NULL OR c.condition_id IS NULL OR y.year_id IS NULL
        """
        
        orphaned_result = dwh_manager.execute_query(orphaned_query)
        orphaned_count = orphaned_result.iloc[0]['orphaned_count']
        
        validation_results["checks"]["no_orphaned_records"] = orphaned_count == 0
        if orphaned_count > 0:
            validation_results["errors"].append(f"Found {orphaned_count} orphaned records")
        
        # Update overall status
        if validation_results["errors"]:
            validation_results["status"] = "failed"
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "checks": {},
            "errors": [str(e)]
        } 