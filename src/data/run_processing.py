# src/data/processor.py
import argparse  # コマンドライン引数を解析するためのモジュール
import logging  # ログ出力機能を提供するモジュール
from pathlib import Path  # ファイルパス操作のためのモジュール

import numpy as np  # 数値計算ライブラリ
import pandas as pd  # データ分析ライブラリ

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)  # ログの基本設定（レベル、フォーマット）
logger = logging.getLogger("data-processor")  # ロガーインスタンスを作成


def load_data(file_path):
    """Load data from a CSV file."""
    logger.info(f"Loading data from {file_path}")  # データ読み込み開始のログ
    return pd.read_csv(file_path)  # CSVファイルを読み込んでDataFrameを返す


def clean_data(df):
    """Clean the dataset by handling missing values and outliers."""
    logger.info("Cleaning dataset")  # データクリーニング開始のログ

    # Make a copy to avoid modifying the original dataframe
    df_cleaned = df.copy()  # 元のデータフレームを変更しないようコピーを作成

    # Handle missing values
    for column in df_cleaned.columns:  # 各列を順次処理
        missing_count = df_cleaned[column].isnull().sum()  # 欠損値の数をカウント
        if missing_count > 0:  # 欠損値が存在する場合
            logger.info(f"Found {missing_count} missing values in {column}")  # 欠損値発見のログ

            # For numeric columns, fill with median
            if pd.api.types.is_numeric_dtype(df_cleaned[column]):  # 数値型の列の場合
                median_value = df_cleaned[column].median()  # 中央値を計算
                df_cleaned[column] = df_cleaned[column].fillna(median_value)  # 欠損値を中央値で補完
                logger.info(
                    f"Filled missing values in {column} with median: {median_value}"
                )  # 中央値補完のログ
            # For categorical columns, fill with mode
            else:  # カテゴリ型の列の場合
                mode_value = df_cleaned[column].mode()[0]  # 最頻値を取得
                df_cleaned[column] = df_cleaned[column].fillna(mode_value)  # 欠損値を最頻値で補完
                logger.info(
                    f"Filled missing values in {column} with mode: {mode_value}"
                )  # 最頻値補完のログ

    # Handle outliers in price (target variable)
    # Using IQR method to identify outliers
    Q1 = df_cleaned["price"].quantile(0.25)  # 第1四分位数を計算
    Q3 = df_cleaned["price"].quantile(0.75)  # 第3四分位数を計算
    IQR = Q3 - Q1  # 四分位範囲を計算
    lower_bound = Q1 - 1.5 * IQR  # 下限値を計算
    upper_bound = Q3 + 1.5 * IQR  # 上限値を計算

    # Filter out extreme outliers
    outliers = df_cleaned[
        (df_cleaned["price"] < lower_bound) | (df_cleaned["price"] > upper_bound)
    ]  # 外れ値を特定

    if not outliers.empty:  # 外れ値が存在する場合
        logger.info(f"Found {len(outliers)} outliers in price column")  # 外れ値発見のログ
        df_cleaned = df_cleaned[
            (df_cleaned["price"] >= lower_bound) & (df_cleaned["price"] <= upper_bound)
        ]  # 外れ値を除外
        logger.info(f"Removed outliers. New dataset shape: {df_cleaned.shape}")  # 外れ値除去後のログ

    return df_cleaned  # クリーニング済みデータフレームを返す


def process_data(input_file, output_file):
    """Full data processing pipeline."""
    # Create output directory if it doesn't exist
    output_path = Path(output_file).parent  # 出力ファイルの親ディレクトリを取得
    output_path.mkdir(parents=True, exist_ok=True)  # 出力ディレクトリを作成（存在しない場合）

    # Load data
    df = load_data(input_file)  # データを読み込み
    logger.info(f"Loaded data with shape: {df.shape}")  # 読み込み完了のログ

    # Clean data
    df_cleaned = clean_data(df)  # データをクリーニング

    # Save processed data
    df_cleaned.to_csv(output_file, index=False)  # 処理済みデータをCSVとして保存
    logger.info(f"Saved processed data to {output_file}")  # 保存完了のログ

    return df_cleaned  # 処理済みデータフレームを返す


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data processing for housing data.")  # 引数パーサーを作成
    parser.add_argument("--input", required=True, help="Path to input CSV file")  # 入力ファイルパスの引数を定義
    parser.add_argument("--output", required=True, help="Path for output CSV file")  # 出力ファイルパスの引数を定義

    args = parser.parse_args()  # コマンドライン引数を解析

    process_data(args.input, args.output)  # データ処理を実行
