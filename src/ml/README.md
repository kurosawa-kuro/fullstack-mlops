# ML Package

機械学習関連のモジュールを整理したパッケージです。

## ディレクトリ構造

```
src/ml/
├── __init__.py           # パッケージ初期化
├── data/                 # データ処理
│   ├── __init__.py
│   └── run_processing.py # データクリーニング・前処理
├── features/             # 特徴量エンジニアリング
│   ├── __init__.py
│   └── engineer.py       # 特徴量作成・変換
├── models/               # モデル訓練・評価
│   ├── __init__.py
│   └── train_model.py    # モデル訓練・MLflow登録
└── pipeline/             # パイプライン管理
    ├── __init__.py
    └── train_pipeline.py # エンドツーエンドパイプライン
```

## 使用方法

### 1. データ処理
```bash
python src/ml/data/run_processing.py --input src/ml/data/raw/house_data.csv --output src/ml/data/processed/cleaned_house_data.csv
```

### 2. 特徴量エンジニアリング
```bash
python src/ml/features/engineer.py --input src/ml/data/processed/cleaned_house_data.csv --output src/ml/data/processed/featured_house_data.csv --preprocessor src/ml/models/trained/preprocessor.pkl
```

### 3. モデル訓練
```bash
python src/ml/models/train_model.py --config configs/model_config.yaml --data src/ml/data/processed/featured_house_data.csv --models-dir src/ml/models
```

### 4. 全パイプライン実行
```bash
python src/ml/pipeline/train_pipeline.py
```

## 開発者向け情報

- **Python バージョン**: 3.8+
- **主要依存関係**: pandas, scikit-learn, xgboost, mlflow, joblib
- **テスト**: `pytest src/tests/`
- **コード品質**: `flake8`, `mypy`, `black`

## 注意事項

- 各モジュールは独立して実行可能です
- パイプライン実行時は順序を守ってください（データ処理 → 特徴量エンジニアリング → モデル訓練）
- モデルファイルは `src/ml/models/trained/` ディレクトリに保存されます