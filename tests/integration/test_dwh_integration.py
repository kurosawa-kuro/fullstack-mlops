"""
統合テスト - DWH統合テスト
"""

import pytest
import os
import duckdb
from pathlib import Path


class TestDWHIntegration:
    """DWH統合テストクラス"""
    
    @pytest.fixture
    def dwh_path(self):
        """DWHパスを取得"""
        return "src/ml/data/dwh/data/house_price_dwh.duckdb"
    
    def test_dwh_file_exists(self, dwh_path):
        """DWHファイルが存在することを確認"""
        assert os.path.exists(dwh_path), f"DWHファイルが見つかりません: {dwh_path}"
    
    def test_dwh_connection(self, dwh_path):
        """DWHに接続できることを確認"""
        if os.path.exists(dwh_path):
            conn = duckdb.connect(dwh_path)
            assert conn is not None
            conn.close()
        else:
            pytest.skip("DWHファイルが存在しません")
    
    def test_dwh_tables_exist(self, dwh_path):
        """DWHテーブルが存在することを確認"""
        if os.path.exists(dwh_path):
            conn = duckdb.connect(dwh_path)
            tables = conn.execute("SHOW TABLES").fetchall()
            conn.close()
            
            # 最低限必要なテーブルが存在することを確認
            table_names = [table[0] for table in tables]
            assert "bronze_raw_house_data" in table_names, "bronze_raw_house_dataテーブルが見つかりません"
        else:
            pytest.skip("DWHファイルが存在しません")
    
    def test_dwh_data_exists(self, dwh_path):
        """DWHにデータが存在することを確認"""
        if os.path.exists(dwh_path):
            conn = duckdb.connect(dwh_path)
            count = conn.execute("SELECT COUNT(*) FROM bronze_raw_house_data").fetchone()[0]
            conn.close()
            
            assert count > 0, "DWHにデータが存在しません"
        else:
            pytest.skip("DWHファイルが存在しません") 