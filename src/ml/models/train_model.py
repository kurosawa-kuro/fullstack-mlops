import argparse  # コマンドライン引数を解析するためのモジュール
import logging  # ログ出力機能を提供するモジュール
import platform  # プラットフォーム情報を取得するモジュール

import duckdb  # DuckDBライブラリ
import joblib  # モデルの保存・読み込みライブラリ
import numpy as np  # 数値計算ライブラリ
import pandas as pd  # データ分析ライブラリ
import sklearn  # scikit-learnライブラリ
import xgboost as xgb  # XGBoostライブラリ
import yaml  # YAMLファイル読み込みライブラリ
from sklearn.compose import ColumnTransformer  # 列別の変換器を組み合わせるクラス
from sklearn.ensemble import GradientBoostingRegressor  # アンサンブル学習アルゴリズム
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer  # 欠損値補完のためのクラス
from sklearn.linear_model import LinearRegression  # 線形回帰アルゴリズム
from sklearn.metrics import mean_absolute_error, r2_score  # 評価指標
from sklearn.model_selection import train_test_split  # データ分割機能
from sklearn.pipeline import Pipeline  # パイプライン構築のためのクラス
from sklearn.preprocessing import LabelEncoder  # ラベルエンコーダー
from sklearn.preprocessing import OneHotEncoder, StandardScaler  # 前処理クラス

import mlflow  # MLflowのメインモジュール
import mlflow.sklearn  # scikit-learnモデル用のMLflowモジュール
from mlflow.tracking import MlflowClient  # MLflowクライアント

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
        description="Train and register final model from config using DuckDB data."
    )  # 引数パーサーを作成
    parser.add_argument(
        "--config", type=str, required=True, help="Path to model_config.yaml"
    )  # 設定ファイルパスの引数を定義
    parser.add_argument(
        "--duckdb-path", type=str, required=True, help="Path to DuckDB database file"
    )  # DuckDBファイルパスの引数を定義
    parser.add_argument(
        "--models-dir", type=str, required=True, help="Directory to save trained model"
    )  # モデル保存ディレクトリの引数を定義
    parser.add_argument(
        "--mlflow-tracking-uri", type=str, default=None, help="MLflow tracking URI"
    )  # MLflow追跡URIの引数を定義
    parser.add_argument(
        "--view-name",
        type=str,
        default="v_house_analytics",
        help="DuckDB view name to use for training data",
    )  # 使用するビュー名の引数を定義
    return parser.parse_args()  # コマンドライン引数を解析して返す


# -----------------------------
# Load data from DuckDB
# -----------------------------
def load_data_from_duckdb(duckdb_path, view_name):
    """
    DuckDBからデータを読み込み、機械学習用に前処理する
    """
    logger.info(f"Loading data from DuckDB: {duckdb_path}, view: {view_name}")

    # DuckDBに接続
    conn = duckdb.connect(duckdb_path)

    try:
        # ビューからデータを取得
        query = f"SELECT * FROM {view_name}"
        data = conn.execute(query).fetchdf()

        logger.info(f"Loaded {len(data)} records from {view_name}")
        logger.info(f"Columns: {list(data.columns)}")

        return data

    finally:
        conn.close()


# -----------------------------
# Clean data (same as non-DuckDB version)
# -----------------------------
def clean_data(df, target_variable="price"):
    """
    非DuckDB版と同じクリーニング処理を適用
    """
    logger.info("Cleaning dataset (same as non-DuckDB version)")

    # Make a copy to avoid modifying the original dataframe
    df_cleaned = df.copy()

    # Handle missing values
    for column in df_cleaned.columns:
        missing_count = df_cleaned[column].isnull().sum()
        if missing_count > 0:
            logger.info(f"Found {missing_count} missing values in {column}")

            # For numeric columns, fill with median
            if pd.api.types.is_numeric_dtype(df_cleaned[column]):
                median_value = df_cleaned[column].median()
                df_cleaned[column] = df_cleaned[column].fillna(median_value)
                logger.info(
                    f"Filled missing values in {column} with median: {median_value}"
                )
            # For categorical columns, fill with mode
            else:
                mode_value = df_cleaned[column].mode()[0]
                df_cleaned[column] = df_cleaned[column].fillna(mode_value)
                logger.info(
                    f"Filled missing values in {column} with mode: {mode_value}"
                )

    # Handle outliers in price (target variable) - same as non-DuckDB version
    Q1 = df_cleaned[target_variable].quantile(0.25)
    Q3 = df_cleaned[target_variable].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Filter out extreme outliers
    outliers = df_cleaned[
        (df_cleaned[target_variable] < lower_bound)
        | (df_cleaned[target_variable] > upper_bound)
    ]

    if not outliers.empty:
        logger.info(f"Found {len(outliers)} outliers in {target_variable} column")
        df_cleaned = df_cleaned[
            (df_cleaned[target_variable] >= lower_bound)
            & (df_cleaned[target_variable] <= upper_bound)
        ]
        logger.info(f"Removed outliers. New dataset shape: {df_cleaned.shape}")

    return df_cleaned


# -----------------------------
# Preprocess data for ML (engineer.py互換)
# -----------------------------
def create_preprocessor():
    """engineer.py/preprocessor.pklと同じ前処理パイプライン"""
    logger.info("Creating preprocessor pipeline (engineer.py互換)")
    categorical_features = ["location", "condition"]
    numerical_features = [
        "sqft",
        "bedrooms",
        "bathrooms",
        "house_age",
        "price_per_sqft",
        "bed_bath_ratio",
    ]
    numerical_transformer = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="mean"))]
    )
    categorical_transformer = Pipeline(
        steps=[("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_transformer, numerical_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )
    return preprocessor


def preprocess_data(data, target_variable):
    """
    Preprocess data for machine learning (DuckDB v_house_analytics view compatible)
    """
    logger.info("Preprocessing data for machine learning (v_house_analytics互換)")
    # 必要なカラムのみ抽出
    X = pd.DataFrame()
    X["sqft"] = data["sqft"]
    X["bedrooms"] = data["bedrooms"]
    X["bathrooms"] = data["bathrooms"]
    
    # year_valueからhouse_ageを計算（DuckDBビューではyear_valueとして提供）
    current_year = 2025
    X["house_age"] = current_year - data["year_value"]
    
    X["price_per_sqft"] = data["price"] / data["sqft"]
    X["bed_bath_ratio"] = data["bedrooms"] / data["bathrooms"]
    X["bed_bath_ratio"] = (
        X["bed_bath_ratio"].replace([np.inf, -np.inf], np.nan).fillna(0)
    )
    
    # DuckDBビューのカラム名を使用
    X["location"] = data["location_name"]
    X["condition"] = data["condition_name"]
    
    y = data[target_variable]
    preprocessor = create_preprocessor()
    X_transformed = preprocessor.fit_transform(X)
    logger.info(f"Final feature matrix shape: {X_transformed.shape}")
    return X_transformed, y, preprocessor


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

    # Load data from DuckDB
    data = load_data_from_duckdb(args.duckdb_path, args.view_name)  # DuckDBからデータを読み込み
    target = model_cfg["target_variable"]  # ターゲット変数名を取得

    # Clean data
    cleaned_data = clean_data(data)

    # Preprocess data
    X, y, preprocessor = preprocess_data(cleaned_data, target)  # データを前処理

    # 特徴量名リストを取得（DuckDBビュー構造に合わせて修正）
    features_used = list(
        cleaned_data.drop(columns=[target])
        .drop(
            columns=["transaction_id", "transaction_date", "price_per_sqft", "location_type", "condition_score", "decade", "century"],
            errors="ignore",
        )
        .columns
    )
    features_used += [
        "log_sqft",
        "house_age_squared",
        "total_rooms",
        "sqft_per_bedroom",
        "house_age_cubed",
        "sqrt_sqft",
        "bedrooms_bathrooms_interaction",
        "age_sqft_interaction",
        "condition_sqft_interaction",
        "price_category",
        "location_price_level",
    ]

    # データを訓練用とテスト用に分割
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
            input_example=X_test[:1],
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
            f"Model for predicting house prices using DuckDB data.\n"
            f"Algorithm: {model_cfg['best_model']}\n"
            f"Hyperparameters: {model_cfg['parameters']}\n"
            f"Features used: {features_used}\n"
            f"Target variable: {target}\n"
            f"Data source: DuckDB view '{args.view_name}'\n"
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
            model_name, "features", str(features_used)
        )  # 特徴量タグを設定
        client.set_registered_model_tag(
            model_name, "target_variable", target
        )  # ターゲット変数タグを設定
        client.set_registered_model_tag(
            model_name, "data_source", f"DuckDB view: {args.view_name}"
        )  # データソースタグを設定
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
            "duckdb_version": duckdb.__version__,  # DuckDBバージョン
        }  # 依存関係のバージョン情報
        for k, v in deps.items():  # 各依存関係について
            client.set_registered_model_tag(model_name, k, v)  # タグを設定

        # Save model and label encoders locally
        import os

        os.makedirs(f"{args.models_dir}/trained", exist_ok=True)  # ディレクトリを作成

        # モデルを保存
        model_save_path = f"{args.models_dir}/trained/{model_name}.pkl"  # 保存パスを構築
        joblib.dump(model, model_save_path)  # モデルをローカルに保存

        # ラベルエンコーダーを保存
        encoders_save_path = f"{args.models_dir}/trained/{model_name}_encoders.pkl"
        joblib.dump(preprocessor, encoders_save_path)

        logger.info(f"Saved trained model to: {model_save_path}")  # モデル保存完了のログ
        logger.info(f"Saved preprocessor to: {encoders_save_path}")  # 前処理器保存完了のログ
        logger.info(f"Final MAE: {mae:.2f}, R²: {r2:.4f}")  # 最終評価指標のログ


if __name__ == "__main__":
    args = parse_args()  # コマンドライン引数を解析
    main(args)  # メイン処理を実行
