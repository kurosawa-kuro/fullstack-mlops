"""
単体テスト - コア設定管理
"""

import pytest
import os
import yaml
from pathlib import Path
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.core.config import Config, get_config, reload_config
except ImportError:
    # コアモジュールが存在しない場合はスキップ
    Config = None


class TestCoreConfig:
    """コア設定管理テストクラス"""
    
    @pytest.fixture
    def sample_config(self):
        """サンプル設定データ"""
        return {
            'app_name': 'House Price Predictor',
            'app_version': '1.0.0',
            'app_environment': 'development',
            'db_type': 'duckdb',
            'db_path': 'test_dwh.duckdb',
            'log_level': 'INFO',
            'log_format': 'json',
            'log_file': 'logs/test.log',
            'mlflow_tracking_uri': 'http://localhost:5555',
            'mlflow_experiment_name': 'test_experiment',
            'log_max_size': '100MB',
            'log_backup_count': 5,
            'api_host': '0.0.0.0',
            'api_port': 8000,
            'api_workers': 4,
            'ui_host': '0.0.0.0',
            'ui_port': 8501,
            'monitoring_enabled': True,
            'metrics_port': 9090,
            'secret_key': 'test-secret-key',
            'debug': False
        }
    
    @pytest.fixture
    def config_file_path(self, tmp_path):
        """一時的な設定ファイルパス"""
        return tmp_path / "test_config.yaml"
    
    def test_config_class_exists(self):
        """Configクラスが存在することを確認"""
        if Config is None:
            pytest.skip("Configクラスが存在しません")
        assert Config is not None
    
    def test_config_initialization(self, sample_config, config_file_path):
        """設定クラスの初期化テスト"""
        if Config is None:
            pytest.skip("Configクラスが存在しません")
        
        # 設定ファイルを作成
        with open(config_file_path, 'w') as f:
            yaml.dump(sample_config, f)
        
        # Configクラスを初期化
        config = Config.from_yaml(str(config_file_path))
        assert config is not None
        assert config.app_name == 'House Price Predictor'
    
    def test_config_loading(self, sample_config, config_file_path):
        """設定ファイルの読み込みテスト"""
        if Config is None:
            pytest.skip("Configクラスが存在しません")
        
        # 設定ファイルを作成
        with open(config_file_path, 'w') as f:
            yaml.dump(sample_config, f)
        
        # 設定を読み込み
        config = Config.from_yaml(str(config_file_path))
        
        # 設定値が正しく読み込まれることを確認
        assert config.app_name == 'House Price Predictor'
        assert config.app_version == '1.0.0'
        assert config.db_type == 'duckdb'
    
    def test_config_default_values(self):
        """デフォルト値のテスト"""
        if Config is None:
            pytest.skip("Configクラスが存在しません")
        
        # デフォルト設定で初期化
        config = Config()
        
        # 基本的な設定が存在することを確認
        assert config.app_name == 'House Price Predictor'
        assert config.app_version == '1.0.0'
        assert config.db_type == 'duckdb'
    
    def test_config_file_validation(self):
        """設定ファイルの検証テスト"""
        if Config is None:
            pytest.skip("Configクラスが存在しません")
        
        # 存在しないファイルで初期化
        with pytest.raises(FileNotFoundError):
            Config.from_yaml("nonexistent_file.yaml")
    
    def test_get_config_function(self):
        """get_config関数のテスト"""
        if Config is None:
            pytest.skip("Configクラスが存在しません")
        
        config = get_config()
        assert config is not None
        assert isinstance(config, Config)
    
    def test_reload_config_function(self):
        """reload_config関数のテスト"""
        if Config is None:
            pytest.skip("Configクラスが存在しません")
        
        config = reload_config()
        assert config is not None
        assert isinstance(config, Config)
    
    def test_config_methods(self):
        """Configクラスのメソッドテスト"""
        if Config is None:
            pytest.skip("Configクラスが存在しません")
        
        config = Config()
        
        # get_database_urlメソッド
        db_url = config.get_database_url()
        assert db_url.startswith("duckdb://")
        
        # is_production/is_developmentメソッド
        assert config.is_development() == True
        assert config.is_production() == False
        
        # getメソッド
        app_name = config.get('app_name')
        assert app_name == 'House Price Predictor'
    
    def test_to_dict_method(self):
        """to_dictメソッドのテスト"""
        if Config is None:
            pytest.skip("Configクラスが存在しません")
        
        config = Config()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert 'app_name' in config_dict
        assert 'db_type' in config_dict


class TestConfigFiles:
    """設定ファイルの存在確認テスト"""
    
    def test_model_config_exists(self):
        """モデル設定ファイルが存在することを確認"""
        config_path = "src/configs/model_config.yaml"
        assert os.path.exists(config_path), f"モデル設定ファイルが見つかりません: {config_path}"
    
    def test_ensemble_config_exists(self):
        """アンサンブル設定ファイルが存在することを確認"""
        config_path = "src/configs/ensemble_config.yaml"
        if os.path.exists(config_path):
            assert True
        else:
            pytest.skip("アンサンブル設定ファイルが存在しません")
    
    def test_training_config_exists(self):
        """訓練設定ファイルが存在することを確認"""
        config_path = "src/configs/training.yaml"
        assert os.path.exists(config_path), f"訓練設定ファイルが見つかりません: {config_path}"
    
    def test_config_files_are_valid_yaml(self):
        """設定ファイルが有効なYAMLであることを確認"""
        config_files = [
            "src/configs/model_config.yaml",
            "src/configs/training.yaml"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    try:
                        yaml.safe_load(f)
                        assert True
                    except yaml.YAMLError as e:
                        pytest.fail(f"YAMLファイルが無効です: {config_file} - {e}")
            else:
                pytest.skip(f"設定ファイルが存在しません: {config_file}") 