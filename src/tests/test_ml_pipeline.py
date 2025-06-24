import os

import joblib
import pandas as pd
import pytest
import yaml


class TestModelPipeline:
    """MLモデルパイプラインのテストクラス"""

    def test_model_files_exist(self):
        """学習済みモデルファイルが存在することを確認"""
        model_path = "src/ml/models/trained/house_price_prediction.pkl"
        preprocessor_path = "src/ml/models/trained/preprocessor.pkl"

        assert os.path.exists(model_path), f"モデルファイルが見つかりません: {model_path}"
        assert os.path.exists(
            preprocessor_path
        ), f"前処理ファイルが見つかりません: {preprocessor_path}"

    def test_model_can_load(self):
        """モデルが正常に読み込めることを確認"""
        model_path = "src/ml/models/trained/house_price_prediction.pkl"
        preprocessor_path = "src/ml/models/trained/preprocessor.pkl"

        try:
            model = joblib.load(model_path)
            preprocessor = joblib.load(preprocessor_path)
            assert model is not None, "モデルがNoneです"
            assert preprocessor is not None, "前処理器がNoneです"
        except Exception as e:
            pytest.fail(f"モデルの読み込みに失敗しました: {e}")

    def test_model_can_predict(self):
        """モデルが予測を実行できることを確認"""
        model_path = "src/ml/models/trained/house_price_prediction.pkl"
        preprocessor_path = "src/ml/models/trained/preprocessor.pkl"

        # テスト用のサンプルデータ
        sample_data = pd.DataFrame(
            {
                "sqft": [1500],
                "bedrooms": [3],
                "bathrooms": [2],
                "year_built": [2010],
                "location": ["Suburban"],
                "condition": ["Good"],
            }
        )
        # 特徴量エンジニアリングで追加されるカラムを再現
        sample_data["house_age"] = 2024 - sample_data["year_built"]  # 年は適宜調整
        sample_data["bed_bath_ratio"] = (
            sample_data["bedrooms"] / sample_data["bathrooms"]
        )
        sample_data["price_per_sqft"] = 0  # テスト用なのでダミー値でOK（予測には使われない）

        try:
            model = joblib.load(model_path)
            preprocessor = joblib.load(preprocessor_path)

            # 前処理を適用
            X_transformed = preprocessor.transform(sample_data)

            # 予測を実行
            prediction = model.predict(X_transformed)

            assert len(prediction) == 1, "予測結果の数が正しくありません"
            assert prediction[0] > 0, "予測価格が正の値ではありません"

        except Exception as e:
            pytest.fail(f"予測の実行に失敗しました: {e}")

    def test_config_file_exists(self):
        """設定ファイルが存在することを確認"""
        config_path = "src/configs/model.yaml"
        assert os.path.exists(config_path), f"設定ファイルが見つかりません: {config_path}"

    def test_config_file_valid(self):
        """設定ファイルが有効なYAML形式であることを確認"""
        config_path = "src/configs/model.yaml"

        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)

            # 必要な設定項目が存在することを確認
            assert "model" in config, "設定ファイルに'model'セクションがありません"
            assert "data" in config, "設定ファイルに'data'セクションがありません"
            assert "features" in config, "設定ファイルに'features'セクションがありません"

        except Exception as e:
            pytest.fail(f"設定ファイルの読み込みに失敗しました: {e}")

    def test_processed_data_exists(self):
        """処理済みデータファイルが存在することを確認"""
        processed_data_path = "src/ml/data/processed/featured_house_data.csv"
        assert os.path.exists(
            processed_data_path
        ), f"処理済みデータが見つかりません: {processed_data_path}"

    def test_processed_data_valid(self):
        """処理済みデータが有効なCSV形式であることを確認"""
        processed_data_path = "src/ml/data/processed/featured_house_data.csv"

        try:
            df = pd.read_csv(processed_data_path)
            assert not df.empty, "処理済みデータが空です"
            assert "price" in df.columns, "処理済みデータに'price'列がありません"

        except Exception as e:
            pytest.fail(f"処理済みデータの読み込みに失敗しました: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
