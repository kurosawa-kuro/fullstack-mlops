#!/usr/bin/env python3
"""
Bronze Layer Setup Script

This script sets up the Bronze layer and ingests raw data from CSV.
Only raw data ingestion is performed - no transformation or feature engineering.
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
    from ml.data.dwh.core import (DWHManager, ingest_bronze_data,
                                  validate_bronze_ingestion)

    print("Successfully imported ml.data.dwh.core modules")
except ImportError as e:
    print(f"ml.data.dwh.core import error: {e}")
    # 代替手段として相対インポートを試す
    try:
        from ..core.database import DWHManager
        from ..core.ingestion import (ingest_bronze_data,
                                      validate_bronze_ingestion)

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
            logging.FileHandler("bronze_setup.log"),
        ],
    )


def main():
    """Main function to setup Bronze layer and ingest data"""
    parser = argparse.ArgumentParser(
        description="Setup Bronze layer and ingest raw house data"
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
        "--validate-only",
        action="store_true",
        help="Only validate existing Bronze data without ingestion",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
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

        # Validate only
        if args.validate_only:
            logger.info("Validating existing Bronze data...")
            validation_results = validate_bronze_ingestion(dwh_manager)

            print("\n" + "=" * 60)
            print("BRONZE LAYER VALIDATION RESULTS")
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

        # Check if CSV file exists
        csv_path = Path(args.csv_file)
        if not csv_path.exists():
            logger.error(f"CSV file not found: {csv_path}")
            sys.exit(1)

        # Ingest Bronze data
        logger.info(f"Starting Bronze layer ingestion from: {csv_path}")
        result = ingest_bronze_data(str(csv_path), dwh_manager)

        # Print results
        print("\n" + "=" * 60)
        print("BRONZE LAYER INGESTION RESULTS")
        print("=" * 60)
        print(f"Status: {result['ingestion_status']}")
        print(f"Timestamp: {result['timestamp']}")

        if result["ingestion_status"] == "success":
            print(f"\nBronze Data Stats:")
            print(f"  - Rows inserted: {result['bronze_data_stats']['rows_inserted']}")
            print(f"  - Columns: {len(result['bronze_data_stats']['columns'])}")

        # Validate the ingestion
        logger.info("Validating Bronze ingestion...")
        validation_results = validate_bronze_ingestion(dwh_manager)

        print(f"\nValidation Results:")
        print(f"  - Status: {validation_results['status']}")

        if validation_results["errors"]:
            print(f"  - Errors: {len(validation_results['errors'])}")
            for error in validation_results["errors"]:
                print(f"    * {error}")

        logger.info("Bronze layer setup and data ingestion completed successfully!")

    except Exception as e:
        logger.error(f"Bronze layer setup failed: {e}")
        sys.exit(1)

    finally:
        # Ensure connection is closed
        if "dwh_manager" in locals():
            dwh_manager.disconnect()


if __name__ == "__main__":
    main()
