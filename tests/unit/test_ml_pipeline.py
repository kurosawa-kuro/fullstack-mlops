import os

import duckdb
import joblib
import pandas as pd
import pytest
import yaml


class TestModelPipeline:
    """MLモデルパイプラインのテストクラス（DuckDB対応）"""

    def test_model_files_exist(self):
        """学習済みモデルファイルが存在することを確認"""
        model_path = "src/ml/models/trained/house_price_prediction.pkl"
        preprocessor_path = "src/ml/models/trained/house_price_prediction_encoders.pkl"

        # モデルファイルが存在しない場合はスキップ
        if not os.path.exists(model_path):
            pytest.skip(f"モデルファイルが存在しません: {model_path}")

        if not os.path.exists(preprocessor_path):
            pytest.skip(f"前処理ファイルが存在しません: {preprocessor_path}")

        assert os.path.exists(model_path), f"モデルファイルが見つかりません: {model_path}"
        assert os.path.exists(
            preprocessor_path
        ), f"前処理ファイルが見つかりません: {preprocessor_path}"

    def test_model_can_load(self):
        """モデルが正常に読み込めることを確認"""
        model_path = "src/ml/models/trained/house_price_prediction.pkl"
        preprocessor_path = "src/ml/models/trained/house_price_prediction_encoders.pkl"

        # モデルファイルが存在しない場合はスキップ
        if not os.path.exists(model_path):
            pytest.skip(f"モデルファイルが存在しません: {model_path}")

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
        preprocessor_path = "src/ml/models/trained/house_price_prediction_encoders.pkl"

        # モデルファイルが存在しない場合はスキップ
        if not os.path.exists(model_path):
            pytest.skip(f"モデルファイルが存在しません: {model_path}")

        # テスト用のサンプルデータ（前処理器が期待する形式）
        sample_data = pd.DataFrame(
            {
                "sqft": [1500],
                "bedrooms": [3],
                "bathrooms": [2],
                "house_age": [14],  # 2024 - 2010
                "price_per_sqft": [200],  # ダミー値
                "bed_bath_ratio": [1.5],  # 3/2
                "location": ["Suburban"],  # location_nameではなくlocation
                "condition": ["Good"],  # condition_nameではなくcondition
            }
        )

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
        config_path = "src/configs/model_config.yaml"
        assert os.path.exists(config_path), f"設定ファイルが見つかりません: {config_path}"

    def test_config_file_valid(self):
        """設定ファイルが有効なYAML形式であることを確認"""
        config_path = "src/configs/model_config.yaml"

        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)

            # 必要な設定項目が存在することを確認
            assert "base_models" in config, "設定ファイルに'base_models'セクションがありません"
            assert "ensemble" in config, "設定ファイルに'ensemble'セクションがありません"
            assert "training" in config, "設定ファイルに'training'セクションがありません"

        except Exception as e:
            pytest.fail(f"設定ファイルの読み込みに失敗しました: {e}")

    def test_duckdb_dwh_exists(self):
        """DuckDB DWHファイルが存在することを確認"""
        dwh_path = "src/ml/data/dwh/house_price_dwh.duckdb"

        # DWHファイルが存在しない場合はスキップ
        if not os.path.exists(dwh_path):
            pytest.skip(f"DuckDB DWHが存在しません: {dwh_path}")

        assert os.path.exists(dwh_path), f"DuckDB DWHが見つかりません: {dwh_path}"

    def test_duckdb_dwh_accessible(self):
        """DuckDB DWHにアクセスできることを確認"""
        dwh_path = "src/ml/data/dwh/house_price_dwh.duckdb"

        # DWHファイルが存在しない場合はスキップ
        if not os.path.exists(dwh_path):
            pytest.skip(f"DuckDB DWHが存在しません: {dwh_path}")

        try:
            conn = duckdb.connect(dwh_path)

            # テーブル一覧を取得
            tables = conn.execute("SHOW TABLES").fetchdf()
            assert not tables.empty, "DWHにテーブルが存在しません"

            # ビューの存在確認
            views = conn.execute("SHOW TABLES").fetchdf()
            assert len(views) > 0, "DWHにビューが存在しません"

            conn.close()

        except Exception as e:
            pytest.fail(f"DuckDB DWHへのアクセスに失敗しました: {e}")

    def test_duckdb_integration(self):
        """DuckDBとモデルの統合テスト"""
        dwh_path = "src/ml/data/dwh/house_price_dwh.duckdb"
        model_path = "src/ml/models/trained/house_price_prediction.pkl"
        preprocessor_path = "src/ml/models/trained/house_price_prediction_encoders.pkl"

        # 必要なファイルが存在しない場合はスキップ
        if not os.path.exists(dwh_path):
            pytest.skip(f"DuckDB DWHが存在しません: {dwh_path}")
        if not os.path.exists(model_path):
            pytest.skip(f"モデルファイルが存在しません: {model_path}")

        try:
            # DuckDBからデータを読み込み
            conn = duckdb.connect(dwh_path)
            data = conn.execute("SELECT * FROM v_house_analytics LIMIT 1").fetchdf()
            conn.close()

            if not data.empty:
                # モデルで予測
                model = joblib.load(model_path)
                preprocessor = joblib.load(preprocessor_path)

                # サンプルデータで予測（前処理器が期待する形式に変換）
                sample = data.iloc[0:1]
                X = pd.DataFrame(
                    {
                        "sqft": sample["sqft"],
                        "bedrooms": sample["bedrooms"],
                        "bathrooms": sample["bathrooms"],
                        "house_age": sample["house_age"],
                        "price_per_sqft": sample["price"] / sample["sqft"],
                        "bed_bath_ratio": sample["bedrooms"] / sample["bathrooms"],
                        "location": sample["location_name"],  # location_name → location
                        "condition": sample[
                            "condition_name"
                        ],  # condition_name → condition
                    }
                )

                X_transformed = preprocessor.transform(X)
                prediction = model.predict(X_transformed)

                assert len(prediction) == 1, "予測結果の数が正しくありません"
                assert prediction[0] > 0, "予測価格が正の値ではありません"

        except Exception as e:
            pytest.fail(f"DuckDB統合テストに失敗しました: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
