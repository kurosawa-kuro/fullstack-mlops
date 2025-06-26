"""
DWH Schema Management

This module defines the data warehouse schema for the house price prediction project,
including table creation scripts and schema management functions.
"""

import logging
from typing import Optional

from .database import DWHManager

logger = logging.getLogger(__name__)


# Schema definition for house price data warehouse
HOUSE_PRICE_SCHEMA = """
-- =====================================================
-- House Price Data Warehouse Schema
-- =====================================================

-- Raw data table (staging area)
CREATE TABLE IF NOT EXISTS raw_house_data (
    id INTEGER PRIMARY KEY,
    price DECIMAL(12,2) NOT NULL,
    sqft INTEGER NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms DECIMAL(3,1) NOT NULL,
    location VARCHAR(50) NOT NULL,
    year_built INTEGER NOT NULL,
    condition VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension table for locations
CREATE TABLE IF NOT EXISTS dim_locations (
    location_id INTEGER PRIMARY KEY,
    location_name VARCHAR(50) UNIQUE NOT NULL,
    location_type VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension table for property conditions
CREATE TABLE IF NOT EXISTS dim_conditions (
    condition_id INTEGER PRIMARY KEY,
    condition_name VARCHAR(20) UNIQUE NOT NULL,
    condition_score INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension table for years
CREATE TABLE IF NOT EXISTS dim_years (
    year_id INTEGER PRIMARY KEY,
    year_value INTEGER UNIQUE NOT NULL,
    decade VARCHAR(10) NOT NULL,
    century VARCHAR(10) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fact table for house transactions
CREATE TABLE IF NOT EXISTS fact_house_transactions (
    transaction_id INTEGER PRIMARY KEY,
    house_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    condition_id INTEGER NOT NULL,
    year_built_id INTEGER NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    sqft INTEGER NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms DECIMAL(3,1) NOT NULL,
    transaction_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    FOREIGN KEY (location_id) REFERENCES dim_locations(location_id),
    FOREIGN KEY (condition_id) REFERENCES dim_conditions(condition_id),
    FOREIGN KEY (year_built_id) REFERENCES dim_years(year_id)
);

-- Aggregated view for analytics with calculated columns
CREATE OR REPLACE VIEW v_house_analytics AS
SELECT 
    h.transaction_id,
    h.price,
    h.sqft,
    h.bedrooms,
    h.bathrooms,
    (h.price / h.sqft) as price_per_sqft,
    (YEAR(CURRENT_DATE) - y.year_value) as house_age,
    (h.bedrooms / h.bathrooms) as bed_bath_ratio,
    l.location_name,
    l.location_type,
    c.condition_name,
    c.condition_score,
    y.year_value,
    y.decade,
    y.century,
    h.transaction_date
FROM fact_house_transactions h
JOIN dim_locations l ON h.location_id = l.location_id
JOIN dim_conditions c ON h.condition_id = c.condition_id
JOIN dim_years y ON h.year_built_id = y.year_id
WHERE l.is_active = TRUE 
  AND c.is_active = TRUE 
  AND y.is_active = TRUE;

-- Summary statistics view
CREATE OR REPLACE VIEW v_summary_statistics AS
SELECT 
    COUNT(*) as total_houses,
    AVG(price) as avg_price,
    MIN(price) as min_price,
    MAX(price) as max_price,
    STDDEV(price) as price_stddev,
    AVG(sqft) as avg_sqft,
    AVG(price_per_sqft) as avg_price_per_sqft,
    AVG(house_age) as avg_house_age
FROM v_house_analytics;

-- Location-based analytics view
CREATE OR REPLACE VIEW v_location_analytics AS
SELECT 
    location_name,
    location_type,
    COUNT(*) as house_count,
    AVG(price) as avg_price,
    AVG(sqft) as avg_sqft,
    AVG(price_per_sqft) as avg_price_per_sqft,
    MIN(price) as min_price,
    MAX(price) as max_price
FROM v_house_analytics
GROUP BY location_name, location_type
ORDER BY avg_price DESC;

-- Condition-based analytics view
CREATE OR REPLACE VIEW v_condition_analytics AS
SELECT 
    condition_name,
    condition_score,
    COUNT(*) as house_count,
    AVG(price) as avg_price,
    AVG(sqft) as avg_sqft,
    AVG(price_per_sqft) as avg_price_per_sqft
FROM v_house_analytics
GROUP BY condition_name, condition_score
ORDER BY condition_score DESC;
"""


def create_schema(dwh_manager: Optional[DWHManager] = None) -> None:
    """
    Create the complete data warehouse schema

    Args:
        dwh_manager: Optional DWHManager instance. If None, creates a new one.
    """
    if dwh_manager is None:
        dwh_manager = DWHManager()

    try:
        logger.info("Creating data warehouse schema...")
        dwh_manager.execute_script(HOUSE_PRICE_SCHEMA)
        logger.info("Data warehouse schema created successfully")

        # Insert dimension data
        _insert_dimension_data(dwh_manager)

    except Exception as e:
        logger.error(f"Failed to create schema: {e}")
        raise


def drop_schema(dwh_manager: Optional[DWHManager] = None) -> None:
    """
    Drop all tables in the data warehouse

    Args:
        dwh_manager: Optional DWHManager instance. If None, creates a new one.
    """
    if dwh_manager is None:
        dwh_manager = DWHManager()

    try:
        logger.info("Dropping data warehouse schema...")

        # Drop views first
        views = [
            "v_house_analytics",
            "v_summary_statistics",
            "v_location_analytics",
            "v_condition_analytics",
        ]

        for view in views:
            try:
                dwh_manager.execute_query(f"DROP VIEW IF EXISTS {view}")
            except Exception as e:
                logger.warning(f"Could not drop view {view}: {e}")

        # Drop tables
        tables = [
            "fact_house_transactions",
            "raw_house_data",
            "dim_locations",
            "dim_conditions",
            "dim_years",
        ]

        for table in tables:
            dwh_manager.drop_table(table)

        logger.info("Data warehouse schema dropped successfully")

    except Exception as e:
        logger.error(f"Failed to drop schema: {e}")
        raise


def _insert_dimension_data(dwh_manager: DWHManager) -> None:
    """
    Insert initial dimension data

    Args:
        dwh_manager: DWHManager instance
    """
    try:
        logger.info("Inserting dimension data...")

        # Insert locations
        locations_data = """
        INSERT INTO dim_locations (location_id, location_name, location_type) VALUES
        (1, 'Suburb', 'Residential'),
        (2, 'Downtown', 'Urban'),
        (3, 'Rural', 'Rural'),
        (4, 'Waterfront', 'Premium'),
        (5, 'Urban', 'Urban'),
        (6, 'Mountain', 'Premium')
        ON CONFLICT (location_id) DO UPDATE SET
        location_name = EXCLUDED.location_name,
        location_type = EXCLUDED.location_type;
        """
        dwh_manager.execute_script(locations_data)

        # Insert conditions
        conditions_data = """
        INSERT INTO dim_conditions (condition_id, condition_name, condition_score) VALUES
        (1, 'Poor', 1),
        (2, 'Fair', 2),
        (3, 'Good', 3),
        (4, 'Excellent', 4)
        ON CONFLICT (condition_id) DO UPDATE SET
        condition_name = EXCLUDED.condition_name,
        condition_score = EXCLUDED.condition_score;
        """
        dwh_manager.execute_script(conditions_data)

        # Insert years (1940-2020)
        years_data = """
        INSERT INTO dim_years (year_id, year_value, decade, century) VALUES
        """

        for i, year in enumerate(range(1940, 2021)):
            decade = f"{year//10*10}s"
            century = "20th" if year < 2000 else "21st"
            years_data += f"({i+1}, {year}, '{decade}', '{century}'),"

        years_data = (
            years_data.rstrip(",")
            + """
        ON CONFLICT (year_id) DO UPDATE SET
        year_value = EXCLUDED.year_value,
        decade = EXCLUDED.decade,
        century = EXCLUDED.century;
        """
        )
        dwh_manager.execute_script(years_data)

        logger.info("Dimension data inserted successfully")

    except Exception as e:
        logger.error(f"Failed to insert dimension data: {e}")
        raise


def get_schema_info(dwh_manager: Optional[DWHManager] = None) -> dict:
    """
    Get information about the current schema

    Args:
        dwh_manager: Optional DWHManager instance. If None, creates a new one.

    Returns:
        Dictionary with schema information
    """
    if dwh_manager is None:
        dwh_manager = DWHManager()

    try:
        tables = dwh_manager.list_tables()
        schema_info = {"tables": {}, "views": [], "total_tables": 0, "total_views": 0}

        for table in tables:
            if table.startswith("v_"):
                schema_info["views"].append(table)
                schema_info["total_views"] += 1
            else:
                table_info = dwh_manager.get_table_info(table)
                row_count = dwh_manager.get_table_count(table)
                schema_info["tables"][table] = {
                    "columns": table_info.to_dict("records"),
                    "row_count": row_count,
                }
                schema_info["total_tables"] += 1

        return schema_info

    except Exception as e:
        logger.error(f"Failed to get schema info: {e}")
        raise
