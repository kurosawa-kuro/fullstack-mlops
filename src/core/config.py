"""
設定管理モジュール
環境変数とYAML設定ファイルを統合して管理
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml
from pydantic import BaseSettings, Field


class DatabaseConfig(BaseSettings):
    """データベース設定"""
    type: str = "duckdb"
    path: str = "data/house_price_dwh.duckdb"
    read_only: bool = False
    memory_limit: str = "4GB"

    class Config:
        env_prefix = "DB_"


class MLflowConfig(BaseSettings):
    """MLflow設定"""
    tracking_uri: str = "http://localhost:5555"
    experiment_name: str = "house_price_prediction"
    model_registry_uri: str = "sqlite:///mlflow.db"
    artifact_store: str = "mlruns"

    class Config:
        env_prefix = "MLFLOW_"


class APIConfig(BaseSettings):
    """API設定"""
    title: str = "House Price Prediction API"
    description: str = "MLOps pipeline for house price prediction"
    version: str = "1.0.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    timeout: int = 30

    class Config:
        env_prefix = "API_"


class UIConfig(BaseSettings):
    """UI設定"""
    title: str = "House Price Predictor"
    theme: str = "light"
    page_title: str = "House Price Predictor"
    page_icon: str = "🏠"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"

    class Config:
        env_prefix = "UI_"


class MonitoringConfig(BaseSettings):
    """監視設定"""
    metrics_enabled: bool = True
    metrics_interval: int = 60
    metrics_endpoint: str = "/metrics"
    health_check_enabled: bool = True
    health_check_endpoint: str = "/health"
    health_check_timeout: int = 5
    alerts_enabled: bool = True
    alerts_email: str = "admin@example.com"
    alerts_slack_webhook: str = ""

    class Config:
        env_prefix = "MONITORING_"


class SecurityConfig(BaseSettings):
    """セキュリティ設定"""
    cors_enabled: bool = True
    cors_origins: list = ["*"]
    cors_methods: list = ["GET", "POST", "PUT", "DELETE"]
    cors_headers: list = ["*"]
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 100
    auth_enabled: bool = False
    auth_type: str = "jwt"
    auth_secret_key: str = "your-secret-key"

    class Config:
        env_prefix = "SECURITY_"


class CacheConfig(BaseSettings):
    """キャッシュ設定"""
    enabled: bool = True
    type: str = "redis"
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    ttl: int = 3600

    class Config:
        env_prefix = "CACHE_"


class AppConfig(BaseSettings):
    """アプリケーション設定"""
    name: str = "House Price Predictor"
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: str = "logs/app.log"
    log_max_size: str = "100MB"
    log_backup_count: int = 5

    # サブ設定
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    mlflow: MLflowConfig = Field(default_factory=MLflowConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)

    class Config:
        env_prefix = "APP_"
        env_file = ".env"
        env_file_encoding = "utf-8"


class ConfigManager:
    """設定管理クラス"""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self.config_path = Path(config_path) if config_path else Path("configs/app.yaml")
        self._config: Optional[Dict[str, Any]] = None
        self._app_config: Optional[AppConfig] = None

    def load_config(self) -> Dict[str, Any]:
        """YAML設定ファイルを読み込み"""
        if self._config is None:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f)
            else:
                self._config = {}
        return self._config

    def get_app_config(self) -> AppConfig:
        """アプリケーション設定を取得"""
        if self._app_config is None:
            # 環境変数から設定を読み込み
            self._app_config = AppConfig()
            
            # YAML設定ファイルの内容を環境変数として設定
            yaml_config = self.load_config()
            for key, value in self._flatten_dict(yaml_config):
                env_key = f"APP_{key.upper()}"
                if env_key not in os.environ:
                    os.environ[env_key] = str(value)
            
            # 再読み込み
            self._app_config = AppConfig()
        
        return self._app_config

    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '') -> list:
        """辞書をフラット化"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}_{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key))
            else:
                items.append((new_key, v))
        return items

    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得"""
        config = self.load_config()
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

    def set(self, key: str, value: Any) -> None:
        """設定値を設定"""
        if self._config is None:
            self.load_config()
        
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

    def save(self) -> None:
        """設定をファイルに保存"""
        if self._config is not None:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)

    def reload(self) -> None:
        """設定を再読み込み"""
        self._config = None
        self._app_config = None
        self.load_config()


# グローバル設定インスタンス
config_manager = ConfigManager()


def get_config() -> AppConfig:
    """設定を取得する便利関数"""
    return config_manager.get_app_config()


def get_setting(key: str, default: Any = None) -> Any:
    """設定値を取得する便利関数"""
    return config_manager.get(key, default) 