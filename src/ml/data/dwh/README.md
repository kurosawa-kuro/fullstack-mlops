# Data Warehouse (DWH) Package

住宅価格予測プロジェクト用のDuckDBデータウェアハウスパッケージです。

## パッケージ構造

```
dwh/
├── __init__.py          # メインパッケージ初期化
├── core/                # コア機能
│   ├── __init__.py
│   ├── database.py      # データベース管理
│   ├── schema.py        # スキーマ管理
│   └── ingestion.py     # データ取り込み
├── scripts/             # ユーティリティスクリプト
│   ├── __init__.py
│   ├── setup_dwh.py     # DWHセットアップ
│   └── explore_dwh.py   # データ探索
├── data/                # データファイル
│   ├── __init__.py
│   └── house_price_dwh.duckdb
└── config/              # 設定ファイル
    ├── __init__.py
    └── settings.py      # 設定管理
```

## 機能

### コア機能 (core/)
- **DWHManager**: DuckDBデータベースの管理
- **スキーマ管理**: テーブル・ビューの作成・削除
- **データ取り込み**: CSVデータの検証・変換・読み込み

### スクリプト (scripts/)
- **setup_dwh.py**: DWHの初期化とデータ取り込み
- **explore_dwh.py**: データベース内容の探索・表示

### 設定 (config/)
- **settings.py**: データベース設定、取り込み設定など

## 使用方法

### 基本的な使用

```python
from ml.data.dwh import DWHManager, ingest_house_data

# DWHマネージャーの初期化
dwh = DWHManager()

# データ取り込み
result = ingest_house_data("house_data.csv", dwh)
```

### スクリプトの実行

```bash
# DWHセットアップ
python src/ml/data/dwh/scripts/setup_dwh.py --csv-file house_data.csv

# データ探索
python src/ml/data/dwh/scripts/explore_dwh.py
```

## データベーススキーマ

### ファクトテーブル
- **fact_house_transactions**: 住宅取引データ

### ディメンションテーブル
- **dim_locations**: 地域情報
- **dim_conditions**: 住宅状態
- **dim_years**: 建築年

### ビュー
- **v_house_analytics**: 分析用ビュー
- **v_summary_statistics**: サマリー統計
- **v_location_analytics**: 地域別分析
- **v_condition_analytics**: 状態別分析

## 設定

`config/settings.py`で以下の設定を変更できます：

- データベース設定（メモリ制限、スレッド数など）
- 取り込み設定（バッチサイズ、検証オプションなど）
- ログ設定

## 開発ガイドライン

1. **コア機能の追加**: `core/`ディレクトリに配置
2. **スクリプトの追加**: `scripts/`ディレクトリに配置
3. **設定の追加**: `config/`ディレクトリに配置
4. **データファイル**: `data/`ディレクトリに配置 