#!/usr/bin/env python3
"""
MLモデルパイプライン実行スクリプト
データ処理 → 特徴量エンジニアリング → モデル訓練 の全工程を自動実行
"""

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

# ログ設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ml-pipeline")


def run_command(command, description):
    """コマンドを実行し、エラー時は例外を発生させる"""
    logger.info(f"実行中: {description}")
    logger.info(f"コマンド: {command}")

    try:
        # 仮想環境内のPythonを使用
        if command.startswith("python "):
            command = command.replace("python ", ".venv/bin/python ")

        # コマンドをリストに分割してshell=Trueを避ける
        if isinstance(command, str):
            command = command.split()

        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} 完了")
        if result.stdout:
            logger.debug(f"出力: {result.stdout}")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} 失敗")
        logger.error(f"エラー出力: {e.stderr}")
        raise


def check_file_exists(file_path, description):
    """ファイルの存在確認"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{description}が見つかりません: {file_path}")
    logger.info(f"✅ {description} 確認済み: {file_path}")


def main():
    parser = argparse.ArgumentParser(description="MLモデルパイプライン実行")
    parser.add_argument("--data-dir", default="data", help="データディレクトリ")
    parser.add_argument("--models-dir", default="models", help="モデル保存ディレクトリ")
    parser.add_argument("--config", default="configs/model_config.yaml", help="設定ファイル")
    parser.add_argument(
        "--skip-data-processing", action="store_true", help="データ処理をスキップ"
    )
    parser.add_argument(
        "--skip-feature-engineering", action="store_true", help="特徴量エンジニアリングをスキップ"
    )

    args = parser.parse_args()

    logger.info("🚀 MLモデルパイプライン開始")

    try:
        # 1. 必要なファイルの存在確認
        logger.info("📋 ファイル存在確認")
        check_file_exists(args.config, "設定ファイル")

        raw_data_path = f"{args.data_dir}/raw/house_data.csv"
        if not args.skip_data_processing:
            check_file_exists(raw_data_path, "生データファイル")

        # 2. データ処理
        if not args.skip_data_processing:
            logger.info("🔄 データ処理開始")
            processed_data_path = f"{args.data_dir}/processed/cleaned_house_data.csv"

            run_command(
                f"python src/ml/data/run_processing.py --input {raw_data_path} --output {processed_data_path}",
                "データ処理",
            )
        else:
            logger.info("⏭️ データ処理をスキップ")

        # 3. 特徴量エンジニアリング
        if not args.skip_feature_engineering:
            logger.info("🔧 特徴量エンジニアリング開始")
            processed_data_path = f"{args.data_dir}/processed/cleaned_house_data.csv"
            featured_data_path = f"{args.data_dir}/processed/featured_house_data.csv"
            preprocessor_path = f"{args.models_dir}/trained/preprocessor.pkl"

            # 出力ディレクトリの作成
            os.makedirs(os.path.dirname(featured_data_path), exist_ok=True)
            os.makedirs(os.path.dirname(preprocessor_path), exist_ok=True)

            run_command(
                f"python src/ml/features/engineer.py --input {processed_data_path} --output {featured_data_path} --preprocessor {preprocessor_path}",
                "特徴量エンジニアリング",
            )
        else:
            logger.info("⏭️ 特徴量エンジニアリングをスキップ")

        # 4. モデル訓練
        logger.info("🎯 モデル訓練開始")
        featured_data_path = f"{args.data_dir}/processed/featured_house_data.csv"

        run_command(
            f"python src/ml/models/train_model.py --config {args.config} --data {featured_data_path} --models-dir {args.models_dir}",
            "モデル訓練",
        )

        # 5. 最終確認
        logger.info("✅ 最終確認")
        model_path = f"{args.models_dir}/trained/house_price_prediction.pkl"
        preprocessor_path = f"{args.models_dir}/trained/preprocessor.pkl"

        check_file_exists(model_path, "学習済みモデル")
        check_file_exists(preprocessor_path, "前処理器")

        # ファイルサイズ確認
        model_size = os.path.getsize(model_path) / (1024 * 1024)  # MB
        preprocessor_size = os.path.getsize(preprocessor_path) / 1024  # KB

        logger.info(f"📊 モデルファイルサイズ: {model_size:.2f} MB")
        logger.info(f"📊 前処理器ファイルサイズ: {preprocessor_size:.2f} KB")

        logger.info("🎉 MLモデルパイプライン完了！")

    except Exception as e:
        logger.error(f"❌ パイプライン実行中にエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
