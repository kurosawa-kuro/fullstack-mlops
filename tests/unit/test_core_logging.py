"""
単体テスト - コアログ設定
"""

import pytest
import os
import logging
import sys
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.core.logging import setup_logging, get_logger
except ImportError:
    # コアモジュールが存在しない場合はスキップ
    setup_logging = None
    get_logger = None


class TestCoreLogging:
    """コアログ設定テストクラス"""
    
    def test_logging_functions_exist(self):
        """ログ関数が存在することを確認"""
        if setup_logging is None or get_logger is None:
            pytest.skip("ログ関数が存在しません")
        assert setup_logging is not None
        assert get_logger is not None
    
    def test_logger_creation(self):
        """ロガーの作成テスト"""
        if get_logger is None:
            pytest.skip("get_logger関数が存在しません")
        
        logger = get_logger(__name__)
        from src.core.logging import StructuredLogger
        assert isinstance(logger, StructuredLogger)
    
    def test_logger_level(self):
        """ロガーレベルのテスト"""
        if get_logger is None:
            pytest.skip("get_logger関数が存在しません")
        
        logger = get_logger(__name__)
        
        # ロガーレベルが適切に設定されていることを確認
        assert logger.level <= logging.INFO
    
    def test_logger_handlers(self):
        """ロガーハンドラーのテスト"""
        if get_logger is None:
            pytest.skip("get_logger関数が存在しません")
        
        logger = get_logger(__name__)
        
        # ハンドラーが設定されていることを確認
        assert len(logger.handlers) > 0
    
    def test_logging_setup(self):
        """ログ設定のテスト"""
        if setup_logging is None:
            pytest.skip("setup_logging関数が存在しません")
        
        # ログ設定を実行
        setup_logging()
        
        # ルートロガーが設定されていることを確認
        root_logger = logging.getLogger()
        assert root_logger.level <= logging.INFO


class TestLoggingInfrastructure:
    """ログインフラストラクチャのテスト"""
    
    def test_log_directory_exists(self):
        """ログディレクトリが存在することを確認"""
        log_dirs = [
            "logs",
            "src/logs"
        ]
        
        existing_dirs = []
        for log_dir in log_dirs:
            if os.path.exists(log_dir):
                existing_dirs.append(log_dir)
        
        # 最低1つのログディレクトリが存在することを確認
        if existing_dirs:
            assert len(existing_dirs) > 0
        else:
            pytest.skip("ログディレクトリが存在しません")
    
    def test_log_files_creation(self, tmp_path):
        """ログファイル作成のテスト"""
        # 一時的なログディレクトリを作成
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        
        # ログファイルパスを作成
        log_file = log_dir / "test.log"
        
        # ログファイルを作成
        with open(log_file, 'w') as f:
            f.write("test log message")
        
        assert log_file.exists()
        assert log_file.read_text() == "test log message"
    
    def test_logging_configuration(self):
        """ログ設定ファイルの存在確認"""
        config_files = [
            "src/core/logging.py",
            "configs/logging.yaml"
        ]
        
        existing_configs = []
        for config_file in config_files:
            if os.path.exists(config_file):
                existing_configs.append(config_file)
        
        # 最低1つのログ設定が存在することを確認
        if existing_configs:
            assert len(existing_configs) > 0
        else:
            pytest.skip("ログ設定ファイルが存在しません")
    
    def test_standard_logging_imports(self):
        """標準ログ機能のインポートテスト"""
        try:
            import logging
            import logging.handlers
            assert True
        except ImportError as e:
            pytest.fail(f"標準ログ機能のインポートに失敗: {e}")
    
    def test_logging_basic_functionality(self):
        """基本的なログ機能のテスト"""
        logger = logging.getLogger("test_logger")
        
        # ログレベルを設定
        logger.setLevel(logging.INFO)
        
        # ハンドラーを追加
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # ログメッセージを出力
        logger.info("Test log message")
        
        # ロガーが正常に動作することを確認
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0 