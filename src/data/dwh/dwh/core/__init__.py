"""
DWH Core Modules

This package contains the core data warehouse functionality:
- Database management
- Bronze layer data ingestion
"""

from .database import DWHManager
from .ingestion import ingest_bronze_data, validate_bronze_ingestion

__all__ = [
    "DWHManager",
    "ingest_bronze_data",
    "validate_bronze_ingestion",
]
