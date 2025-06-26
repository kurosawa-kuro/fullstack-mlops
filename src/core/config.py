"""
設定管理モジュール
統一された設定管理を提供
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """アプリケーション設定クラス"""

    # アプリケーション設定
    app_name: str = Field(default="House Price Predictor", description="アプリケーション名")
    app_version: str = Field(default="1.0.0", description="アプリケーションバージョン")
    app_environment: str = Field(default="development", description="実行環境")

    # データベース設定
    db_type: str = Field(default="duckdb", description="データベースタイプ")
    db_path: str = Field(
        default="models/trained/house_price_dwh.duckdb", description="データベースパス"
    )

    # MLflow設定
    mlflow_tracking_uri: str = Field(
        default="http://localhost:5555", description="MLflow追跡URI"
    )
    mlflow_experiment_name: str = Field(
        default="house_price_prediction", description="MLflow実験名"
    )

    # ログ設定
    log_level: str = Field(default="INFO", description="ログレベル")
    log_format: str = Field(default="json", description="ログフォーマット")
    log_file: str = Field(default="logs/app.log", description="ログファイルパス")
    log_max_size: str = Field(default="100MB", description="ログファイル最大サイズ")
    log_backup_count: int = Field(default=5, description="ログバックアップ数")

    # API設定
    api_host: str = Field(default="0.0.0.0", description="APIホスト")
    api_port: int = Field(default=8000, description="APIポート")
    api_workers: int = Field(default=4, description="APIワーカー数")

    # UI設定
    ui_host: str = Field(default="0.0.0.0", description="UIホスト")
    ui_port: int = Field(default=8501, description="UIポート")

    # 監視設定
    monitoring_enabled: bool = Field(default=True, description="監視有効化")
    metrics_port: int = Field(default=9090, description="メトリクスポート")

    # セキュリティ設定
    secret_key: str = Field(default="your-secret-key-here", description="シークレットキー")
    debug: bool = Field(default=False, description="デバッグモード")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @classmethod
    def from_yaml(cls, config_path: str) -> "Config":
        """YAMLファイルから設定を読み込み"""
        if not Path(config_path).exists():
            raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        return cls(**config_data)

    def to_dict(self) -> Dict[str, Any]:
        """設定を辞書形式で取得"""
        return self.model_dump()

    def get_database_url(self) -> str:
        """データベースURLを取得"""
        if self.db_type == "duckdb":
            return f"duckdb://{self.db_path}"
        else:
            raise ValueError(f"サポートされていないデータベースタイプ: {self.db_type}")

    def is_production(self) -> bool:
        """本番環境かどうかを判定"""
        return self.app_environment.lower() == "production"

    def is_development(self) -> bool:
        """開発環境かどうかを判定"""
        return self.app_environment.lower() == "development"

    def get(self, key: str, default: Any = None) -> Any:
        """ドット区切りでネストされた値を取得"""
        keys = key.split('.')
        value = self
        for k in keys:
            value = getattr(value, k, default)
            if value is default:
                break
        return value


# グローバル設定インスタンス
config = Config()


def get_config() -> Config:
    """設定インスタンスを取得"""
    return config


def reload_config(config_path: Optional[str] = None) -> Config:
    """設定を再読み込み"""
    global config
    if config_path:
        config = Config.from_yaml(config_path)
    else:
        config = Config()
    return config
