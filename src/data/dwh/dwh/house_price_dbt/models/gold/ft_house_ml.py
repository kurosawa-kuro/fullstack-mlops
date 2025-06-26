import os
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.preprocessing import LabelEncoder, StandardScaler


def model(dbt, session):
    """
    Gold layer: ML-ready features for house price prediction
    This model performs feature engineering and preprocessing for ML models
    """

    # Get silver data - dbtのPythonモデルではdf()メソッドを使用
    silver_df = dbt.ref("silver_house_data")

    # Convert to pandas DataFrame
    df = silver_df.df()

    # Filter complete records only
    df = df[df["is_complete_record"] == True].copy()

    # Remove outliers
    df = df[df["is_price_outlier"] == False].copy()
    df = df[df["is_age_outlier"] == False].copy()

    print(f"Processing {len(df)} records for ML features")

    # Feature engineering
    df = _engineer_features(df)

    # Feature encoding
    df = _encode_features(df)

    # Feature scaling
    df = _scale_features(df)

    # Feature selection
    df = _select_features(df)

    # Save preprocessing artifacts
    _save_preprocessing_artifacts(df)

    return df


def _engineer_features(df):
    """Engineer new features"""

    # Log transformations for skewed features
    df["log_price"] = np.log1p(df["price"])
    df["log_sqft"] = np.log1p(df["sqft"])

    # Polynomial features
    df["sqft_squared"] = df["sqft"] ** 2
    df["price_per_sqft_squared"] = df["price_per_sqft"] ** 2

    # Interaction features
    df["price_bedrooms_interaction"] = df["price"] * df["bedrooms"]
    df["price_bathrooms_interaction"] = df["price"] * df["bathrooms"]
    df["sqft_bedrooms_interaction"] = df["sqft"] * df["bedrooms"]

    # Categorical features
    df["is_old_house"] = (df["house_age"] > 50).astype(int)
    df["is_new_house"] = (df["house_age"] < 10).astype(int)
    df["is_large_house"] = (df["sqft"] > df["sqft"].quantile(0.75)).astype(int)
    df["is_expensive"] = (df["price"] > df["price"].quantile(0.75)).astype(int)

    # Location-based features
    location_avg_price = df.groupby("location")["price"].mean()
    df["location_avg_price"] = df["location"].map(location_avg_price)
    df["price_vs_location_avg"] = df["price"] / df["location_avg_price"]

    # Condition-based features
    condition_mapping = {"POOR": 1, "FAIR": 2, "GOOD": 3, "EXCELLENT": 4}
    df["condition_score"] = df["condition"].map(condition_mapping)

    return df


def _encode_features(df):
    """Encode categorical features"""

    # Label encoding for location
    le_location = LabelEncoder()
    df["location_encoded"] = le_location.fit_transform(df["location"])

    # Save label encoder
    artifacts_dir = Path("target/preprocessing_artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    with open(artifacts_dir / "location_encoder.pkl", "wb") as f:
        pickle.dump(le_location, f)

    return df


def _scale_features(df):
    """Scale numerical features"""

    # Features to scale
    scale_features = [
        "price",
        "sqft",
        "bedrooms",
        "bathrooms",
        "year_built",
        "price_per_sqft",
        "house_age",
        "bed_bath_ratio",
        "log_price",
        "log_sqft",
        "sqft_squared",
        "price_per_sqft_squared",
        "price_bedrooms_interaction",
        "price_bathrooms_interaction",
        "sqft_bedrooms_interaction",
        "location_avg_price",
        "price_vs_location_avg",
    ]

    # Filter features that exist in the dataframe
    available_features = [f for f in scale_features if f in df.columns]

    if available_features:
        scaler = StandardScaler()
        df_scaled = scaler.fit_transform(df[available_features])
        df_scaled = pd.DataFrame(
            df_scaled,
            columns=[f"{f}_scaled" for f in available_features],
            index=df.index,
        )

        # Save scaler
        artifacts_dir = Path("target/preprocessing_artifacts")
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        with open(artifacts_dir / "feature_scaler.pkl", "wb") as f:
            pickle.dump(scaler, f)

        # Add scaled features to dataframe
        df = pd.concat([df, df_scaled], axis=1)

    return df


def _select_features(df):
    """Select most important features for ML"""

    # Target variable
    target = "price"

    # Feature columns (exclude target and metadata)
    exclude_cols = [
        "id",
        "created_at",
        "is_complete_record",
        "is_price_outlier",
        "is_age_outlier",
        "location",
        "condition",
    ]

    feature_cols = [col for col in df.columns if col not in exclude_cols + [target]]

    # 必須特徴量
    essential_features = [
        "sqft",
        "bedrooms",
        "bathrooms",
        "year_built",
        "location_encoded",
        "condition_score",
    ]

    # Ensure we have enough features
    if len(feature_cols) > 5:
        # Select top features using correlation with target
        correlations = (
            df[feature_cols + [target]]
            .corr()[target]
            .abs()
            .sort_values(ascending=False)
        )
        top_features = correlations[1:11].index.tolist()  # Exclude target itself

        # Add essential features
        selected_features = list(set(top_features + essential_features))

        # Filter to available features
        selected_features = [f for f in selected_features if f in df.columns]

        # Create final dataframe with selected features and target
        final_cols = selected_features + [target]
        df = df[final_cols].copy()

        print(f"Selected {len(selected_features)} features for ML model")
    else:
        # 特徴量が少ない場合も必須特徴量を含める
        selected_features = [f for f in essential_features if f in df.columns]
        final_cols = selected_features + [target]
        df = df[final_cols].copy()

    return df


def _save_preprocessing_artifacts(df):
    """Save preprocessing artifacts for inference"""

    artifacts_dir = Path("target/preprocessing_artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Save feature names
    feature_names = [col for col in df.columns if col != "price"]
    with open(artifacts_dir / "feature_names.pkl", "wb") as f:
        pickle.dump(feature_names, f)

    # Save data statistics
    stats = {
        "mean": df.mean().to_dict(),
        "std": df.std().to_dict(),
        "min": df.min().to_dict(),
        "max": df.max().to_dict(),
    }

    with open(artifacts_dir / "data_stats.pkl", "wb") as f:
        pickle.dump(stats, f)

    print(f"Preprocessing artifacts saved to {artifacts_dir}")
