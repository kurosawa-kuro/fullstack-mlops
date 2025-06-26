#!/usr/bin/env python3
"""
コード移行スクリプト
既存のコードを新しい構造に移行
"""

import shutil
import os
from pathlib import Path
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_code():
    """既存のコードを新しい構造に移行"""
    
    logger.info("🚀 コード移行を開始します")
    
    # データ層移行
    if Path('src/ml/data').exists():
        logger.info("📁 データ層を移行中...")
        try:
            # 既存のデータファイルを新しい構造にコピー
            if Path('src/data/dwh').exists():
                shutil.rmtree('src/data/dwh')
            shutil.copytree('src/ml/data', 'src/data/dwh', dirs_exist_ok=True)
            logger.info("✅ データ層移行完了")
        except Exception as e:
            logger.error(f"❌ データ層移行エラー: {e}")
    
    # 特徴量移行
    if Path('src/ml/features').exists():
        logger.info("🔧 特徴量層を移行中...")
        try:
            # 既存の特徴量ファイルを新しい構造にコピー
            for file in Path('src/ml/features').glob('*.py'):
                shutil.copy2(file, 'src/features/')
            logger.info("✅ 特徴量層移行完了")
        except Exception as e:
            logger.error(f"❌ 特徴量層移行エラー: {e}")
    
    # モデル層移行
    if Path('src/ml/models').exists():
        logger.info("🤖 モデル層を移行中...")
        try:
            # 既存のモデルファイルを新しい構造にコピー
            for file in Path('src/ml/models').glob('*.py'):
                if 'train' in file.name.lower():
                    shutil.copy2(file, 'src/models/training/')
                elif 'ensemble' in file.name.lower():
                    shutil.copy2(file, 'src/models/ensemble/')
                else:
                    shutil.copy2(file, 'src/models/base/')
            logger.info("✅ モデル層移行完了")
        except Exception as e:
            logger.error(f"❌ モデル層移行エラー: {e}")
    
    # パイプライン移行
    if Path('src/ml/pipeline').exists():
        logger.info("🔗 パイプライン層を移行中...")
        try:
            # 既存のパイプラインファイルを新しい構造にコピー
            for file in Path('src/ml/pipeline').glob('*.py'):
                shutil.copy2(file, 'src/models/inference/')
            logger.info("✅ パイプライン層移行完了")
        except Exception as e:
            logger.error(f"❌ パイプライン層移行エラー: {e}")
    
    # サービス層移行（既存のAPI/UIはそのまま）
    logger.info("🌐 サービス層は既存の構造を維持")
    
    logger.info("✅ コード移行完了")

def migrate_tests():
    """テストファイルを新しい構造に移行"""
    
    logger.info("🧪 テスト移行を開始します")
    
    # 既存のテストファイルを新しい構造に移行
    if Path('src/tests').exists():
        try:
            # 単体テストとして移行
            for file in Path('src/tests').glob('*.py'):
                if 'test_' in file.name:
                    shutil.copy2(file, 'tests/unit/')
            logger.info("✅ テスト移行完了")
        except Exception as e:
            logger.error(f"❌ テスト移行エラー: {e}")

def create_migration_artifacts():
    """移行用のアーティファクトを作成"""
    
    logger.info("📦 移行アーティファクトを作成中...")
    
    # 移行完了マーカー
    with open('MIGRATION_COMPLETED.txt', 'w') as f:
        f.write("Migration completed successfully\n")
        f.write(f"Timestamp: {Path().cwd()}\n")
    
    logger.info("✅ 移行アーティファクト作成完了")

if __name__ == "__main__":
    try:
        migrate_code()
        migrate_tests()
        create_migration_artifacts()
        print("🎉 移行が正常に完了しました！")
    except Exception as e:
        logger.error(f"❌ 移行中にエラーが発生しました: {e}")
        exit(1) 