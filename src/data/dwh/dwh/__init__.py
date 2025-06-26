"""
Data Warehouse (DWH) package for house price prediction project.

This package provides functionality for:
- DuckDB database management
- Bronze layer data ingestion
- Bronze layer validation

Package Structure:
├── core/           # Core DWH functionality
├── scripts/        # Utility scripts
├── data/           # Database files
└── config/         # Configuration files
"""

__version__ = "1.0.0"
__author__ = "MLOps Team"

# Import core functionality
from .core import DWHManager, ingest_bronze_data, validate_bronze_ingestion

__all__ = [
    "DWHManager",
    "ingest_bronze_data",
    "validate_bronze_ingestion",
]
