"""
DWH Configuration Settings

This module contains configuration settings for the data warehouse.
"""

import os
from pathlib import Path
from typing import Any, Dict

# Base paths
DWH_BASE_PATH = Path(__file__).parent.parent
DATA_PATH = DWH_BASE_PATH / "data"
CONFIG_PATH = DWH_BASE_PATH / "config"

# Database settings
DEFAULT_DB_NAME = "house_price_dwh.duckdb"
DEFAULT_DB_PATH = DATA_PATH / DEFAULT_DB_NAME

# Database configuration
DB_CONFIG = {
    "memory_limit": "1GB",
    "threads": 4,
    "enable_httpfs": True,
}

# Schema settings
SCHEMA_SETTINGS = {
    "auto_create_schema": True,
    "validate_on_ingestion": True,
    "backup_before_drop": True,
}

# Ingestion settings
INGESTION_SETTINGS = {
    "batch_size": 1000,
    "validate_data": True,
    "remove_invalid_rows": True,
    "log_ingestion_stats": True,
}

# Validation settings
VALIDATION_SETTINGS = {
    "check_data_consistency": True,
    "check_orphaned_records": True,
    "check_referential_integrity": True,
}

# Logging settings
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "dwh.log",
}


def get_db_path(db_name: str = None) -> Path:
    """Get database file path"""
    if db_name is None:
        db_name = DEFAULT_DB_NAME
    return DATA_PATH / db_name


def get_config() -> Dict[str, Any]:
    """Get complete configuration"""
    return {
        "database": {
            "default_path": str(DEFAULT_DB_PATH),
            "config": DB_CONFIG,
        },
        "schema": SCHEMA_SETTINGS,
        "ingestion": INGESTION_SETTINGS,
        "validation": VALIDATION_SETTINGS,
        "logging": LOGGING_CONFIG,
    }
