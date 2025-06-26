import argparse
import logging
import os
import platform

import duckdb
import joblib
import numpy as np
import pandas as pd
import sklearn
import xgboost as xgb
import yaml
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (GradientBoostingRegressor, RandomForestRegressor,
                              StackingRegressor, VotingRegressor)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train ensemble model from config using DuckDB data."
    )
    parser.add_argument(
        "--config", type=str, required=True, help="Path to ensemble_config.yaml"
    )
    parser.add_argument(
        "--duckdb-path", type=str, required=True, help="Path to DuckDB database file"
    )
    parser.add_argument(
        "--models-dir", type=str, required=True, help="Directory to save trained model"
    )
    parser.add_argument(
        "--mlflow-tracking-uri", type=str, default=None, help="MLflow tracking URI"
    )
    parser.add_argument(
        "--view-name",
        type=str,
        default="v_house_analytics",
        help="DuckDB view name to use for training data",
    )
    return parser.parse_args()


def load_data_from_duckdb(duckdb_path, view_name):
    """DuckDBからデータを読み込み、機械学習用に前処理する"""
    logger.info(f"Loading data from DuckDB: {duckdb_path}, view: {view_name}")

    conn = duckdb.connect(duckdb_path)

    try:
        query = f"SELECT * FROM {view_name}"
        data = conn.execute(query).fetchdf()

        logger.info(f"Loaded {len(data)} records from {view_name}")
        logger.info(f"Columns: {list(data.columns)}")

        return data

    finally:
        conn.close()


def clean_data(df, target_variable="price"):
    """非DuckDB版と同じクリーニング処理を適用"""
    logger.info("Cleaning dataset (same as non-DuckDB version)")

    df_cleaned = df.copy()

    # Handle missing values
    for column in df_cleaned.columns:
        missing_count = df_cleaned[column].isnull().sum()
        if missing_count > 0:
            logger.info(f"Found {missing_count} missing values in {column}")

            if pd.api.types.is_numeric_dtype(df_cleaned[column]):
                median_value = df_cleaned[column].median()
                df_cleaned[column] = df_cleaned[column].fillna(median_value)
                logger.info(
                    f"Filled missing values in {column} with median: {median_value}"
                )
            else:
                mode_value = df_cleaned[column].mode()[0]
                df_cleaned[column] = df_cleaned[column].fillna(mode_value)
                logger.info(
                    f"Filled missing values in {column} with mode: {mode_value}"
                )

    # Handle outliers in price (target variable)
    Q1 = df_cleaned[target_variable].quantile(0.25)
    Q3 = df_cleaned[target_variable].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

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
    """engineer.py/preprocessor.pklと同じ特徴量のみを使う"""
    logger.info("Preprocessing data for machine learning (engineer.py互換)")

    X = pd.DataFrame()
    X["sqft"] = data["sqft"]
    X["bedrooms"] = data["bedrooms"]
    X["bathrooms"] = data["bathrooms"]
    X["house_age"] = data["house_age"]
    X["price_per_sqft"] = data["price"] / data["sqft"]
    X["bed_bath_ratio"] = data["bedrooms"] / data["bathrooms"]
    X["bed_bath_ratio"] = (
        X["bed_bath_ratio"].replace([np.inf, -np.inf], np.nan).fillna(0)
    )
    X["location"] = data["location_name"]
    X["condition"] = data["condition_name"]

    y = data[target_variable]
    preprocessor = create_preprocessor()
    X_transformed = preprocessor.fit_transform(X)

    logger.info(f"Final feature matrix shape: {X_transformed.shape}")
    return X_transformed, y, preprocessor


def get_base_model_instance(name, params):
    """ベースモデルのインスタンスを作成"""
    model_map = {
        "RandomForest": RandomForestRegressor,
        "XGBoost": xgb.XGBRegressor,
        "GradientBoosting": GradientBoostingRegressor,
    }

    if name not in model_map:
        raise ValueError(f"Unsupported model: {name}")

    # weightパラメータを除外（VotingRegressorで使用）
    model_params = {k: v for k, v in params.items() if k != "weight"}
    return model_map[name](**model_params)


def create_voting_ensemble(base_models_config):
    """Voting Ensembleを作成"""
    logger.info("Creating Voting Ensemble")

    estimators = []
    for model_name, config in base_models_config.items():
        model = get_base_model_instance(model_name, config)
        weight = config.get("weight", 1.0)
        estimators.append((model_name.lower(), model))
        logger.info(f"Added {model_name} with weight {weight}")

    # 重みを抽出
    weights = [config.get("weight", 1.0) for config in base_models_config.values()]

    ensemble = VotingRegressor(estimators=estimators, weights=weights, n_jobs=-1)

    return ensemble


def create_stacking_ensemble(base_models_config, stacking_config):
    """Stacking Ensembleを作成"""
    logger.info("Creating Stacking Ensemble")

    estimators = []
    for model_name, config in base_models_config.items():
        model = get_base_model_instance(model_name, config)
        estimators.append((model_name.lower(), model))
        logger.info(f"Added {model_name} as base model")

    # メタモデルを作成
    meta_model_map = {
        "LinearRegression": LinearRegression,
        "RandomForest": RandomForestRegressor,
    }

    meta_model_name = stacking_config.get("meta_model", "LinearRegression")
    meta_model = meta_model_map[meta_model_name]()

    ensemble = StackingRegressor(
        estimators=estimators,
        final_estimator=meta_model,
        cv=stacking_config.get("cv_folds", 5),
        n_jobs=-1,
    )

    return ensemble


def evaluate_model(model, X_test, y_test, model_name="Ensemble"):
    """モデルの評価を行う"""
    logger.info(f"Evaluating {model_name}")

    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    logger.info(f"{model_name} Performance:")
    logger.info(f"  MAE: {mae:.2f}")
    logger.info(f"  R²: {r2:.4f}")
    logger.info(f"  RMSE: {rmse:.2f}")

    return {"mae": mae, "r2": r2, "rmse": rmse, "predictions": y_pred}


def main(args):
    # Load config
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    ensemble_cfg = config["ensemble"]
    base_models_cfg = config["base_models"]
    training_cfg = config["training"]

    if args.mlflow_tracking_uri:
        mlflow.set_tracking_uri(args.mlflow_tracking_uri)
        mlflow.set_experiment(ensemble_cfg["name"])

    # Load and preprocess data
    data = load_data_from_duckdb(args.duckdb_path, args.view_name)
    target = ensemble_cfg["target_variable"]

    cleaned_data = clean_data(data)
    X, y, preprocessor = preprocess_data(cleaned_data, target)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=training_cfg["test_size"],
        random_state=training_cfg["random_state"],
    )

    # Create ensemble
    method = ensemble_cfg["method"]

    if method == "voting":
        ensemble = create_voting_ensemble(base_models_cfg)
    elif method == "stacking":
        stacking_cfg = config.get("stacking", {})
        ensemble = create_stacking_ensemble(base_models_cfg, stacking_cfg)
    else:
        raise ValueError(f"Unsupported ensemble method: {method}")

    # Start MLflow run
    with mlflow.start_run(run_name=f"ensemble_{method}_training"):
        logger.info(
            f"Training {method} ensemble with {len(base_models_cfg)} base models"
        )

        # Train ensemble
        ensemble.fit(X_train, y_train)

        # Evaluate ensemble
        ensemble_results = evaluate_model(
            ensemble, X_test, y_test, f"{method.title()} Ensemble"
        )

        # Evaluate individual base models for comparison
        base_model_results = {}
        for model_name, config in base_models_cfg.items():
            base_model = get_base_model_instance(model_name, config)
            base_model.fit(X_train, y_train)
            base_model_results[model_name] = evaluate_model(
                base_model, X_test, y_test, model_name
            )

        # Log metrics
        mlflow.log_metrics(
            {
                "ensemble_mae": ensemble_results["mae"],
                "ensemble_r2": ensemble_results["r2"],
                "ensemble_rmse": ensemble_results["rmse"],
            }
        )

        # Log base model metrics
        for model_name, results in base_model_results.items():
            mlflow.log_metrics(
                {
                    f"{model_name.lower()}_mae": results["mae"],
                    f"{model_name.lower()}_r2": results["r2"],
                    f"{model_name.lower()}_rmse": results["rmse"],
                }
            )

        # Log parameters
        mlflow.log_params(
            {
                "ensemble_method": method,
                "base_models": list(base_models_cfg.keys()),
                "test_size": training_cfg["test_size"],
            }
        )

        # Register model
        model_name = ensemble_cfg["name"]
        mlflow.sklearn.log_model(
            ensemble,
            "ensemble_model",
            input_example=X_test[:1],
            registered_model_name=model_name,
        )

        # Register to MLflow Model Registry
        logger.info("Registering ensemble model to MLflow Model Registry...")
        client = MlflowClient()

        try:
            client.create_registered_model(model_name)
        except Exception as e:
            if "already exists" not in str(e):
                raise e

        model_uri = f"runs:/{mlflow.active_run().info.run_id}/ensemble_model"
        model_version = client.create_model_version(
            name=model_name, source=model_uri, run_id=mlflow.active_run().info.run_id
        )

        # Transition to Staging
        client.transition_model_version_stage(
            name=model_name, version=model_version.version, stage="Staging"
        )

        # Add description
        description = (
            f"Ensemble model for predicting house prices using DuckDB data.\n"
            f"Method: {method.title()}\n"
            f"Base models: {list(base_models_cfg.keys())}\n"
            f"Target variable: {target}\n"
            f"Data source: DuckDB view '{args.view_name}'\n"
            f"Performance metrics:\n"
            f"  - MAE: {ensemble_results['mae']:.2f}\n"
            f"  - R²: {ensemble_results['r2']:.4f}\n"
            f"  - RMSE: {ensemble_results['rmse']:.2f}"
        )

        client.update_registered_model(name=model_name, description=description)

        # Save model locally
        os.makedirs(f"{args.models_dir}/trained", exist_ok=True)

        model_save_path = f"{args.models_dir}/trained/{model_name}.pkl"
        joblib.dump(ensemble, model_save_path)

        preprocessor_save_path = (
            f"{args.models_dir}/trained/{model_name}_preprocessor.pkl"
        )
        joblib.dump(preprocessor, preprocessor_save_path)

        logger.info(f"Saved ensemble model to: {model_save_path}")
        logger.info(f"Saved preprocessor to: {preprocessor_save_path}")

        # Print comparison summary
        logger.info("\n" + "=" * 50)
        logger.info("ENSEMBLE PERFORMANCE COMPARISON")
        logger.info("=" * 50)

        logger.info(f"\n{method.title()} Ensemble:")
        logger.info(f"  MAE: {ensemble_results['mae']:.2f}")
        logger.info(f"  R²: {ensemble_results['r2']:.4f}")
        logger.info(f"  RMSE: {ensemble_results['rmse']:.2f}")

        logger.info(f"\nBase Models:")
        for model_name, results in base_model_results.items():
            logger.info(f"  {model_name}:")
            logger.info(f"    MAE: {results['mae']:.2f}")
            logger.info(f"    R²: {results['r2']:.4f}")
            logger.info(f"    RMSE: {results['rmse']:.2f}")

        # Check if ensemble improves performance
        best_base_mae = min(results["mae"] for results in base_model_results.values())
        best_base_r2 = max(results["r2"] for results in base_model_results.values())

        mae_improvement = (
            (best_base_mae - ensemble_results["mae"]) / best_base_mae
        ) * 100
        r2_improvement = ((ensemble_results["r2"] - best_base_r2) / best_base_r2) * 100

        logger.info(f"\nImprovement over best base model:")
        logger.info(f"  MAE improvement: {mae_improvement:.2f}%")
        logger.info(f"  R² improvement: {r2_improvement:.2f}%")


if __name__ == "__main__":
    args = parse_args()
    main(args)
