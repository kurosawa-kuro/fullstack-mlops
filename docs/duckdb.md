以下のようなステップ＆テンプレートで進めると、Raw 不動産データ → DuckDB での前処理・特徴量生成 → scikit-learn での学習、という一連の流れがスムーズに構築できます。

---

## 1. DuckDB に生データを取り込む

```python
import duckdb

# インプロセス DuckDB を起動（メモリ or ファイル）
con = duckdb.connect(database=':memory:')  # or 'real_estate.duckdb'

# CSV ワイルドカードでまとめて読み込み
con.execute("""
CREATE TABLE raw AS
SELECT * 
FROM read_csv_auto('data/real_estate_raw_*.csv');
""")
```

* `read_csv_auto` が自動的に型推論／ヘッダー読み込みを行ってくれます。
* ファイル名に日付やエリアなどバッチ識別子を含めておくと管理しやすいです。

---

## 2. DuckDB 上での前処理＆特徴量生成

```sql
-- 例：日付文字列から日時を抜き出し
ALTER TABLE raw ADD COLUMN 
  listing_date_ts AS TO_TIMESTAMP(listing_date, 'YYYY-MM-DD');

-- 例：面積あたり価格、築年数などの基本特徴
CREATE TABLE features AS
SELECT
  id,
  price,
  area_sqm,
  price / NULLIF(area_sqm, 0)     AS price_per_sqm,
  EXTRACT('year' FROM listing_date_ts) 
    - build_year             AS building_age,
  CASE 
    WHEN build_year < 2000 THEN 'old' 
    ELSE 'new' 
  END                         AS age_group,
  -- 位置情報をバケツ化（例: 市区町村コードからワンホット化前のカテゴリ）
  region_code,
  -- 任意：ウィンドウ関数で近隣中央値など
  MEDIAN(price) 
    OVER (PARTITION BY region_code) 
    AS region_median_price
FROM raw
WHERE price IS NOT NULL 
  AND area_sqm > 0;
```

* **マテリアライズ**：重い `MEDIAN` や集計は一度 `features` テーブルに落としておくと再利用しやすいです。
* **NULLIF** でゼロ除算を防止。
* **CASE／EXTRACT／WINDOW** を駆使して、SQL だけで多彩な特徴を一気に生成できます。

---

## 3. pandas DataFrame に展開して学習準備

```python
# DuckDB から直接 pandas DataFrame に取り込み
df = con.execute("SELECT * FROM features").df()

# 必要な列を選択
feature_cols = [
    'price_per_sqm',
    'building_age',
    'region_median_price',
    # カテゴリ列は後述のエンコーディングへ
]
X_num = df[feature_cols]

# カテゴリ変数 region_code を OneHotEncoding
X_cat = (
    pd.get_dummies(df['region_code'], prefix='region')
    .astype(float)
)

# 最終的な入力行列
X = pd.concat([X_num, X_cat], axis=1)
y = df['price']  # 目的変数
```

---

## 4. scikit-learn でパイプライン構成＆学習

```python
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

# データ分割
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 前処理＋モデルを一括管理する Pipeline
pipe = Pipeline([
    ('scaler', StandardScaler()),            # 数値特徴量の標準化
    ('reg', RandomForestRegressor(
        n_estimators=100, 
        max_depth=10, 
        n_jobs=-1, 
        random_state=42
    )),
])

# モデル学習
pipe.fit(X_train, y_train)

# 評価
print("R² on test:", pipe.score(X_test, y_test))
```

---

## 5. さらなる高速化＆運用ポイント

1. **マテリアライズ済みテーブルの再利用**

   * 前処理が重い場合は都度再計算せず、中間テーブルを残して再利用
2. **`PRAGMA threads`** で CPU コア数設定

   ```sql
   PRAGMA threads=8;
   ```
3. **大規模時のサンプル抽出**

   ```sql
   CREATE TABLE sample_10pct AS
   SELECT * FROM features
   WHERE RANDOM() < 0.1;
   ```
4. **定期バッチ**

   * 上記をスクリプト化して Airflow や GitHub Actions 等でスケジューリング

---

以上をテンプレート化しておくと、

1. `raw → features` を DuckDB 上で確実に動かし
2. そのまま pandas & scikit-learn パイプラインに渡し
3. モデル性能を確認したら、同じ SQL を本番 DWH（Snowflake 等）に流用

という一貫ワークフローが低コストかつ高再現性で実現できます。次の不動産推測プロジェクト、ぜひこれをベースにしてみてください！
