"""
カスタム例外クラス
アプリケーション固有の例外を定義
"""

from typing import Any, Dict, Optional


class BaseException(Exception):
    """基本例外クラス"""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """例外を辞書形式に変換"""
        return {"error": self.code, "message": self.message, "details": self.details}


class ConfigurationError(BaseException):
    """設定エラー"""

    pass


class DatabaseError(BaseException):
    """データベースエラー"""

    pass


class DataValidationError(BaseException):
    """データ検証エラー"""

    pass


class ModelError(BaseException):
    """モデルエラー"""

    pass


class TrainingError(ModelError):
    """訓練エラー"""

    pass


class PredictionError(ModelError):
    """予測エラー"""

    pass


class FeatureEngineeringError(BaseException):
    """特徴量エンジニアリングエラー"""

    pass


class MLflowError(BaseException):
    """MLflowエラー"""

    pass


class APIError(BaseException):
    """APIエラー"""

    pass


class ValidationError(APIError):
    """バリデーションエラー"""

    pass


class AuthenticationError(APIError):
    """認証エラー"""

    pass


class AuthorizationError(APIError):
    """認可エラー"""

    pass


class RateLimitError(APIError):
    """レート制限エラー"""

    pass


class ServiceUnavailableError(APIError):
    """サービス利用不可エラー"""

    pass


class MonitoringError(BaseException):
    """監視エラー"""

    pass


class CacheError(BaseException):
    """キャッシュエラー"""

    pass


# 具体的な例外クラス
class ModelNotFoundError(ModelError):
    """モデルが見つからないエラー"""

    pass


class ModelVersionNotFoundError(ModelError):
    """モデルバージョンが見つからないエラー"""

    pass


class InvalidModelFormatError(ModelError):
    """無効なモデル形式エラー"""

    pass


class DataSourceNotFoundError(DatabaseError):
    """データソースが見つからないエラー"""

    pass


class DataConnectionError(DatabaseError):
    """データ接続エラー"""

    pass


class DataQueryError(DatabaseError):
    """データクエリエラー"""

    pass


class InvalidFeatureError(FeatureEngineeringError):
    """無効な特徴量エラー"""

    pass


class FeatureNotFoundError(FeatureEngineeringError):
    """特徴量が見つからないエラー"""

    pass


class InvalidInputDataError(DataValidationError):
    """無効な入力データエラー"""

    pass


class MissingRequiredFieldError(DataValidationError):
    """必須フィールド不足エラー"""

    pass


class InvalidFieldTypeError(DataValidationError):
    """無効なフィールド型エラー"""

    pass


class InvalidFieldValueError(DataValidationError):
    """無効なフィールド値エラー"""

    pass


class MLflowConnectionError(MLflowError):
    """MLflow接続エラー"""

    pass


class MLflowExperimentNotFoundError(MLflowError):
    """MLflow実験が見つからないエラー"""

    pass


class MLflowModelNotFoundError(MLflowError):
    """MLflowモデルが見つからないエラー"""

    pass


class MLflowTrackingError(MLflowError):
    """MLflow追跡エラー"""

    pass


class InvalidRequestError(ValidationError):
    """無効なリクエストエラー"""

    pass


class MissingAuthenticationError(AuthenticationError):
    """認証情報不足エラー"""

    pass


class InvalidTokenError(AuthenticationError):
    """無効なトークンエラー"""

    pass


class InsufficientPermissionsError(AuthorizationError):
    """権限不足エラー"""

    pass


class RateLimitExceededError(RateLimitError):
    """レート制限超過エラー"""

    pass


class ServiceMaintenanceError(ServiceUnavailableError):
    """サービスメンテナンスエラー"""

    pass


class MonitoringConnectionError(MonitoringError):
    """監視接続エラー"""

    pass


class MetricsCollectionError(MonitoringError):
    """メトリクス収集エラー"""

    pass


class CacheConnectionError(CacheError):
    """キャッシュ接続エラー"""

    pass


class CacheKeyNotFoundError(CacheError):
    """キャッシュキーが見つからないエラー"""

    pass


# 例外ハンドラー
class ExceptionHandler:
    """例外ハンドラー"""

    @staticmethod
    def handle_exception(
        exception: Exception, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """例外を処理して辞書形式で返す"""
        if isinstance(exception, BaseException):
            return exception.to_dict()
        else:
            return {
                "error": "InternalServerError",
                "message": str(exception),
                "details": context or {},
            }

    @staticmethod
    def get_http_status_code(exception: Exception) -> int:
        """例外に対応するHTTPステータスコードを取得"""
        if isinstance(exception, ValidationError):
            return 400
        elif isinstance(exception, AuthenticationError):
            return 401
        elif isinstance(exception, AuthorizationError):
            return 403
        elif isinstance(exception, RateLimitError):
            return 429
        elif isinstance(exception, ServiceUnavailableError):
            return 503
        elif isinstance(exception, (ModelNotFoundError, DataSourceNotFoundError)):
            return 404
        else:
            return 500


# 例外コンテキストマネージャー
class ExceptionContext:
    """例外コンテキストマネージャー"""

    def __init__(self, logger, context: Optional[Dict[str, Any]] = None):
        self.logger = logger
        self.context = context or {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # 例外をログに記録
            self.logger.exception(
                "例外が発生しました",
                exception_type=exc_type.__name__,
                exception_message=str(exc_val),
                **self.context,
            )

            # カスタム例外でない場合は、適切なカスタム例外に変換
            if not isinstance(exc_val, BaseException):
                if exc_type == ValueError:
                    raise ValidationError(str(exc_val), details=self.context)
                elif exc_type == FileNotFoundError:
                    raise DataSourceNotFoundError(str(exc_val), details=self.context)
                elif exc_type == ConnectionError:
                    raise DataConnectionError(str(exc_val), details=self.context)
                else:
                    # その他の例外はそのまま再発生
                    return False

            return True

        return False


def exception_context(logger, **context):
    """例外コンテキストを作成"""
    return ExceptionContext(logger, context)
