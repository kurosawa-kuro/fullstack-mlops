#!/usr/bin/env python3
"""
DWH Setup and Data Ingestion Script

This script sets up the DuckDB data warehouse and ingests house data from CSV.
It can be run independently or as part of the MLOps pipeline.
"""

import argparse
import logging
import sys
from pathlib import Path

# デバッグ情報を追加
print(f"Current working directory: {Path.cwd()}")
print(f"Script location: {Path(__file__).resolve()}")
print(f"Script parents: {list(Path(__file__).resolve().parents)}")

# srcディレクトリの絶対パスをsys.pathに追加
# setup_dwh.py -> scripts -> dwh -> data -> ml -> src -> fullstack-mlops
# つまり、parents[5]でfullstack-mlopsディレクトリを取得
src_path = Path(__file__).resolve().parents[5] / "src"
print(f"Adding to sys.path: {src_path}")
print(f"src_path exists: {src_path.exists()}")

sys.path.insert(0, str(src_path))
print(f"sys.path after insertion: {sys.path[:3]}")

# モジュールが存在するかチェック
try:
    import ml

    print(f"ml module found at: {ml.__file__}")
except ImportError as e:
    print(f"ml module import error: {e}")

try:
    from ml.data.dwh.core import (
        DWHManager,
        create_schema,
        drop_schema,
        get_schema_info,
        ingest_house_data,
        validate_ingestion,
    )

    print("Successfully imported ml.data.dwh.core modules")
except ImportError as e:
    print(f"ml.data.dwh.core import error: {e}")
    # 代替手段として相対インポートを試す
    try:
        from ..core.database import DWHManager
        from ..core.ingestion import ingest_house_data, validate_ingestion
        from ..core.schema import create_schema, drop_schema, get_schema_info

        print("Successfully imported using relative imports")
    except ImportError as e2:
        print(f"Relative import also failed: {e2}")
        sys.exit(1)


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("dwh_setup.log"),
        ],
    )


def main():
    """Main function to setup DWH and ingest data"""
    parser = argparse.ArgumentParser(
        description="Setup DuckDB DWH and ingest house data"
    )
    parser.add_argument(
        "--csv-file",
        type=str,
        default="src/ml/data/raw/house_data.csv",
        help="Path to the CSV file containing house data",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=None,
        help="Path to the DuckDB database file (optional)",
    )
    parser.add_argument(
        "--drop-schema",
        action="store_true",
        help="Drop existing schema before creating new one",
    )
    parser.add_argument(
        "--force-schema",
        action="store_true",
        help="Force schema recreation even if tables exist",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate existing data without ingestion",
    )
    parser.add_argument(
        "--info-only",
        action="store_true",
        help="Only show schema information without making changes",
    )
    parser.add_argument(
        "--check-schema", action="store_true", help="Check current schema status"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="DEBUG",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        # Initialize DWH manager
        dwh_manager = DWHManager(args.db_path)
        logger.info(f"Initialized DWH manager with database: {dwh_manager.db_path}")

        # Show schema information only
        if args.info_only:
            logger.info("Showing schema information...")
            schema_info = get_schema_info(dwh_manager)

            print("\n" + "=" * 60)
            print("DWH SCHEMA INFORMATION")
            print("=" * 60)
            print(f"Total Tables: {schema_info['total_tables']}")
            print(f"Total Views: {schema_info['total_views']}")

            if schema_info["tables"]:
                print("\nTables:")
                for table_name, table_info in schema_info["tables"].items():
                    print(f"  - {table_name}: {table_info['row_count']} rows")
                    for col in table_info["columns"]:
                        print(f"    * {col['column_name']}: {col['data_type']}")

            if schema_info["views"]:
                print(f"\nViews: {', '.join(schema_info['views'])}")

            return

        # Validate only
        if args.validate_only:
            logger.info("Validating existing data...")
            validation_results = validate_ingestion(dwh_manager)

            print("\n" + "=" * 60)
            print("DATA VALIDATION RESULTS")
            print("=" * 60)
            print(f"Status: {validation_results['status']}")

            if validation_results["checks"]:
                print("\nChecks:")
                for check_name, check_result in validation_results["checks"].items():
                    status = "✅ PASS" if check_result else "❌ FAIL"
                    print(f"  - {check_name}: {status}")

            if validation_results["errors"]:
                print("\nErrors:")
                for error in validation_results["errors"]:
                    print(f"  - {error}")

            return

        # Check schema status
        if args.check_schema:
            logger.info("Checking current schema status...")
            tables = dwh_manager.list_tables()
            print(f"\nCurrent tables: {tables}")

            required_tables = [
                "raw_house_data",
                "fact_house_transactions",
                "dim_locations",
                "dim_conditions",
                "dim_years",
            ]
            missing_tables = [table for table in required_tables if table not in tables]

            if missing_tables:
                print(f"\nMissing tables: {missing_tables}")
                print("Use --force-schema to recreate the complete schema")
            else:
                print("\nAll required tables exist!")

            return

        # Drop schema if requested
        if args.drop_schema:
            logger.info("Dropping existing schema...")
            drop_schema(dwh_manager)

        # Force schema recreation if requested
        if args.force_schema:
            logger.info("Force recreating schema...")
            drop_schema(dwh_manager)
            create_schema(dwh_manager)
            tables = dwh_manager.list_tables()
            logger.info(f"Schema recreated. Available tables: {tables}")

        # Check if CSV file exists
        csv_path = Path(args.csv_file)
        if not csv_path.exists():
            logger.error(f"CSV file not found: {csv_path}")
            sys.exit(1)

        # Ingest data
        logger.info(f"Starting data ingestion from: {csv_path}")

        # デバッグ: スキーマ作成後のテーブル確認
        logger.info("Checking tables after schema creation...")
        tables = dwh_manager.list_tables()
        logger.info(f"Available tables: {tables}")

        result = ingest_house_data(str(csv_path), dwh_manager)

        # Print results
        print("\n" + "=" * 60)
        print("DATA INGESTION RESULTS")
        print("=" * 60)
        print(f"Status: {result['ingestion_status']}")
        print(f"Timestamp: {result['timestamp']}")

        if result["ingestion_status"] == "success":
            print(f"\nRaw Data Stats:")
            print(f"  - Rows inserted: {result['raw_data_stats']['rows_inserted']}")
            print(f"  - Columns: {len(result['raw_data_stats']['columns'])}")

            print(f"\nFact Data Stats:")
            print(f"  - Rows inserted: {result['fact_data_stats']['rows_inserted']}")
            print(f"  - Rows processed: {result['fact_data_stats']['rows_processed']}")
            print(
                f"  - Rows with missing dimensions: {result['fact_data_stats']['rows_with_missing_dimensions']}"
            )

            if result["summary_statistics"]:
                summary = result["summary_statistics"]["summary"]
                if summary:
                    print(f"\nSummary Statistics:")
                    print(f"  - Total houses: {summary.get('total_houses', 'N/A')}")
                    if summary.get("avg_price"):
                        print(
                            f"  - Average price: ${summary.get('avg_price', 'N/A'):,.2f}"
                        )
                    else:
                        print("  - Average price: N/A")
                    if summary.get("avg_sqft"):
                        print(
                            f"  - Average sqft: {summary.get('avg_sqft', 'N/A'):,.0f}"
                        )
                    else:
                        print("  - Average sqft: N/A")
                    if summary.get("avg_price_per_sqft"):
                        print(
                            f"  - Average price per sqft: ${summary.get('avg_price_per_sqft', 'N/A'):,.2f}"
                        )
                    else:
                        print("  - Average price per sqft: N/A")

                location_analytics = result["summary_statistics"]["location_analytics"]
                if location_analytics:
                    print(f"\nLocation Analytics (Top 3):")
                    for i, location in enumerate(location_analytics[:3]):
                        print(
                            f"  {i+1}. {location['location_name']}: ${location['avg_price']:,.0f} avg price"
                        )

        # Validate the ingestion
        logger.info("Validating ingestion...")
        validation_results = validate_ingestion(dwh_manager)

        print(f"\nValidation Results:")
        print(f"  - Status: {validation_results['status']}")

        if validation_results["errors"]:
            print(f"  - Errors: {len(validation_results['errors'])}")
            for error in validation_results["errors"]:
                print(f"    * {error}")

        # Show final schema info
        schema_info = get_schema_info(dwh_manager)
        print(f"\nFinal Schema:")
        print(f"  - Tables: {schema_info['total_tables']}")
        print(f"  - Views: {schema_info['total_views']}")

        logger.info("DWH setup and data ingestion completed successfully!")

    except Exception as e:
        logger.error(f"DWH setup failed: {e}")
        sys.exit(1)

    finally:
        # Ensure connection is closed
        if "dwh_manager" in locals():
            dwh_manager.disconnect()


if __name__ == "__main__":
    main()
