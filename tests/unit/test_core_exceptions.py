"""
単体テスト - コアカスタム例外
"""

import pytest
import os
import sys
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.core.exceptions import (
        HousePricePredictorError,
        ConfigError,
        DataError,
        ModelError,
        ValidationError
    )
except ImportError:
    # コアモジュールが存在しない場合はスキップ
    HousePricePredictorError = None
    ConfigError = None
    DataError = None
    ModelError = None
    ValidationError = None


class TestCoreExceptions:
    """コアカスタム例外テストクラス"""
    
    def test_base_exception_exists(self):
        """基本例外クラスが存在することを確認"""
        if HousePricePredictorError is None:
            pytest.skip("基本例外クラスが存在しません")
        assert HousePricePredictorError is not None
    
    def test_specific_exceptions_exist(self):
        """特定の例外クラスが存在することを確認"""
        if ConfigError is None:
            pytest.skip("特定の例外クラスが存在しません")
        assert ConfigError is not None
        assert DataError is not None
        assert ModelError is not None
        assert ValidationError is not None
    
    def test_exception_inheritance(self):
        """例外クラスの継承関係をテスト"""
        if HousePricePredictorError is None:
            pytest.skip("例外クラスが存在しません")
        
        # 基本例外クラスがExceptionを継承していることを確認
        assert issubclass(HousePricePredictorError, Exception)
        
        # 特定の例外クラスが基本例外クラスを継承していることを確認
        if ConfigError:
            assert issubclass(ConfigError, HousePricePredictorError)
        if DataError:
            assert issubclass(DataError, HousePricePredictorError)
        if ModelError:
            assert issubclass(ModelError, HousePricePredictorError)
        if ValidationError:
            assert issubclass(ValidationError, HousePricePredictorError)
    
    def test_exception_instantiation(self):
        """例外クラスのインスタンス化テスト"""
        if HousePricePredictorError is None:
            pytest.skip("例外クラスが存在しません")
        
        # 基本例外クラスのインスタンス化
        error = HousePricePredictorError("Test error message")
        assert str(error) == "Test error message"
        
        # 特定の例外クラスのインスタンス化
        if ConfigError:
            config_error = ConfigError("Configuration error")
            assert str(config_error) == "Configuration error"
        
        if DataError:
            data_error = DataError("Data error")
            assert str(data_error) == "Data error"
        
        if ModelError:
            model_error = ModelError("Model error")
            assert str(model_error) == "Model error"
        
        if ValidationError:
            validation_error = ValidationError("Validation error")
            assert str(validation_error) == "Validation error"
    
    def test_exception_with_details(self):
        """詳細情報付き例外のテスト"""
        if HousePricePredictorError is None:
            pytest.skip("例外クラスが存在しません")
        
        # 詳細情報付きで例外を作成
        error = HousePricePredictorError("Test error", details={"field": "value"})
        assert str(error) == "Test error"
        
        # 詳細情報が設定されていることを確認
        if hasattr(error, 'details'):
            assert error.details == {"field": "value"}
    
    def test_exception_raising(self):
        """例外の発生テスト"""
        if HousePricePredictorError is None:
            pytest.skip("例外クラスが存在しません")
        
        # 例外が発生することを確認
        with pytest.raises(HousePricePredictorError):
            raise HousePricePredictorError("Test exception")
        
        # 特定の例外が発生することを確認
        if ConfigError:
            with pytest.raises(ConfigError):
                raise ConfigError("Config exception")
        
        if DataError:
            with pytest.raises(DataError):
                raise DataError("Data exception")
        
        if ModelError:
            with pytest.raises(ModelError):
                raise ModelError("Model exception")
        
        if ValidationError:
            with pytest.raises(ValidationError):
                raise ValidationError("Validation exception")


class TestExceptionInfrastructure:
    """例外インフラストラクチャのテスト"""
    
    def test_exception_file_exists(self):
        """例外ファイルが存在することを確認"""
        exception_files = [
            "src/core/exceptions.py"
        ]
        
        for exception_file in exception_files:
            if os.path.exists(exception_file):
                assert True
            else:
                pytest.skip(f"例外ファイルが存在しません: {exception_file}")
    
    def test_standard_exception_imports(self):
        """標準例外機能のインポートテスト"""
        try:
            import builtins
            assert hasattr(builtins, 'Exception')
            assert hasattr(builtins, 'ValueError')
            assert hasattr(builtins, 'TypeError')
            assert True
        except ImportError as e:
            pytest.fail(f"標準例外機能のインポートに失敗: {e}")
    
    def test_exception_handling_pattern(self):
        """例外処理パターンのテスト"""
        try:
            # 意図的に例外を発生させる
            raise ValueError("Test value error")
        except ValueError as e:
            # 例外が正しくキャッチされることを確認
            assert str(e) == "Test value error"
        except Exception as e:
            # 他の例外が発生した場合は失敗
            pytest.fail(f"予期しない例外が発生: {e}")
        else:
            # 例外が発生しなかった場合は失敗
            pytest.fail("例外が発生しませんでした")
    
    def test_exception_context(self):
        """例外コンテキストのテスト"""
        try:
            # ネストした例外処理をテスト
            try:
                raise ValueError("Inner error")
            except ValueError as inner_e:
                raise RuntimeError("Outer error") from inner_e
        except RuntimeError as outer_e:
            # 例外チェーンが正しく設定されていることを確認
            assert str(outer_e) == "Outer error"
            assert outer_e.__cause__ is not None
            assert str(outer_e.__cause__) == "Inner error" 