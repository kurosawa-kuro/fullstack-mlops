# src/ml/features/engineer.py
import argparse  # コマンドライン引数を解析するためのモジュール
import logging  # ログ出力機能を提供するモジュール
from datetime import datetime  # 日時操作のためのモジュール

import joblib  # モデルの保存・読み込みライブラリ
import numpy as np  # 数値計算ライブラリ
import pandas as pd  # データ分析ライブラリ
from sklearn.compose import ColumnTransformer  # 列別の変換器を組み合わせるクラス
from sklearn.impute import SimpleImputer  # 欠損値補完のためのクラス
from sklearn.pipeline import Pipeline  # パイプライン構築のためのクラス
from sklearn.preprocessing import OneHotEncoder  # カテゴリ変数のワンホットエンコーディング

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)  # ログの基本設定（レベル、フォーマット）
logger = logging.getLogger("feature-engineering")  # ロガーインスタンスを作成


def create_features(df):
    """Create new features from existing data."""
    logger.info("Creating new features")  # 特徴量作成開始のログ

    # Make a copy to avoid modifying the original dataframe
    df_featured = df.copy()  # 元のデータフレームを変更しないようコピーを作成

    # Calculate house age
    current_year = datetime.now().year  # 現在の年を取得
    df_featured["house_age"] = current_year - df_featured["year_built"]  # 築年数を計算
    logger.info("Created 'house_age' feature")  # 築年数特徴量作成のログ

    # Price per square foot
    df_featured["price_per_sqft"] = df_featured["price"] / df_featured["sqft"]  # 坪単価を計算
    logger.info("Created 'price_per_sqft' feature")  # 坪単価特徴量作成のログ

    # Bedroom to bathroom ratio
    df_featured["bed_bath_ratio"] = df_featured["bedrooms"] / df_featured["bathrooms"]  # 寝室とバスルームの比率を計算
    # Handle division by zero
    df_featured["bed_bath_ratio"] = df_featured["bed_bath_ratio"].replace(
        [np.inf, -np.inf], np.nan
    )  # 無限大の値をNaNに置換
    df_featured["bed_bath_ratio"] = df_featured["bed_bath_ratio"].fillna(0)  # NaNを0で補完
    logger.info("Created 'bed_bath_ratio' feature")  # 寝室バスルーム比率特徴量作成のログ

    # Do NOT one-hot encode categorical variables here; let the preprocessor handle it
    return df_featured  # 特徴量追加済みデータフレームを返す


def create_preprocessor():
    """Create a preprocessing pipeline."""
    logger.info("Creating preprocessor pipeline")  # 前処理パイプライン作成開始のログ

    # Define feature groups
    categorical_features = ["location", "condition"]  # カテゴリ変数のリスト
    numerical_features = [
        "sqft",
        "bedrooms",
        "bathrooms",
        "house_age",
        "price_per_sqft",
        "bed_bath_ratio",
    ]  # 数値変数のリスト

    # Preprocessing for numerical features
    numerical_transformer = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="mean"))]
    )  # 数値変数用の前処理パイプライン（平均値補完）

    # Preprocessing for categorical features
    categorical_transformer = Pipeline(
        steps=[("onehot", OneHotEncoder(handle_unknown="ignore"))]
    )  # カテゴリ変数用の前処理パイプライン（ワンホットエンコーディング）

    # Combine preprocessors in a column transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_transformer, numerical_features),  # 数値変数の変換器
            ("cat", categorical_transformer, categorical_features),  # カテゴリ変数の変換器
        ]
    )  # 列別変換器を組み合わせた前処理器

    return preprocessor  # 前処理器を返す


def run_feature_engineering(input_file, output_file, preprocessor_file):
    """Full feature engineering pipeline."""
    # Load cleaned data
    logger.info(f"Loading data from {input_file}")  # データ読み込み開始のログ
    df = pd.read_csv(input_file)  # CSVファイルを読み込み

    # Create features
    df_featured = create_features(df)  # 特徴量を作成
    logger.info(f"Created featured dataset with shape: {df_featured.shape}")  # 特徴量作成完了のログ

    # Create and fit the preprocessor
    preprocessor = create_preprocessor()  # 前処理器を作成
    X = df_featured.drop(columns=["price"], errors="ignore")  # 特徴量のみを抽出（価格列を除外）
    y = (
        df_featured["price"] if "price" in df_featured.columns else None
    )  # ターゲット変数を抽出（存在する場合）
    X_transformed = preprocessor.fit_transform(X)  # 前処理器を学習して特徴量を変換
    logger.info("Fitted the preprocessor and transformed the features")  # 前処理完了のログ

    # Save the preprocessor
    joblib.dump(preprocessor, preprocessor_file)  # 前処理器をファイルに保存
    logger.info(f"Saved preprocessor to {preprocessor_file}")  # 前処理器保存完了のログ

    # Save fully preprocessed data
    df_transformed = pd.DataFrame(X_transformed)  # 変換された特徴量をDataFrameに変換
    if y is not None:  # ターゲット変数が存在する場合
        df_transformed["price"] = y.values  # ターゲット変数を追加
    df_transformed.to_csv(output_file, index=False)  # 前処理済みデータをCSVとして保存
    logger.info(f"Saved fully preprocessed data to {output_file}")  # 前処理済みデータ保存完了のログ

    return df_transformed  # 前処理済みデータフレームを返す


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Feature engineering for housing data."
    )  # 引数パーサーを作成
    parser.add_argument("--input", required=True, help="Path to cleaned CSV file")  # 入力ファイルパスの引数を定義
    parser.add_argument(
        "--output", required=True, help="Path for output CSV file (engineered features)"
    )  # 出力ファイルパスの引数を定義
    parser.add_argument(
        "--preprocessor", required=True, help="Path for saving the preprocessor"
    )  # 前処理器保存パスの引数を定義

    args = parser.parse_args()  # コマンドライン引数を解析

    run_feature_engineering(args.input, args.output, args.preprocessor)  # 特徴量エンジニアリングを実行
