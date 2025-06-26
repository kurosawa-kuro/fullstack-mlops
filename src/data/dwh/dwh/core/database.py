"""
DuckDB Data Warehouse Manager

This module provides a comprehensive interface for managing the DuckDB data warehouse,
including connection management, query execution, and database operations.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import duckdb
import pandas as pd

logger = logging.getLogger(__name__)


class DWHManager:
    """
    DuckDB Data Warehouse Manager

    Provides a high-level interface for managing the DuckDB data warehouse,
    including schema creation, data ingestion, and query execution.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the DWH Manager

        Args:
            db_path: Path to the DuckDB database file. If None, uses default path.
        """
        if db_path is None:
            # Default database path in the data directory
            current_dir = Path(__file__).parent
            db_path = current_dir.parent / "data" / "house_price_dwh.duckdb"

        self.db_path = Path(db_path)
        self.connection: Optional[duckdb.DuckDBPyConnection] = None
        self._ensure_db_directory()

    def _ensure_db_directory(self) -> None:
        """Ensure the database directory exists"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> duckdb.DuckDBPyConnection:
        """
        Establish connection to DuckDB database

        Returns:
            DuckDB connection object
        """
        if self.connection is None:
            try:
                self.connection = duckdb.connect(str(self.db_path))
                logger.info(f"Connected to DuckDB database: {self.db_path}")

                # Enable extensions for better performance
                self.connection.execute("INSTALL httpfs")
                self.connection.execute("LOAD httpfs")

                # Set configuration for better performance
                self.connection.execute("SET memory_limit='1GB'")
                self.connection.execute("SET threads=4")

            except Exception as e:
                logger.error(f"Failed to connect to DuckDB: {e}")
                raise

        return self.connection

    def disconnect(self) -> None:
        """Close the database connection"""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                logger.info("Disconnected from DuckDB database")
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")

    def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame

        Args:
            query: SQL query string
            params: Optional parameters for the query

        Returns:
            Query results as pandas DataFrame
        """
        conn = self.connect()
        try:
            if params:
                # DuckDBでは名前付きパラメータを使用
                result = conn.execute(query, params).fetchdf()
            else:
                result = conn.execute(query).fetchdf()
            logger.debug(f"Executed query: {query[:100]}...")
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            raise

    def execute_script(self, script: str) -> None:
        """
        Execute a SQL script (multiple statements)

        Args:
            script: SQL script containing multiple statements
        """
        conn = self.connect()
        try:
            conn.execute(script)
            logger.info("SQL script executed successfully")
        except Exception as e:
            logger.error(f"Script execution failed: {e}")
            logger.error(f"Script: {script[:200]}...")
            raise

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database

        Args:
            table_name: Name of the table to check

        Returns:
            True if table exists, False otherwise
        """
        query = """
        SELECT COUNT(*) as count 
        FROM information_schema.tables 
        WHERE table_name = $table_name
        """
        result = self.execute_query(query, {"table_name": table_name})
        return result.iloc[0]["count"] > 0

    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """
        Get detailed information about a table

        Args:
            table_name: Name of the table

        Returns:
            DataFrame with table schema information
        """
        query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = $table_name
        ORDER BY ordinal_position
        """
        return self.execute_query(query, {"table_name": table_name})

    def get_table_count(self, table_name: str) -> int:
        """
        Get the number of rows in a table

        Args:
            table_name: Name of the table

        Returns:
            Number of rows in the table
        """
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(query)
        return int(result.iloc[0]["count"])

    def list_tables(self) -> List[str]:
        """
        List all tables in the database

        Returns:
            List of table names
        """
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        result = self.execute_query(query)
        return result["table_name"].tolist()

    def drop_table(self, table_name: str) -> None:
        """
        Drop a table from the database

        Args:
            table_name: Name of the table to drop
        """
        if self.table_exists(table_name):
            query = f"DROP TABLE {table_name}"
            self.execute_query(query)
            logger.info(f"Dropped table: {table_name}")
        else:
            logger.warning(f"Table {table_name} does not exist")

    def vacuum(self) -> None:
        """Optimize the database by removing unused space"""
        conn = self.connect()
        try:
            conn.execute("VACUUM")
            logger.info("Database vacuum completed")
        except Exception as e:
            logger.error(f"Vacuum failed: {e}")
            raise

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.disconnect()
