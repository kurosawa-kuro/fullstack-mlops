"""
DWH Core Modules

This package contains the core data warehouse functionality:
- Database management
- Schema operations
- Data ingestion and transformation
"""

from .database import DWHManager
from .schema import create_schema, drop_schema, get_schema_info
from .ingestion import ingest_house_data, validate_ingestion

__all__ = [
    "DWHManager",
    "create_schema",
    "drop_schema",
    "get_schema_info",
    "ingest_house_data",
    "validate_ingestion",
] 