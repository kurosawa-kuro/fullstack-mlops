import argparse  # コマンドライン引数を解析するためのモジュール
import logging  # ログ出力機能を提供するモジュール
import platform  # プラットフォーム情報を取得するモジュール

import joblib  # モデルの保存・読み込みライブラリ
import mlflow  # MLflowのメインモジュール
import mlflow.sklearn  # scikit-learnモデル用のMLflowモジュール
import numpy as np  # 数値計算ライブラリ
import pandas as pd  # データ分析ライブラリ
import sklearn  # scikit-learnライブラリ
import xgboost as xgb  # XGBoostライブラリ
import yaml  # YAMLファイル読み込みライブラリ
from mlflow.tracking import MlflowClient  # MLflowクライアント
from sklearn.ensemble import (GradientBoostingRegressor,  # アンサンブル学習アルゴリズム
                              RandomForestRegressor)
from sklearn.linear_model import LinearRegression  # 線形回帰アルゴリズム
from sklearn.metrics import mean_absolute_error, r2_score  # 評価指標
from sklearn.model_selection import train_test_split  # データ分割機能

# -----------------------------
# Configure logging
# -----------------------------
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)  # ログの基本設定（レベル、フォーマット）
logger = logging.getLogger(__name__)  # ロガーインスタンスを作成


# -----------------------------
# Argument parser
# -----------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Train and register final model from config."
    )  # 引数パーサーを作成
    parser.add_argument(
        "--config", type=str, required=True, help="Path to model_config.yaml"
    )  # 設定ファイルパスの引数を定義
    parser.add_argument(
        "--data", type=str, required=True, help="Path to processed CSV dataset"
    )  # データファイルパスの引数を定義
    parser.add_argument(
        "--models-dir", type=str, required=True, help="Directory to save trained model"
    )  # モデル保存ディレクトリの引数を定義
    parser.add_argument(
        "--mlflow-tracking-uri", type=str, default=None, help="MLflow tracking URI"
    )  # MLflow追跡URIの引数を定義
    return parser.parse_args()  # コマンドライン引数を解析して返す


# -----------------------------
# Load model from config
# -----------------------------
def get_model_instance(name, params):
    model_map = {
        "LinearRegression": LinearRegression,  # 線形回帰
        "RandomForest": RandomForestRegressor,  # ランダムフォレスト
        "GradientBoosting": GradientBoostingRegressor,  # 勾配ブースティング
        "XGBoost": xgb.XGBRegressor,  # XGBoost
    }  # モデル名とクラスのマッピング
    if name not in model_map:  # サポートされていないモデルの場合
        raise ValueError(f"Unsupported model: {name}")  # エラーを発生
    return model_map[name](**params)  # 指定されたパラメータでモデルインスタンスを作成して返す


# -----------------------------
# Main logic
# -----------------------------
def main(args):
    # Load config
    with open(args.config, "r") as f:  # 設定ファイルを開く
        config = yaml.safe_load(f)  # YAMLファイルを読み込み
    model_cfg = config["model"]  # モデル設定を取得

    if args.mlflow_tracking_uri:  # MLflow追跡URIが指定されている場合
        mlflow.set_tracking_uri(args.mlflow_tracking_uri)  # MLflow追跡URIを設定
        mlflow.set_experiment(model_cfg["name"])  # 実験名を設定

    # Load data
    data = pd.read_csv(args.data)  # CSVファイルを読み込み
    target = model_cfg["target_variable"]  # ターゲット変数名を取得

    # Use all features except the target variable
    X = data.drop(columns=[target])  # 特徴量を抽出（ターゲット変数を除外）
    y = data[target]  # ターゲット変数を抽出
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )  # データを訓練用とテスト用に分割

    # Get model
    model = get_model_instance(
        model_cfg["best_model"], model_cfg["parameters"]
    )  # モデルインスタンスを作成

    # Start MLflow run
    with mlflow.start_run(run_name="final_training"):  # MLflow実行を開始
        logger.info(f"Training model: {model_cfg['best_model']}")  # モデル学習開始のログ
        model.fit(X_train, y_train)  # モデルを学習
        y_pred = model.predict(X_test)  # テストデータで予測

        mae = float(mean_absolute_error(y_test, y_pred))  # 平均絶対誤差を計算
        r2 = float(r2_score(y_test, y_pred))  # 決定係数を計算

        # Log params and metrics
        mlflow.log_params(model_cfg["parameters"])  # パラメータをログに記録
        mlflow.log_metrics({"mae": mae, "r2": r2})  # 評価指標をログに記録

        # Log and register model
        mlflow.sklearn.log_model(
            model,
            "tuned_model",
            input_example=X_test.iloc[:1],
            registered_model_name=model_cfg["name"],
        )  # モデルをログに記録して登録
        model_name = model_cfg["name"]  # モデル名を取得
        model_uri = f"runs:/{mlflow.active_run().info.run_id}/tuned_model"  # モデルURIを構築

        logger.info("Registering model to MLflow Model Registry...")  # モデル登録開始のログ
        client = MlflowClient()  # MLflowクライアントを作成
        try:
            client.create_registered_model(model_name)  # 登録モデルを作成
        except Exception as e:  # 例外が発生した場合
            if "already exists" in str(e):  # 既に存在する場合
                logger.info(
                    f"Model {model_name} already exists, skipping creation"
                )  # 既存モデルのログ
            else:  # その他の例外の場合
                raise e  # 例外を再発生

        model_version = client.create_model_version(
            name=model_name, source=model_uri, run_id=mlflow.active_run().info.run_id
        )  # モデルバージョンを作成

        # Transition model to "Staging"
        client.transition_model_version_stage(
            name=model_name, version=model_version.version, stage="Staging"
        )  # モデルをステージング段階に移行

        # Add a human-readable description
        description = (
            f"Model for predicting house prices.\n"
            f"Algorithm: {model_cfg['best_model']}\n"
            f"Hyperparameters: {model_cfg['parameters']}\n"
            f"Features used: All features in the dataset except the target variable\n"
            f"Target variable: {target}\n"
            f"Trained on dataset: {args.data}\n"
            f"Model saved at: {args.models_dir}/trained/{model_name}.pkl\n"
            f"Performance metrics:\n"
            f"  - MAE: {mae:.2f}\n"
            f"  - R²: {r2:.4f}"
        )  # モデルの説明文を作成
        client.update_registered_model(
            name=model_name, description=description
        )  # 登録モデルの説明を更新

        # Add tags for better organization
        client.set_registered_model_tag(
            model_name, "algorithm", model_cfg["best_model"]
        )  # アルゴリズムタグを設定
        client.set_registered_model_tag(
            model_name, "hyperparameters", str(model_cfg["parameters"])
        )  # ハイパーパラメータタグを設定
        client.set_registered_model_tag(
            model_name, "features", "All features except target variable"
        )  # 特徴量タグを設定
        client.set_registered_model_tag(
            model_name, "target_variable", target
        )  # ターゲット変数タグを設定
        client.set_registered_model_tag(
            model_name, "training_dataset", args.data
        )  # 訓練データセットタグを設定
        client.set_registered_model_tag(
            model_name, "model_path", f"{args.models_dir}/trained/{model_name}.pkl"
        )  # モデルパスタグを設定

        # Add dependency tags
        deps = {
            "python_version": platform.python_version(),  # Pythonバージョン
            "scikit_learn_version": sklearn.__version__,  # scikit-learnバージョン
            "xgboost_version": xgb.__version__,  # XGBoostバージョン
            "pandas_version": pd.__version__,  # pandasバージョン
            "numpy_version": np.__version__,  # numpyバージョン
        }  # 依存関係のバージョン情報
        for k, v in deps.items():  # 各依存関係について
            client.set_registered_model_tag(model_name, k, v)  # タグを設定

        # Save model locally
        save_path = f"{args.models_dir}/trained/{model_name}.pkl"  # 保存パスを構築
        joblib.dump(model, save_path)  # モデルをローカルに保存
        logger.info(f"Saved trained model to: {save_path}")  # モデル保存完了のログ
        logger.info(f"Final MAE: {mae:.2f}, R²: {r2:.4f}")  # 最終評価指標のログ


if __name__ == "__main__":
    args = parse_args()  # コマンドライン引数を解析
    main(args)  # メイン処理を実行
