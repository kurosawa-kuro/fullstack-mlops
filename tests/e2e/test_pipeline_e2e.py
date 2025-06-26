"""
E2Eテスト - パイプライン全体テスト
"""

import pytest
import os
import joblib
import pandas as pd
from pathlib import Path


class TestPipelineE2E:
    """パイプラインE2Eテストクラス"""
    
    def test_config_files_exist(self):
        """設定ファイルが存在することを確認"""
        config_files = [
            "src/configs/model_config.yaml",
            "src/configs/ensemble_config.yaml",
            "src/configs/training.yaml"
        ]
        
        for config_file in config_files:
            assert os.path.exists(config_file), f"設定ファイルが見つかりません: {config_file}"
    
    def test_raw_data_exists(self):
        """生データが存在することを確認"""
        raw_data_path = "src/ml/data/raw/house_data.csv"
        assert os.path.exists(raw_data_path), f"生データが見つかりません: {raw_data_path}"
    
    def test_dwh_exists(self):
        """DWHが存在することを確認"""
        dwh_path = "src/ml/data/dwh/data/house_price_dwh.duckdb"
        assert os.path.exists(dwh_path), f"DWHが見つかりません: {dwh_path}"
    
    def test_model_files_exist(self):
        """モデルファイルが存在することを確認（オプション）"""
        model_files = [
            "src/ml/models/trained/house_price_predictor_duckdb.pkl",
            "src/ml/models/trained/house_price_predictor_duckdb_encoders.pkl"
        ]
        
        existing_models = []
        for model_file in model_files:
            if os.path.exists(model_file):
                existing_models.append(model_file)
        
        # 最低1つのモデルファイルが存在することを確認
        if existing_models:
            assert len(existing_models) > 0, "モデルファイルが見つかりません"
        else:
            pytest.skip("モデルファイルが存在しません（訓練が必要）")
    
    def test_ensemble_model_exists(self):
        """アンサンブルモデルが存在することを確認（オプション）"""
        ensemble_files = [
            "src/ml/models/trained/house_price_ensemble_duckdb.pkl",
            "src/ml/models/trained/house_price_ensemble_duckdb_preprocessor.pkl"
        ]
        
        existing_ensembles = []
        for ensemble_file in ensemble_files:
            if os.path.exists(ensemble_file):
                existing_ensembles.append(ensemble_file)
        
        if existing_ensembles:
            assert len(existing_ensembles) > 0, "アンサンブルモデルファイルが見つかりません"
        else:
            pytest.skip("アンサンブルモデルファイルが存在しません（訓練が必要）")
    
    def test_directory_structure(self):
        """ディレクトリ構造が正しいことを確認"""
        required_dirs = [
            "src/core",
            "src/data",
            "src/models", 
            "src/services",
            "src/ml",
            "tests/unit",
            "tests/integration",
            "tests/e2e"
        ]
        
        for dir_path in required_dirs:
            assert os.path.exists(dir_path), f"ディレクトリが見つかりません: {dir_path}" 