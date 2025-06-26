#!/usr/bin/env python3
"""
DuckDB DWH Explorer
DuckDBデータベースの内容を探索・表示するスクリプト
"""

import os
import sys
from pathlib import Path

import duckdb
import pandas as pd

# Add src to path for imports
script_path = Path(__file__).resolve()
src_path = script_path.parents[5]  # Go up to src directory
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def explore_dwh(database_path: str):
    """DuckDBデータベースの内容を探索・表示"""

    print("=" * 60)
    print("🏠 HOUSE PRICE DWH EXPLORER")
    print("=" * 60)

    # Connect to database
    con = duckdb.connect(database_path)

    try:
        # Get all tables
        tables_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        tables = con.execute(tables_query).fetchall()
        table_names = [table[0] for table in tables]

        print(f"\n📊 テーブル一覧 ({len(table_names)}個):")
        for i, table in enumerate(table_names, 1):
            print(f"  {i}. {table}")

        # Get all views
        views_query = "SELECT table_name FROM information_schema.views WHERE table_schema = 'main'"
        views = con.execute(views_query).fetchall()
        view_names = [view[0] for view in views]

        if view_names:
            print(f"\n👁️ ビュー一覧 ({len(view_names)}個):")
            for i, view in enumerate(view_names, 1):
                print(f"  {i}. {view}")

        # Show sample data from each table
        print("\n" + "=" * 60)
        print("📋 テーブル詳細")
        print("=" * 60)

        for table_name in table_names:
            print(f"\n🔍 {table_name}:")
            print("-" * 40)

            # Get row count
            count_query = f"SELECT COUNT(*) FROM {table_name}"
            count = con.execute(count_query).fetchone()[0]
            print(f"行数: {count:,}")

            # Get column info
            schema_query = f"DESCRIBE {table_name}"
            schema = con.execute(schema_query).fetchall()
            print("列構成:")
            for col in schema:
                print(f"  - {col[0]}: {col[1]}")

            # Show sample data (first 5 rows)
            if count > 0:
                sample_query = f"SELECT * FROM {table_name} LIMIT 5"
                sample_df = con.execute(sample_query).df()
                print("\nサンプルデータ:")
                print(sample_df.to_string(index=False))

        # Show view contents
        if view_names:
            print("\n" + "=" * 60)
            print("👁️ ビュー詳細")
            print("=" * 60)

            for view_name in view_names:
                print(f"\n🔍 {view_name}:")
                print("-" * 40)

                # Get row count
                count_query = f"SELECT COUNT(*) FROM {view_name}"
                count = con.execute(count_query).fetchone()[0]
                print(f"行数: {count:,}")

                # Show sample data
                if count > 0:
                    sample_query = f"SELECT * FROM {view_name} LIMIT 5"
                    sample_df = con.execute(sample_query).df()
                    print("\nサンプルデータ:")
                    print(sample_df.to_string(index=False))

        # Show summary statistics
        print("\n" + "=" * 60)
        print("📈 サマリー統計")
        print("=" * 60)

        # Basic stats from fact table
        if "fact_house_transactions" in table_names:
            stats_query = """
            SELECT 
                COUNT(*) as total_houses,
                AVG(price) as avg_price,
                MIN(price) as min_price,
                MAX(price) as max_price,
                AVG(sqft) as avg_sqft,
                AVG(price/sqft) as avg_price_per_sqft
            FROM fact_house_transactions
            """
            stats = con.execute(stats_query).fetchone()

            print(f"総住宅数: {stats[0]:,}")
            print(f"平均価格: ${stats[1]:,.2f}")
            print(f"最低価格: ${stats[2]:,.2f}")
            print(f"最高価格: ${stats[3]:,.2f}")
            print(f"平均面積: {stats[4]:,.0f} sqft")
            print(f"平均単価: ${stats[5]:,.2f}/sqft")

        # Location analysis
        if "v_location_analytics" in view_names:
            print(f"\n📍 地域別分析:")
            loc_query = "SELECT * FROM v_location_analytics ORDER BY avg_price DESC"
            loc_df = con.execute(loc_query).df()
            print(loc_df.to_string(index=False))

        # Condition analysis
        if "v_condition_analytics" in view_names:
            print(f"\n🏠 状態別分析:")
            cond_query = "SELECT * FROM v_condition_analytics ORDER BY avg_price DESC"
            cond_df = con.execute(cond_query).df()
            print(cond_df.to_string(index=False))

    finally:
        con.close()


def main():
    """メイン関数"""
    database_path = "src/ml/data/dwh/data/house_price_dwh.duckdb"

    if not os.path.exists(database_path):
        print(f"❌ エラー: データベースファイルが見つかりません: {database_path}")
        print("先に setup_dwh.py を実行してください。")
        return

    explore_dwh(database_path)


if __name__ == "__main__":
    main()
