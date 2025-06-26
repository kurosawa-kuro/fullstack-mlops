#!/usr/bin/env python3
"""
設定移行スクリプト
既存の設定を新しい形式に移行
"""

import yaml
import json
from pathlib import Path
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_config():
    """既存の設定を新しい形式に移行"""
    
    logger.info("⚙️ 設定移行を開始します")
    
    # 既存の設定ファイルを読み込み
    old_configs = {
        'base_models': Path('src/configs/base_models.yaml'),
        'ensemble': Path('src/configs/ensemble.yaml'),
        'training': Path('src/configs/training.yaml')
    }
    
    # 新しい設定ファイルを作成
    new_config = {
        'app': {
            'name': 'House Price Predictor',
            'version': '1.0.0',
            'environment': 'development'
        },
        'database': {
            'type': 'duckdb',
            'path': 'models/trained/house_price_dwh.duckdb'
        },
        'mlflow': {
            'tracking_uri': 'http://localhost:5555',
            'experiment_name': 'house_price_prediction'
        },
        'logging': {
            'level': 'INFO',
            'format': 'json',
            'file': 'logs/app.log'
        },
        'models': {},
        'training': {},
        'ensemble': {}
    }
    
    # 既存の設定を新しい構造に統合
    for name, path in old_configs.items():
        if path.exists():
            logger.info(f"📄 {name} 設定を読み込み中...")
            try:
                with open(path, 'r') as f:
                    config_data = yaml.safe_load(f)
                    if config_data:
                        new_config[name] = config_data
                        logger.info(f"✅ {name} 設定移行完了")
            except Exception as e:
                logger.error(f"❌ {name} 設定移行エラー: {e}")
        else:
            logger.warning(f"⚠️ {name} 設定ファイルが見つかりません: {path}")
    
    # 新しい設定ファイルに保存
    try:
        with open('configs/app.yaml', 'w') as f:
            yaml.dump(new_config, f, default_flow_style=False, allow_unicode=True)
        logger.info("✅ 新しい設定ファイル作成完了")
    except Exception as e:
        logger.error(f"❌ 設定ファイル作成エラー: {e}")
    
    # 環境別設定ファイルも作成
    environments = ['development', 'staging', 'production']
    for env in environments:
        env_config = new_config.copy()
        env_config['app']['environment'] = env
        
        # 環境別の設定調整
        if env == 'production':
            env_config['logging']['level'] = 'WARNING'
            env_config['mlflow']['tracking_uri'] = 'http://mlflow:5555'
        
        try:
            with open(f'configs/environments/{env}.yaml', 'w') as f:
                yaml.dump(env_config, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"✅ {env} 環境設定作成完了")
        except Exception as e:
            logger.error(f"❌ {env} 環境設定作成エラー: {e}")

def create_env():
    """環境変数ファイルを作成"""
    
    logger.info("🔧 環境変数ファイルを作成中...")
    
    # 実際の環境変数ファイル（機密情報を含む）
    env_template = """# アプリケーション設定
APP_NAME=House Price Predictor
APP_VERSION=1.0.0
APP_ENVIRONMENT=development

# データベース設定
DB_TYPE=duckdb
DB_PATH=models/trained/house_price_dwh.duckdb

# MLflow設定
MLFLOW_TRACKING_URI=http://localhost:5555
MLFLOW_EXPERIMENT_NAME=house_price_prediction

# ログ設定
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/app.log

# API設定
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# UI設定
UI_HOST=0.0.0.0
UI_PORT=8501

# 監視設定
MONITORING_ENABLED=true
METRICS_PORT=9090

# セキュリティ設定
SECRET_KEY=your-secret-key-here
DEBUG=false
"""
    
    # テンプレートファイル（機密情報を含まない）
    env_example_template = """# アプリケーション設定
APP_NAME=House Price Predictor
APP_VERSION=1.0.0
APP_ENVIRONMENT=development

# データベース設定
DB_TYPE=duckdb
DB_PATH=models/trained/house_price_dwh.duckdb

# MLflow設定
MLFLOW_TRACKING_URI=http://localhost:5555
MLFLOW_EXPERIMENT_NAME=house_price_prediction

# ログ設定
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/app.log

# API設定
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# UI設定
UI_HOST=0.0.0.0
UI_PORT=8501

# 監視設定
MONITORING_ENABLED=true
METRICS_PORT=9090

# セキュリティ設定
SECRET_KEY=your-secret-key-here
DEBUG=false
"""
    
    try:
        # .envファイルを作成
        with open('.env', 'w') as f:
            f.write(env_template)
        logger.info("✅ .envファイル作成完了")
        
        # .env.exampleファイルを作成
        with open('.env.example', 'w') as f:
            f.write(env_example_template)
        logger.info("✅ .env.exampleファイル作成完了")
        
    except Exception as e:
        logger.error(f"❌ 環境変数ファイル作成エラー: {e}")

def create_pyproject_toml():
    """pyproject.tomlを作成"""
    
    logger.info("📦 pyproject.tomlを作成中...")
    
    pyproject_content = """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "house-price-predictor"
version = "1.0.0"
description = "エンドツーエンドMLOps住宅価格予測システム"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.11"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "streamlit>=1.28.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.3.0",
    "xgboost>=2.0.0",
    "lightgbm>=4.0.0",
    "duckdb>=0.9.0",
    "mlflow>=2.8.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "joblib>=1.3.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.5.0",
    "bandit>=1.7.0",
    "pre-commit>=3.4.0",
]

[project.scripts]
house-price-predictor = "src.main:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.black]
line-length = 88
target-version = ['py311']

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
]
"""
    
    try:
        with open('pyproject.toml', 'w') as f:
            f.write(pyproject_content)
        logger.info("✅ pyproject.toml作成完了")
    except Exception as e:
        logger.error(f"❌ pyproject.toml作成エラー: {e}")

if __name__ == "__main__":
    try:
        migrate_config()
        create_env()
        create_pyproject_toml()
        print("🎉 設定移行が正常に完了しました！")
    except Exception as e:
        logger.error(f"❌ 設定移行中にエラーが発生しました: {e}")
        exit(1) 