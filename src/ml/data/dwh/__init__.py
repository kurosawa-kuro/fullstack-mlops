"""
Data Warehouse (DWH) package for house price prediction project.

This package provides functionality for:
- DuckDB database management
- Data ingestion and transformation
- Schema management
- Query optimization

Package Structure:
├── core/           # Core DWH functionality
├── scripts/        # Utility scripts
├── data/           # Database files
└── config/         # Configuration files
"""

__version__ = "1.0.0"
__author__ = "MLOps Team"

# Import core functionality
from .core import (
    DWHManager,
    create_schema,
    drop_schema,
    get_schema_info,
    ingest_house_data,
    validate_ingestion,
)

__all__ = [
    "DWHManager",
    "create_schema",
    "drop_schema",
    "ingest_house_data",
    "validate_ingestion",
    "get_schema_info",
]
