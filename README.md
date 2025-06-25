# 🏠 House Price Predictor – MLOps学習プロジェクト

**House Price Predictor**プロジェクトへようこそ！これは機械学習パイプラインの構築と運用化をマスターするために設計された、実践的なエンドツーエンドMLOpsユースケースです。

生データから始まり、データ前処理、特徴量エンジニアリング、実験、MLflowでのモデル追跡、そして必要に応じてJupyterでの探索まで、業界標準のツールを使用しながら一連の流れを学びます。

> 🚀 **MLOpsをゼロからマスターしたい方へ**  
[School of DevOpsのMLOpsブートキャンプ](https://schoolofdevops.com)でスキルアップしましょう。

---

## 🚀 クイックスタート

### 基本的な使用方法

```bash
# 1. 環境セットアップ
make venv
make install

# 2. モデル訓練（既存モデルがあればスキップ）
make train

# 3. テスト実行
make test

# 4. 全パイプライン実行
make pipeline
```

### 効率的な開発コマンド

```bash
# 既存モデルがあればスキップしてクイック実行
make pipeline-quick

# 強制再訓練（モデルを更新したい場合）
make train-force

# モデル性能確認
make check-model

# プロジェクト状態確認
make status
```

---

## 📦 プロジェクト構成

```
house-price-predictor/
├── configs/                # モデル用YAML設定ファイル
├── data/                   # 生データと処理済みデータセット
├── deployment/
│   └── mlflow/             # MLflow用Docker Compose設定
├── models/                 # 訓練済みモデルと前処理器
├── notebooks/              # 実験用Jupyterノートブック（オプション）
├── src/
│   ├── services/api/      # FastAPIアプリケーション
│   ├── services/ui/       # Streamlitフロントエンド
│   └── ml/                 # 機械学習関連
│       ├── data/           # データクリーニングと前処理スクリプト
│       │   └── dwh/        # DuckDB DWH構築と管理
│       ├── features/       # 特徴量エンジニアリングパイプライン
│       ├── models/         # モデル訓練と評価
│       └── pipeline/       # エンドツーエンドパイプライン
├── requirements.txt        # Python依存関係
└── README.md               # このファイル
```

---

## 🗄️ DuckDB データウェアハウス (DWH) 構築

このプロジェクトでは、DuckDBを使用した高性能なデータウェアハウスを構築し、住宅価格データの分析と機械学習パイプラインの基盤として活用します。

### 🎯 DWHの特徴

- **高性能**: DuckDBの列指向ストレージによる高速クエリ処理
- **軽量**: ファイルベースのデータベースでサーバー不要
- **SQL互換**: 標準SQLによる直感的なデータ操作
- **分析ビュー**: 地域別・状態別の自動分析ビュー
- **スケーラブル**: 大規模データセットにも対応

### 📊 DWHスキーマ設計

#### ディメンションテーブル
- **`dim_locations`**: 地域情報（Suburb, Downtown, Rural, Waterfront等）
- **`dim_conditions`**: 住宅状態（Poor, Fair, Good, Excellent）
- **`dim_years`**: 築年数情報（年、年代、世紀）

#### ファクトテーブル
- **`fact_house_transactions`**: 住宅取引データ（価格、面積、部屋数等）

#### 分析ビュー
- **`v_house_analytics`**: 住宅分析統合ビュー
- **`v_location_analytics`**: 地域別分析
- **`v_condition_analytics`**: 状態別分析
- **`v_summary_statistics`**: 全体統計

### 🚀 DWH構築とデータインジェスション

#### 1. 依存関係のインストール

```bash
# DuckDBのインストール
pip install duckdb

# または requirements.txtに追加
echo "duckdb>=1.3.0" >> requirements.txt
pip install -r requirements.txt
```

#### 2. DWH構築とデータ投入

```bash
# CSVファイルからDWHを構築
python src/ml/data/dwh/setup_dwh.py \
  --csv-file src/ml/data/raw/house_data.csv

# 強制再構築（スキーマを再作成したい場合）
python src/ml/data/dwh/setup_dwh.py \
  --csv-file src/ml/data/raw/house_data.csv \
  --force-schema
```

**期待される出力例：**
```
2025-06-25 08:34:01,000 - __main__ - INFO - Initialized DWH manager
2025-06-25 08:34:01,000 - __main__ - INFO - Starting data ingestion from: src/ml/data/raw/house_data.csv
2025-06-25 08:34:01,041 - ml.data.dwh.ingestion - INFO - Loaded CSV with 84 rows and 7 columns
2025-06-25 08:34:01,171 - ml.data.dwh.ingestion - INFO - Raw data ingestion completed: 84 rows inserted
2025-06-25 08:34:01,314 - ml.data.dwh.ingestion - INFO - Fact data transformation completed: 84 rows inserted
2025-06-25 08:34:01,321 - ml.data.dwh.ingestion - INFO - Data ingestion completed successfully

============================================================
DATA INGESTION RESULTS
============================================================
Status: success
Timestamp: 2025-06-25T08:34:01.321908

Raw Data Stats:
  - Rows inserted: 84
  - Columns: 8

Fact Data Stats:
  - Rows inserted: 84
  - Rows processed: 84
  - Rows with missing dimensions: 0

Summary Statistics:
  - Total houses: 84
  - Average price: $628,559.52
  - Average sqft: 2,192
  - Average price per sqft: $268.09

Location Analytics (Top 3):
  1. Waterfront: $1,306,000 avg price
  2. Mountain: $936,000 avg price
  3. Downtown: $666,471 avg price
```

### 🔍 DWHデータの探索

#### 1. Pythonスクリプトでの探索

```bash
# DWHの内容を詳細表示
python src/ml/data/dwh/explore_dwh.py
```

**出力例：**
```
============================================================
🏠 HOUSE PRICE DWH EXPLORER
============================================================

📊 テーブル一覧 (5個):
  1. dim_conditions
  2. dim_locations
  3. dim_years
  4. fact_house_transactions
  5. raw_house_data

👁️ ビュー一覧 (4個):
  1. v_condition_analytics
  2. v_house_analytics
  3. v_location_analytics
  4. v_summary_statistics

📈 サマリー統計
============================================================
総住宅数: 84
平均価格: $628,559.52
最低価格: $249,000.00
最高価格: $1,680,000.00
平均面積: 2,192 sqft
平均単価: $268.09/sqft

📍 地域別分析:
location_name location_type  house_count    avg_price    avg_sqft  avg_price_per_sqft
   Waterfront       Premium           15 1.306000e+06 3322.800000          391.488445
     Mountain       Premium            2 9.360000e+05 2935.000000          318.744339
     Downtown         Urban           17 6.664706e+05 2415.058824          275.168866
```

#### 2. DuckDB CLIでの直接操作

```bash
# DuckDB CLIのインストール（Ubuntu/WSL）
sudo snap install duckdb

# データベースに接続
duckdb src/ml/data/dwh/house_price_dwh.duckdb
```

**基本的なCLIコマンド：**
```sql
-- テーブル一覧表示
.tables

-- スキーマ表示
.schema

-- サマリー統計を表示
SELECT * FROM v_summary_statistics;

-- 地域別分析を表示
SELECT * FROM v_location_analytics ORDER BY avg_price DESC;

-- 状態別分析を表示
SELECT * FROM v_condition_analytics ORDER BY avg_price DESC;

-- 最初の5件の住宅データを表示
SELECT * FROM fact_house_transactions LIMIT 5;

-- 終了
.quit
```

**便利な分析クエリ例：**
```sql
-- 価格帯別の住宅数分析
SELECT 
  CASE 
    WHEN price < 300000 THEN 'Under $300k'
    WHEN price < 500000 THEN '$300k-$500k'
    WHEN price < 800000 THEN '$500k-$800k'
    ELSE 'Over $800k'
  END as price_range,
  COUNT(*) as house_count,
  AVG(price) as avg_price
FROM fact_house_transactions
GROUP BY price_range
ORDER BY MIN(price);

-- 築年数別の平均価格分析
SELECT 
  y.decade,
  AVG(h.price) as avg_price,
  COUNT(*) as house_count,
  AVG(h.sqft) as avg_sqft
FROM fact_house_transactions h
JOIN dim_years y ON h.year_built_id = y.year_id
GROUP BY y.decade
ORDER BY y.decade;

-- 地域・状態別の価格分析
SELECT 
  l.location_name,
  c.condition_name,
  COUNT(*) as house_count,
  AVG(h.price) as avg_price,
  AVG(h.price/h.sqft) as avg_price_per_sqft
FROM fact_house_transactions h
JOIN dim_locations l ON h.location_id = l.location_id
JOIN dim_conditions c ON h.condition_id = c.condition_id
GROUP BY l.location_name, c.condition_name
ORDER BY avg_price DESC;
```

**ワンライナーでのクエリ実行：**
```bash
# テーブル一覧を表示
duckdb src/ml/data/dwh/house_price_dwh.duckdb ".tables"

# サマリー統計を表示
duckdb src/ml/data/dwh/house_price_dwh.duckdb "SELECT * FROM v_summary_statistics;"

# 地域別分析を表示
duckdb src/ml/data/dwh/house_price_dwh.duckdb "SELECT * FROM v_location_analytics ORDER BY avg_price DESC;"

# 価格帯別分析を表示
duckdb src/ml/data/dwh/house_price_dwh.duckdb "
SELECT 
  CASE 
    WHEN price < 300000 THEN 'Under $300k'
    WHEN price < 500000 THEN '$300k-$500k'
    WHEN price < 800000 THEN '$500k-$800k'
    ELSE 'Over $800k'
  END as price_range,
  COUNT(*) as house_count,
  AVG(price) as avg_price
FROM fact_house_transactions
GROUP BY price_range
ORDER BY MIN(price);
"
```

### 🔧 DWH管理コマンド

#### データベース情報の確認
```bash
# ファイルサイズ確認
ls -lh src/ml/data/dwh/house_price_dwh.duckdb

# データベース統計
python -c "
import duckdb
con = duckdb.connect('src/ml/data/dwh/house_price_dwh.duckdb')
result = con.execute('SELECT COUNT(*) FROM fact_house_transactions').fetchone()
print(f'Total records: {result[0]:,}')
con.close()
"
```

#### バックアップとリストア
```bash
# バックアップ作成
cp src/ml/data/dwh/house_price_dwh.duckdb src/ml/data/dwh/backups/house_price_dwh_${DATE}.duckdb
```

### ⚠️ DWH関連のトラブルシューティング

#### 1. DuckDB CLIが見つからない
```bash
# Ubuntu/WSLでのインストール
sudo snap install duckdb

# インストール確認
which duckdb
duckdb --version

# または、Pythonから直接実行
python -c "
import duckdb
con = duckdb.connect('src/ml/data/dwh/house_price_dwh.duckdb')
print(con.execute('SELECT * FROM v_summary_statistics').fetchall())
con.close()
"
```

#### 2. データベースファイルが破損
```bash
# バックアップから復元
cp src/ml/data/dwh/house_price_dwh_backup.duckdb src/ml/data/dwh/house_price_dwh.duckdb

# または、DWHを再構築
python src/ml/data/dwh/setup_dwh.py \
  --csv-file src/ml/data/raw/house_data.csv \
  --force-schema
```

#### 3. メモリ不足エラー
```bash
# DuckDBのメモリ設定を調整
python -c "
import duckdb
con = duckdb.connect('src/ml/data/dwh/house_price_dwh.duckdb')
con.execute('SET memory_limit=\'1GB\'')
# クエリ実行
con.close()
"
```

#### 4. CLIでアクセスできない場合

**問題**: `duckdb src/ml/data/dwh/house_price_dwh.duckdb`でプロンプトが表示されない

**解決策**:
```bash
# 1. ファイルの存在確認
ls -la src/ml/data/dwh/house_price_dwh.duckdb

# 2. ファイルの権限確認
chmod 644 src/ml/data/dwh/house_price_dwh.duckdb

# 3. 絶対パスでアクセス
duckdb /home/wsl/dev/mlops/fullstack-mlops/src/ml/data/dwh/house_price_dwh.duckdb

# 4. ワンライナーでテスト
duckdb src/ml/data/dwh/house_price_dwh.duckdb ".tables"
```

#### 5. クエリ実行時のエラー

**問題**: SQLクエリでエラーが発生する

**解決策**:
```bash
# 1. テーブル存在確認
duckdb src/ml/data/dwh/house_price_dwh.duckdb ".tables"

# 2. スキーマ確認
duckdb src/ml/data/dwh/house_price_dwh.duckdb ".schema"

# 3. 簡単なクエリでテスト
duckdb src/ml/data/dwh/house_price_dwh.duckdb "SELECT COUNT(*) FROM fact_house_transactions;"
```

#### 6. VSCode拡張でアクセスできない場合

**問題**: VSCodeでDuckDBファイルを開けない

**解決策**:
```bash
# 1. VSCode拡張の再インストール
# VSCodeで拡張をアンインストール後、再インストール

# 2. ファイルパスの確認
# WSL環境では、Windows側のVSCodeからWSLのファイルにアクセス

# 3. 代替方法：PythonスクリプトでGUI表示
python -c "
import duckdb
import pandas as pd
con = duckdb.connect('src/ml/data/dwh/house_price_dwh.duckdb')
df = con.execute('SELECT * FROM v_summary_statistics').df()
print(df.to_string(index=False))
con.close()
"
```

#### 7. DuckDBロックエラー

**問題**: `Error: unable to open database: IO Error: Could not set lock on file: Conflicting lock is held`

**解決策**:
```bash
# 1. 既存のDuckDBプロセスを確認
ps aux | grep duckdb

# 2. ユーザープロセスを終了
pkill -f duckdb

# 3. または、Pythonプロセスを終了
pkill -f python.*duckdb

# 4. 再度アクセスを試行
make dwh-tables

# 5. それでも解決しない場合は、データベースファイルを再作成
make dwh-force
```

**予防策**:
- 複数のDuckDBプロセスを同時に起動しない
- 使用後は必ず`.quit`でCLIを終了
- Pythonスクリプトでは`con.close()`を確実に実行

### 🎯 DWH活用のベストプラクティス

#### 1. **定期的なバックアップ**
```bash
# 日次バックアップスクリプト例
#!/bin/bash
DATE=$(date +%Y%m%d)
cp src/ml/data/dwh/house_price_dwh.duckdb \
   src/ml/data/dwh/backups/house_price_dwh_${DATE}.duckdb
```

#### 2. **パフォーマンス最適化**
- インデックスの適切な設定
- クエリの最適化
- 定期的なVACUUM実行

#### 3. **データ品質管理**
- 定期的なデータ整合性チェック
- 異常値の検出と処理
- データ更新履歴の管理

#### 4. VSCodeでのGUI参照

1. **VSCode拡張のインストール**:
   - VSCode Marketplaceで「DuckDB」を検索
   - DuckDB拡張をインストール

2. **データベースファイルを開く**:
   ```bash
   # WSLからVSCodeを起動
   code .
   ```
   - `src/ml/data/dwh/house_price_dwh.duckdb`を右クリック
   - 「Open With DuckDB」を選択

3. **GUIでの操作**:
   - テーブル一覧の表示
   - SQLクエリの実行
   - 結果の可視化
   - データのエクスポート

4. **Pythonスクリプトでの操作**

```bash
# 統計情報を表示
make dwh-stats

# 詳細な探索
make dwh-explore

# カスタムクエリ実行
python -c "
import duckdb
con = duckdb.connect('src/ml/data/dwh/house_price_dwh.duckdb')
result = con.execute('SELECT * FROM v_summary_statistics').fetchall()
print('📊 サマリー統計:')
for row in result:
    print(f'  総住宅数: {row[0]:,}')
    print(f'  平均価格: ${row[1]:,.2f}')
    print(f'  最低価格: ${row[2]:,.2f}')
    print(f'  最高価格: ${row[3]:,.2f}')
con.close()
"
```

---

## 🛠️ 学習・開発環境のセットアップ

まず、以下のツールがシステムにインストールされていることを確認してください：

- [Python 3.11](https://www.python.org/downloads/) **または** [Python 3.12](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- [Visual Studio Code](https://code.visualstudio.com/) または他のエディタ
- [UV – Pythonパッケージ・環境管理ツール](https://github.com/astral-sh/uv)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) **または** [Podman Desktop](https://podman-desktop.io/)

---

## 🚀 環境の準備

### 前提条件の確認

1. **必要なツールがインストールされているか確認：**
   ```bash
   python3 --version  # Python 3.11以上
   git --version      # Git
   docker --version   # Docker
   ```

2. **UVのインストール確認：**
   ```bash
   uv --version
   ```
   インストールされていない場合：
   ```bash
   sudo snap install astral-uv --classic
   ```

### プロジェクトのセットアップ

1. **このリポジトリをフォーク**してください（GitHub上で）

2. **フォークしたリポジトリをクローン：**
   ```bash
   # xxxxxxをあなたのGitHubユーザー名または組織名に置き換えてください
   git clone https://github.com/xxxxxx/house-price-predictor.git
   cd house-price-predictor
   ```

3. **UVを使用してPython仮想環境をセットアップ：**
   ```bash
   # Python 3.11の場合
   uv venv --python python3.11
   # または Python 3.12の場合
   uv venv --python python3.12
   
   source .venv/bin/activate
   ```

4. **仮想環境が正しくアクティベートされたか確認：**
   ```bash
   which python
   # 出力例: /home/wsl/dev/mlops/house-price-predictor/.venv/bin/python
   
   python --version
   # 出力例: Python 3.12.3
   ```

5. **依存関係をインストール：**
   ```bash
   uv pip install -r requirements.txt
   ```

6. **インストールの確認：**
   ```bash
   python -c "import mlflow, pandas, numpy, sklearn; print('All packages installed successfully!')"
   ```

---

## ⚠️ トラブルシューティング

### Python 3.12での依存関係インストールエラー

Python 3.12を使用している場合、以下のエラーが発生する可能性があります：

#### 1. numpyビルドエラー
```
ModuleNotFoundError: No module named 'distutils'
```

**解決策：** `requirements.txt`の`numpy==1.24.3`を`numpy>=1.25.0`に変更してください。

#### 2. pyarrowビルドエラー
```
CMake Error: Could not find a package configuration file provided by "Arrow"
```

**解決策：** `requirements.txt`の末尾に`pyarrow>=14.0.0`を追加してください。

#### 3. mlflowとpyarrowのバージョン競合
```
Because mlflow==2.3.1 depends on pyarrow>=4.0.0,<12 and you require pyarrow>=14.0.0
```

**解決策：** `requirements.txt`の`mlflow==2.3.1`を`mlflow>=2.10.0`に変更してください。

#### 4. バイナリ互換性エラー（numpy/pandas/scikit-learn）
```
ValueError: numpy.dtype size changed, may indicate binary incompatibility. Expected 96 from C header, got 88 from PyObject
```

**解決策：** 以下のコマンドでパッケージを再インストールしてください：
```bash
# 仮想環境がアクティベートされていることを確認
source .venv/bin/activate

# パッケージを再インストール
uv pip install --force-reinstall --no-cache-dir numpy pandas scikit-learn
```

#### 5. pipコマンドが見つからない
```
which pip
# 出力: /usr/bin/pip (システムのpip)
```

**解決策：** `uv`を使用してパッケージをインストールしてください：
```bash
uv pip install [パッケージ名]
```

### モデル訓練時のエラー

#### 1. 設定ファイルが見つからない
```
FileNotFoundError: [Errno 2] No such file or directory: 'configs/model_config.yaml'
```

**解決策：** `configs`ディレクトリと設定ファイルを作成してください：
```bash
mkdir -p configs
```

#### 2. 設定ファイルのキーエラー
```
KeyError: 'name'
KeyError: 'target_variable'
KeyError: 'best_model'
```

**解決策：** `configs/model_config.yaml`に必要なキーを追加してください：
```yaml
name: "house_price_prediction"

model:
  name: "house_price_prediction"
  type: "random_forest"
  target_variable: "price"
  best_model: "RandomForest"
  parameters:
    n_estimators: 100
    max_depth: 10
    min_samples_split: 2
    min_samples_leaf: 1
    random_state: 42
```

### Docker関連の問題

#### 1. MLflowにアクセスできない（WSL2環境）
```
ERR_CONNECTION_REFUSED
```

**解決策：**
1. WSL2のIPアドレスを確認：`ip addr show eth0 | grep inet`
2. `http://[WSL2のIP]:5555`でアクセス（例：`http://192.168.1.131:5555`）

#### 2. FastAPI/Streamlitアプリにアクセスできない（WSL2環境）
```
ERR_CONNECTION_REFUSED
```

**解決策：**
1. WSL2のIPアドレスを確認：`ip addr show eth0 | grep inet`
2. 以下のURLでアクセス：
   - Streamlit: `http://[WSL2のIP]:8501`
   - FastAPI: `http://[WSL2のIP]:8000`

#### 3. Docker Composeの警告
```
WARN[0000] the attribute `version` is obsolete, it will be ignored
```

**解決策：** この警告は無視して問題ありません。新しいDocker Composeでは`version`属性は不要です。

#### 4. コンテナが起動しない
```bash
# コンテナのログを確認
docker compose logs

# コンテナを再起動
docker compose down
docker compose up -d
```

#### 5. Python 3.12での依存関係ビルドエラー
```
pip._vendor.pyproject_hooks._impl.BackendUnavailable: Cannot import 'setuptools.build_meta'
```

**解決策：** Dockerfileでsetuptoolsを先にインストールするように修正済みです。

#### 6. モデルファイルが見つからないエラー
```
FileNotFoundError: [Errno 2] No such file or directory: 'models/trained/house_price_model.pkl'
```

**解決策：** `src/services/api/inference.py`のモデルファイル名を`house_price_prediction.pkl`に修正済みです。

#### 7. コンテナが再起動を繰り返す
```bash
# 確認方法
docker compose logs fastapi
```

**解決策：**
1. モデルファイルが存在することを確認
2. ファイル名が正しいことを確認
3. コンテナを再ビルド：
   ```bash
   docker compose down
   docker compose up --build -d
   ```

#### 8. ポートが既に使用されている
```
Error response from daemon: driver failed programming external connectivity on endpoint
```

**解決策：**
```bash
# 使用中のポートを確認
netstat -tlnp | grep :8000
netstat -tlnp | grep :8501

# 既存のコンテナを停止
docker compose down

# 他のプロセスを停止してから再起動
docker compose up -d
```

#### 9. メモリ不足エラー
```
failed to register layer: Error processing tar file(exit status 1): write /usr/local/lib/python3.12/site-packages/... no space left on device
```

**解決策：**
```bash
# Dockerの未使用リソースをクリーンアップ
docker system prune -a

# ディスク容量を確認
df -h
```

### MLflow関連の警告

#### 1. モデルシグネチャの警告
```
WARNING mlflow.models.model: Model logged without a signature and input example
```

**解決策：** この警告は動作に影響しません。本格運用時には`input_example`パラメータを追加することを推奨します。

#### 2. 非推奨パラメータの警告
```
WARNING mlflow.models.model: `artifact_path` is deprecated. Please use `name` instead.
```

**解決策：** この警告は動作に影響しません。将来のバージョンで修正される予定です。

#### 3. モデルバージョンの重複
```
Registered model 'house_price_prediction' already exists. Creating a new version
```

**解決策：** これは正常な動作です。同じモデル名で複数回実行すると新しいバージョンが作成されます。

### JupyterLab関連の問題

#### 1. JupyterLabがインストールされていない
```
No module named jupyterlab
```

**解決策：** JupyterLabをインストールしてください：
```bash
uv pip install jupyterlab
```

#### 2. 仮想環境がアクティベートされていない
```
Command 'python' not found
```

**解決策：** 仮想環境をアクティベートしてください：
```bash
source .venv/bin/activate
```

### 修正後のrequirements.txt例
```txt
# データ処理・分析
pandas==1.5.3
numpy>=1.25.0

# 機械学習
scikit-learn==1.2.2
xgboost==1.7.5

# 可視化
matplotlib==3.7.1
seaborn==0.12.2

# 実験追跡・モデル管理
mlflow>=2.10.0

# テスト
pytest==7.3.1

# API開発
fastapi==0.95.2
uvicorn==0.22.0

# その他
pyyaml>=6.0.1
joblib==1.3.1
setuptools==65.5.0
ipykernel==6.29.5
pyarrow>=14.0.0
jupyterlab>=4.0.0
```

---

## 📊 実験追跡用MLflowのセットアップ

実験とモデル実行を追跡するために：

```bash
cd deployment/mlflow
docker compose -f docker-compose.yaml up -d
docker compose ps
```

> 🐧 **Podmanを使用している場合：**
```bash
podman compose -f docker-compose.yaml up -d
podman compose ps
```

### WSL2環境でのMLflowアクセス

WSL2環境では、`localhost`でのアクセスに問題がある場合があります。以下の手順で確認してください：

#### 1. コンテナの状態確認
```bash
docker compose ps
```
出力例：
```
NAME                     IMAGE                          COMMAND                  SERVICE   CREATED         STATUS         PORTS
mlflow-tracking-server   ghcr.io/mlflow/mlflow:latest   "mlflow server --hos…"   mlflow    4 minutes ago   Up 4 minutes   0.0.0.0:5555->5000/tcp, [::]:5555->5000/tcp
```

#### 2. WSL2のIPアドレス確認
```bash
ip addr show eth0 | grep inet
```
出力例：
```
inet 192.168.1.131/24 brd 192.168.1.255 scope global noprefixroute eth0
```

#### 3. MLflow UIへのアクセス
以下のURLのいずれかでアクセスしてください：

**推奨方法（WSL2のIPアドレスを使用）：**
```
http://192.168.1.131:5555
```

**代替方法（localhostを使用）：**
```
http://localhost:5555
```

> ⚠️ **注意**: WSL2環境では、`localhost`でのアクセスが拒否される場合があります。その場合は、WSL2のIPアドレス（例：`192.168.1.131:5555`）を使用してください。

#### 4. トラブルシューティング

**ポートがリッスンしているか確認：**
```bash
netstat -tlnp | grep 5555
```

**コンテナを再起動する場合：**
```bash
docker compose down
docker compose up -d
```

**Docker Composeの警告について：**
```
WARN[0000] the attribute `version` is obsolete, it will be ignored
```
この警告は無視して問題ありません。Docker Composeの新しいバージョンでは`version`属性は不要です。

---

## 📒 JupyterLabの使用（オプション）

インタラクティブな環境を好む場合は、JupyterLabを起動してください：

```bash
# プロジェクトのルートディレクトリにいることを確認
cd /path/to/house-price-predictor

# 仮想環境がアクティベートされていることを確認
source .venv/bin/activate

# JupyterLabを起動
python -m jupyterlab
```

> ⚠️ **注意**: `uv python -m jupyterlab`は正しくありません。`uv python`はPythonの管理用コマンドです。JupyterLabを起動するには`python -m jupyterlab`を使用してください。

起動後、ブラウザで表示されるURL（通常は`http://localhost:8888`）にアクセスしてください。

---

## 🔁 モデルワークフロー

### 🧹 ステップ1: データ処理

生の住宅データセットをクリーニングと前処理：

```bash
python src/ml/data/run_processing.py \
  --input src/ml/data/raw/house_data.csv \
  --output src/ml/data/processed/cleaned_house_data.csv
```

**期待される出力例：**
```
2025-06-24 06:52:02,179 - data-processor - INFO - Loading data from src/ml/data/raw/house_data.csv
2025-06-24 06:52:02,181 - data-processor - INFO - Loaded data with shape: (84, 7)
2025-06-24 06:52:02,181 - data-processor - INFO - Cleaning dataset
2025-06-24 06:52:02,183 - data-processor - INFO - Found 7 outliers in price column
2025-06-24 06:52:02,183 - data-processor - INFO - Removed outliers. New dataset shape: (77, 7)
2025-06-24 06:52:02,186 - data-processor - INFO - Saved processed data to src/ml/data/processed/cleaned_house_data.csv
```

---

### 🧠 ステップ2: 特徴量エンジニアリング

変換を適用し、特徴量を生成：

```bash
python src/ml/features/engineer.py \
  --input src/ml/data/processed/cleaned_house_data.csv \
  --output src/ml/data/processed/featured_house_data.csv \
  --preprocessor src/ml/models/trained/preprocessor.pkl
```

**期待される出力例：**
```
2025-06-24 06:55:07,608 - feature-engineering - INFO - Loading data from src/ml/data/processed/cleaned_house_data.csv
2025-06-24 06:55:07,610 - feature-engineering - INFO - Creating new features
2025-06-24 06:55:07,611 - feature-engineering - INFO - Created 'house_age' feature
2025-06-24 06:55:07,611 - feature-engineering - INFO - Created 'price_per_sqft' feature
2025-06-24 06:55:07,611 - feature-engineering - INFO - Created 'bed_bath_ratio' feature
2025-06-24 06:55:07,612 - feature-engineering - INFO - Created featured dataset with shape: (77, 10)
2025-06-24 06:55:07,612 - feature-engineering - INFO - Creating preprocessor pipeline
2025-06-24 06:55:07,618 - feature-engineering - INFO - Fitted the preprocessor and transformed the features
2025-06-24 06:55:07,619 - feature-engineering - INFO - Saved preprocessor to src/ml/models/trained/preprocessor.pkl
2025-06-24 06:55:07,621 - feature-engineering - INFO - Saved fully preprocessed data to src/ml/data/processed/featured_house_data.csv
```

---

### 📈 ステップ3: モデリングと実験

モデルを訓練し、すべてをMLflowにログ：

```bash
python src/ml/models/train_model.py \
  --config configs/model_config.yaml \
  --data src/ml/data/processed/featured_house_data.csv \
  --models-dir src/ml/models \
  --mlflow-tracking-uri http://192.168.1.131:5555
```

**期待される出力例：**
```
2025-06-24 07:02:09,052 - INFO - Training model: RandomForest
2025-06-24 07:02:10,699 - INFO - Registering model to MLflow Model Registry...
2025-06-24 07:02:10,997 - INFO - Saved trained model to: src/ml/models/trained/house_price_prediction.pkl
2025-06-24 07:02:10,997 - INFO - Final MAE: 13977.50, R²: 0.9882
🏃 View run final_training at: http://192.168.1.131:5555/#/experiments/1/runs/f0f4aa121cc5405f93fcc03e77962b89
🧪 View experiment at: http://192.168.1.131:5555/#/experiments/1
```

---

#### 📊 モデル性能比較（2025年6月時点）

| モデル                | MAE（平均絶対誤差） | R²（決定係数） |
|----------------------|---------------------|---------------|
| **Stacking Ensemble**     | **10,858**             | **0.9929**    |
| Voting Ensemble      | 12,169              | 0.9917        |
| GradientBoosting     | 11,204              | 0.9916        |
| RandomForest         | 13,978              | 0.9882        |
| XGBoost              | 15,245              | 0.9894        |

- **最も高精度なのはStacking Ensemble（MAE: 10,858, R²: 0.9929）**
- Voting Ensembleも単体モデルより高精度
- 全体的に業界トップクラスの精度（R² 99%超）

##### 解説
- Stackingは複数モデルの長所を活かし、最終的な予測精度が最も高くなりました。
- Votingも安定した高精度ですが、Stackingの方が誤差がさらに小さくなります。
- データ件数が少ない場合でもアンサンブル効果がしっかり現れています。

---

### 📊 結果の確認

#### MLflow UIでの確認
1. ブラウザでMLflow UIにアクセス（例：`http://192.168.1.131:5555`）
2. 実験一覧から「house_price_prediction」を選択
3. 実行履歴、メトリクス、モデルバージョンを確認

#### 生成されたファイル
- `src/ml/data/processed/cleaned_house_data.csv`: クリーニング済みデータ
- `src/ml/data/processed/featured_house_data.csv`: 特徴量エンジニアリング済みデータ
- `src/ml/models/trained/preprocessor.pkl`: 前処理器
- `src/ml/models/trained/house_price_prediction.pkl`: 訓練済みモデル

---

## 🚀 FastAPIとStreamlitアプリケーションの構築

FastAPIとStreamlitアプリのコードは、すでに`src/services/api`と`src/services/ui`に用意されています。これらのアプリを構築して起動するには：

### 📋 前提条件

1. **DockerとDocker Composeがインストールされていることを確認：**
   ```bash
   docker --version
   docker compose version
   ```

2. **訓練済みモデルが存在することを確認：**
   ```bash
   ls -la src/ml/models/trained/
   # 以下のファイルが存在することを確認：
   # - house_price_prediction.pkl
   # - preprocessor.pkl
   ```

### 🔧 アプリケーションの構築と起動

1. **Docker Composeでアプリケーションを起動：**
   ```bash
   docker compose up --build -d
   ```

2. **コンテナの状態を確認：**
   ```bash
   docker compose ps
   ```

3. **アプリケーションにアクセス：**
   - **Streamlit Web UI**: `http://192.168.1.131:8501`
   - **FastAPI エンドポイント**: `http://192.168.1.131:8000`
   - **FastAPI ドキュメント**: `http://192.168.1.131:8000/docs`

### 🧪 API テスト

FastAPIを直接使用して予測をテスト：

```bash
curl -X POST "http://192.168.1.131:8000/predict" \
-H "Content-Type: application/json" \
-d '{
  "sqft": 1500,
  "bedrooms": 3,
  "bathrooms": 2,
  "location": "suburban",
  "year_built": 2000,
  "condition": "fair"
}'
```

**期待される応答例：**
```json
{
  "predicted_price": 482690.0,
  "confidence_interval": [434421.0, 530959.0],
  "features_importance": {},
  "prediction_time": "2025-06-23T22:51:21.143610"
}
```

### ⚠️ トラブルシューティング

#### 1. Python 3.12での依存関係ビルドエラー

**エラー例：**
```
pip._vendor.pyproject_hooks._impl.BackendUnavailable: Cannot import 'setuptools.build_meta'
```

**解決策：** Dockerfileでsetuptoolsを先にインストールするように修正済みです。

#### 2. モデルファイルが見つからないエラー

**エラー例：**
```
FileNotFoundError: [Errno 2] No such file or directory: 'models/trained/house_price_model.pkl'
```

**解決策：** `src/services/api/inference.py`のモデルファイル名を`house_price_prediction.pkl`に修正済みです。

#### 3. コンテナが再起動を繰り返す

**確認方法：**
```bash
docker compose logs fastapi
```

**解決策：**
1. モデルファイルが存在することを確認
2. ファイル名が正しいことを確認
3. コンテナを再ビルド：
   ```bash
   docker compose down
   docker compose up --build -d
   ```

#### 4. WSL2環境でのアクセス問題

**問題：** `localhost`でのアクセスが拒否される

**解決策：** WSL2のIPアドレスを使用：
```bash
# WSL2のIPアドレスを確認
ip addr show eth0 | grep inet

# アプリケーションにアクセス
# Streamlit: http://[WSL2_IP]:8501
# FastAPI: http://[WSL2_IP]:8000
```

#### 5. ポートが既に使用されている

**エラー例：**
```
Error response from daemon: driver failed programming external connectivity on endpoint
```

**解決策：**
```bash
# 使用中のポートを確認
netstat -tlnp | grep :8000
netstat -tlnp | grep :8501

# 既存のコンテナを停止
docker compose down

# 他のプロセスを停止してから再起動
docker compose up -d
```

#### 6. メモリ不足エラー

**エラー例：**
```
failed to register layer: Error processing tar file(exit status 1): write /usr/local/lib/python3.12/site-packages/... no space left on device
```

**解決策：**
```bash
# Dockerの未使用リソースをクリーンアップ
docker system prune -a

# ディスク容量を確認
df -h
```

### 📊 アプリケーション構成

#### FastAPI バックエンド
- **ポート**: 8000
- **エンドポイント**:
  - `GET /health`: ヘルスチェック
  - `POST /predict`: 単一予測
  - `POST /batch-predict`: バッチ予測
- **自動生成ドキュメント**: `http://192.168.1.131:8000/docs`

#### Streamlit フロントエンド
- **ポート**: 8501
- **機能**:
  - インタラクティブな予測フォーム
  - リアルタイム結果表示
  - 信頼区間の可視化
- **環境変数**: `API_URL=http://fastapi:8000`

### 🔄 アプリケーションの管理

#### 起動
```bash
docker compose up -d
```

#### 停止
```bash
docker compose down
```

#### ログ確認
```bash
# 全サービスのログ
docker compose logs

# 特定サービスのログ
docker compose logs fastapi
docker compose logs streamlit
```

#### 再ビルド
```bash
docker compose down
docker compose up --build -d
```

### 🎯 次のステップ

1. **Streamlit UIで予測を試す**: `http://192.168.1.131:8501`
2. **API ドキュメントを確認**: `http://192.168.1.131:8000/docs`
3. **バッチ予測をテスト**: 複数の住宅データで一括予測
4. **モデル性能の監視**: MLflowで実験結果を確認
5. **本番環境へのデプロイ**: KubernetesやAWS ECSでの運用

### ✅ 成功例

#### アプリケーション起動確認
```bash
# コンテナの状態確認
docker compose ps

# 出力例：
NAME                                IMAGE                             COMMAND                  SERVICE     CREATED         STATUS         PORTS
house-price-predictor-fastapi-1     house-price-predictor-fastapi     "uvicorn main:app --…"   fastapi     4 minutes ago   Up 4 minutes   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
house-price-predictor-streamlit-1   house-price-predictor-streamlit   "streamlit run app.py"   streamlit   4 minutes ago   Up 4 minutes   0.0.0.0:8501->8501/tcp, [::]:8501->8501/tcp
```

#### API テスト成功例
```bash
curl -X POST "http://192.168.1.131:8000/predict" \
-H "Content-Type: application/json" \
-d '{
  "sqft": 1500,
  "bedrooms": 3,
  "bathrooms": 2,
  "location": "suburban",
  "year_built": 2000,
  "condition": "fair"
}'

# 応答例：
{
  "predicted_price": 482690.0,
  "confidence_interval": [434421.0, 530959.0],
  "features_importance": {},
  "prediction_time": "2025-06-23T22:51:21.143610"
}
```

### 🌐 アクセス情報

| サービス | URL | 説明 |
|---------|-----|------|
| Streamlit UI | `http://192.168.1.131:8501` | メインのWebインターフェース |
| FastAPI | `http://192.168.1.131:8000` | REST API エンドポイント |
| FastAPI Docs | `http://192.168.1.131:8000/docs` | 自動生成APIドキュメント |
| MLflow UI | `http://192.168.1.131:5555` | 実験追跡・モデル管理 |

> 💡 **注意**: WSL2環境では、`localhost`の代わりにWSL2のIPアドレス（`192.168.1.131`）を使用してください。

---

## 🔄 CI/CD パイプライン

このプロジェクトには、GitHub Actionsを使用した自動化されたCI/CDパイプラインが含まれています。コードの品質チェック、テスト、モデル訓練、そしてリリースまで自動化されています。

### 📋 CI/CD ワークフロー構成

#### 1. **コード品質チェック** (`code-quality`)
- **実行タイミング**: プッシュ・プルリクエスト時
- **内容**:
  - Black によるコードフォーマットチェック
  - isort によるインポート順序チェック
  - flake8 によるリント
  - mypy による型チェック
  - bandit によるセキュリティチェック

#### 2. **テスト実行** (`test`)
- **実行タイミング**: コード品質チェック後
- **内容**:
  - 基本ユニットテスト
  - カバレッジレポート生成
  - Codecov へのカバレッジアップロード

#### 3. **モデル訓練** (`train-model`)
- **実行タイミング**: main/masterブランチへのプッシュ時のみ
- **内容**:
  - データ処理パイプライン実行
  - 特徴量エンジニアリング
  - モデル訓練
  - アーティファクトの保存

#### 4. **モデル性能テスト** (`model-performance`)
- **実行タイミング**: モデル訓練後
- **内容**:
  - 訓練済みモデルの読み込みテスト
  - 予測機能テスト
  - モデルファイルサイズ確認

#### 5. **リリース作成** (`create-release`)
- **実行タイミング**: タグプッシュ時
- **内容**:
  - GitHub Release の自動作成
  - モデルファイルのリリース添付
  - リリースノートの自動生成

### 🚀 CI/CD の使用方法

#### 自動実行
```bash
# mainブランチにプッシュすると自動実行
git add .
git commit -m "feat: 新しい特徴量を追加"
git push origin main
```

#### 手動実行
1. GitHub リポジトリの **Actions** タブに移動
2. **ML Model CI/CD** ワークフローを選択
3. **Run workflow** ボタンをクリック

#### リリース作成
```bash
# タグを作成してプッシュ
git tag v1.0.0
git push origin v1.0.0
```

### 📊 CI/CD ダッシュボード

#### GitHub Actions での確認
- **ワークフロー実行状況**: `https://github.com/[username]/house-price-predictor/actions`
- **実行ログ**: 各ジョブの詳細ログを確認可能
- **アーティファクト**: 訓練済みモデルとデータのダウンロード

#### 成功例
```
✅ code-quality: コード品質チェック完了
✅ test: テスト実行完了 (カバレッジ: 85%)
✅ train-model: モデル訓練完了 (MAE: 13977.50, R²: 0.9882)
✅ model-performance: モデル性能テスト完了
✅ create-release: リリース v1.0.0 作成完了
```

### 🔧 CI/CD 設定ファイル

#### ワークフローファイル
- **場所**: `.github/workflows/ml-cicd.yml`
- **主要設定**:
  - Python 3.12 環境
  - 依存関係キャッシュ
  - 条件付き実行
  - アーティファクト管理

#### 実行条件
```yaml
on:
  push:
    branches: [main, master, develop]
    paths: ['src/**', 'src/configs/**', 'src/ml/data/**', 'src/tests/**']
  pull_request:
    branches: [main, master, develop]
  workflow_dispatch:  # 手動実行
```

### 📈 CI/CD メトリクス

#### 品質指標
- **コードカバレッジ**: 85%以上を目標
- **リントエラー**: 0件を目標
- **型チェック**: エラー0件を目標
- **セキュリティ**: 高リスク0件を目標

#### パフォーマンス指標
- **ビルド時間**: 通常5-10分
- **テスト実行時間**: 通常2-3分
- **モデル訓練時間**: 通常1-2分

### 🛠️ CI/CD トラブルシューティング

#### 1. ワークフローが実行されない
**原因**: ファイルパスの変更が対象外
**解決策**: `paths`設定を確認し、必要に応じて追加

#### 2. 依存関係インストールエラー
**原因**: requirements.txtのバージョン競合
**解決策**: パッケージバージョンを調整

#### 3. モデル訓練エラー
**原因**: 設定ファイルの不備
**解決策**: `configs/model_config.yaml`の内容を確認

#### 4. アーティファクトアップロードエラー
**原因**: ファイルサイズ制限
**解決策**: 不要なファイルを除外設定に追加

### 🎯 CI/CD ベストプラクティス

#### 1. **コミットメッセージ**
```bash
# 良い例
git commit -m "feat: 新しい特徴量エンジニアリングを追加"
git commit -m "fix: モデル訓練時のエラーを修正"
git commit -m "docs: READMEにCI/CD説明を追加"

# 避けるべき例
git commit -m "update"
git commit -m "fix bug"
```

#### 2. **ブランチ戦略**
```bash
# 開発ブランチで作業
git checkout -b feature/new-model
git add .
git commit -m "feat: 新しいモデルアルゴリズムを追加"
git push origin feature/new-model

# プルリクエスト作成
# mainブランチにマージ後、CI/CDが自動実行
```

#### 3. **テスト戦略**
- 新機能追加時は必ずテストを追加
- カバレッジを85%以上に維持
- 統合テストとユニットテストの両方を実装

### 🔄 継続的改善

#### 1. **パイプライン最適化**
- キャッシュ戦略の見直し
- 並列実行の活用
- 不要なステップの削除

#### 2. **品質向上**
- 静的解析ツールの追加
- セキュリティスキャンの強化
- パフォーマンステストの追加

#### 3. **監視とアラート**
- ワークフロー失敗時の通知
- パフォーマンスメトリクスの追跡
- セキュリティ脆弱性の監視

---

## 🧠 MLOpsについてさらに詳しく

このプロジェクトは、School of DevOpsの[**MLOpsブートキャンプ**](https://schoolofdevops.com)の一部です。そこでは以下のことを学べます：

- MLパイプラインの構築と追跡
- モデルのコンテナ化とデプロイ
- GitHub ActionsやArgo Workflowsを使用した訓練ワークフローの自動化
- 機械学習システムへのDevOpsの原則の適用

🔗 [MLOpsを始める →](https://schoolofdevops.com)

---

## 🤝 貢献

このプロジェクトをさらに良くするための貢献、課題、提案を歓迎します。お気軽にフォーク、探索、そしてプルリクエストを送ってください！

---

ハッピーラーニング！  
— **School of DevOps**チーム