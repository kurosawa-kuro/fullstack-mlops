"""
Data Warehouse (DWH) package for house price prediction project.

This package provides functionality for:
- DuckDB database management
- Data ingestion and transformation
- Schema management
- Query optimization
"""

__version__ = "1.0.0"
__author__ = "MLOps Team"

from .database import DWHManager
from .schema import create_schema, drop_schema, get_schema_info
from .ingestion import ingest_house_data, validate_ingestion

__all__ = [
    "DWHManager",
    "create_schema", 
    "drop_schema",
    "ingest_house_data",
    "validate_ingestion",
    "get_schema_info"
] 