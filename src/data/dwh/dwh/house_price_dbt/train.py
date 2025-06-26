import pickle
from pathlib import Path

import duckdb
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# Goldテーブルのパス
GOLD_TABLE = "main_gold.ft_house_ml"
DB_PATH = "src/ml/data/dwh/data/house_price_dwh.duckdb"

# データ読込
con = duckdb.connect(DB_PATH)
df = con.execute(f"SELECT * FROM {GOLD_TABLE}").df()
con.close()

print(f"[INFO] Goldテーブルから{len(df)}件ロード")

# 特徴量・目的変数
X = df.drop("price", axis=1)
y = df["price"]

# 学習・検証分割
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# モデル学習
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 評価
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"[RESULT] モデル精度評価:")
print(f"  - MSE: {mse:,.2f}")
print(f"  - MAE: {mae:,.0f}")
print(f"  - R²: {r2:.4f}")

# モデル保存
artifacts_dir = Path("src/ml/data/dwh/house_price_dbt/artifacts")
artifacts_dir.mkdir(parents=True, exist_ok=True)
with open(artifacts_dir / "rf_model.pkl", "wb") as f:
    pickle.dump(model, f)
print(f"[INFO] モデルを {artifacts_dir}/rf_model.pkl に保存")
