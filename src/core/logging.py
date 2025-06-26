"""
ログ設定モジュール
構造化ログとローテーション機能を提供
"""

import json
import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .config import get_config


class JSONFormatter(logging.Formatter):
    """JSON形式のログフォーマッター"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 例外情報がある場合は追加
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # 追加のフィールドがある場合は追加
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)

        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """カラー付きコンソールフォーマッター"""

    COLORS = {
        "DEBUG": "\033[36m",  # シアン
        "INFO": "\033[32m",  # 緑
        "WARNING": "\033[33m",  # 黄
        "ERROR": "\033[31m",  # 赤
        "CRITICAL": "\033[35m",  # マゼンタ
        "RESET": "\033[0m",  # リセット
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        # カラーコードを適用
        record.levelname = f"{color}{record.levelname}{reset}"
        record.name = f"{color}{record.name}{reset}"

        return super().format(record)


class StructuredLogger:
    """構造化ロガークラス"""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self) -> None:
        """ロガーの設定"""
        # ログレベルを設定
        level = self.config.get("level", "INFO")
        self.logger.setLevel(getattr(logging, level.upper()))

        # 既存のハンドラーをクリア
        self.logger.handlers.clear()

        # コンソールハンドラー
        if self.config.get("console", True):
            self._setup_console_handler()

        # ファイルハンドラー
        if self.config.get("file"):
            self._setup_file_handler()

        # プロパゲーションを無効化
        self.logger.propagate = False

    def _setup_console_handler(self) -> None:
        """コンソールハンドラーの設定"""
        console_handler = logging.StreamHandler(sys.stdout)

        if self.config.get("format") == "json":
            formatter = JSONFormatter()
        else:
            formatter = ColoredFormatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _setup_file_handler(self) -> None:
        """ファイルハンドラーの設定"""
        log_file = Path(self.config["file"])
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # ローテーション設定
        max_size = self.config.get("max_size", "100MB")
        backup_count = self.config.get("backup_count", 5)

        # サイズをバイトに変換
        if isinstance(max_size, str):
            size_map = {"KB": 1024, "MB": 1024**2, "GB": 1024**3}
            for unit, multiplier in size_map.items():
                if max_size.upper().endswith(unit):
                    max_size = int(max_size[: -len(unit)]) * multiplier
                    break
            else:
                max_size = int(max_size)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_size, backupCount=backup_count, encoding="utf-8"
        )

        if self.config.get("format") == "json":
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def log(self, level: str, message: str, **kwargs) -> None:
        """構造化ログを出力"""
        extra_fields = kwargs if kwargs else None

        if extra_fields:
            # カスタムレコードを作成
            record = self.logger.makeRecord(
                self.name, getattr(logging, level.upper()), "", 0, message, (), None
            )
            record.extra_fields = extra_fields
            self.logger.handle(record)
        else:
            getattr(self.logger, level.lower())(message)

    def debug(self, message: str, **kwargs) -> None:
        """DEBUGレベルでログ出力"""
        self.log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """INFOレベルでログ出力"""
        self.log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """WARNINGレベルでログ出力"""
        self.log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """ERRORレベルでログ出力"""
        self.log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """CRITICALレベルでログ出力"""
        self.log("CRITICAL", message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """例外情報付きでログ出力"""
        self.log("ERROR", message, exc_info=True, **kwargs)

    @property
    def level(self):
        return self.logger.level

    @property
    def handlers(self):
        return self.logger.handlers


def setup_logging(config: Optional[Dict[str, Any]] = None) -> StructuredLogger:
    """ログ設定を初期化"""
    if config is None:
        app_config = get_config()
        config = {
            "level": app_config.log_level,
            "format": app_config.log_format,
            "file": app_config.log_file,
            "max_size": app_config.log_max_size,
            "backup_count": app_config.log_backup_count,
            "console": True,
        }

    # ルートロガーの設定
    root_logger = StructuredLogger("root", config)

    # アプリケーションロガーの設定
    app_logger = StructuredLogger("app", config)

    return app_logger


def get_logger(name: str) -> StructuredLogger:
    """指定名のStructuredLoggerを取得"""
    return StructuredLogger(name)


# デフォルトロガー
logger = get_logger("fullstack-mlops")


class LogContext:
    """ログコンテキストマネージャー"""

    def __init__(self, logger: StructuredLogger, context: Dict[str, Any]):
        self.logger = logger
        self.context = context
        self.original_extra = getattr(logger.logger, "extra_fields", {})

    def __enter__(self):
        self.logger.logger.extra_fields = {**self.original_extra, **self.context}
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.logger.extra_fields = self.original_extra


def log_context(logger: StructuredLogger, **context) -> LogContext:
    """ログコンテキストを作成"""
    return LogContext(logger, context)


# 使用例
if __name__ == "__main__":
    # ログ設定
    setup_logging()

    # 基本的なログ出力
    logger.info("アプリケーション開始")

    # 構造化ログ出力
    logger.info("ユーザーアクション", user_id=123, action="login", ip="192.168.1.1")

    # コンテキスト付きログ
    with log_context(logger, request_id="req-123", user_id=456):
        logger.info("リクエスト処理開始")
        logger.info("データベース接続完了")
        logger.info("リクエスト処理完了")

    # エラーログ
    try:
        1 / 0
    except Exception as e:
        logger.exception("予期しないエラーが発生", error_type=type(e).__name__)

    logger.info("アプリケーション終了")
