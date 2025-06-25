# 🏠 House Price Predictor – エンドツーエンドMLOpsプロジェクト

このプロジェクトは、住宅価格予測のためのMLOpsパイプラインを「データウェアハウス構築」から「特徴量エンジニアリング」「アンサンブル学習」「API/フロントエンド公開」まで一気通貫で体験できる学習用リポジトリです。

- **データ基盤**: DuckDB DWH
- **MLパイプライン**: scikit-learn, XGBoost, アンサンブル（Voting/Stacking）
- **実験管理**: MLflow
- **API/フロント**: FastAPI, Streamlit
- **CI/CD**: GitHub Actions
- **最高精度**: Stacking Ensemble（MAE: 10,858, R²: 0.9929）

---

## 🚀 クイックスタート

```bash
make venv
make install
make dwh
make train-ensemble
make check-ensemble
```

- WSL2/Python3.11+推奨
- 依存関係・コマンドはMakefileで一元管理
- 詳細は下記「トラブルシューティング」参照

---

## 📦 プロジェクト構成

```
mlops/fullstack-mlops/
├── Makefile                # 便利コマンド集
├── requirements.txt        # 依存関係
├── README.md               # このファイル
├── src/
│   ├── configs/            # モデル設定YAML
│   ├── ml/
│   │   ├── data/           # データ処理・DWH
│   │   ├── features/       # 特徴量エンジニアリング
│   │   ├── models/         # モデル訓練・アンサンブル
│   │   └── pipeline/       # パイプライン統合
│   ├── services/
│   │   ├── api/            # FastAPIサーバ
│   │   └── ui/             # Streamlitフロント
│   └── tests/              # テスト
├── deployment/             # MLflow, K8s等
└── models/trained/         # 訓練済みモデル
```

---

## 🏗️ パイプライン全体像

1. **データウェアハウス構築**（DuckDB）
2. **データ前処理・特徴量エンジニアリング**
3. **モデル訓練（単体/アンサンブル）**
4. **MLflowによる実験管理・モデル登録**
5. **API/フロントエンド公開（FastAPI/Streamlit）**
6. **CI/CD自動化（GitHub Actions）**

---

## 📊 モデル性能比較（2025年6月時点）

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

## 🧩 各ステップ詳細

### 1. データウェアハウス（DWH）構築
- `make dwh` でDuckDBベースのDWHを自動構築
- 地域・状態・築年数などのディメンション設計済み
- SQL/CLI/Pythonから分析可能

### 2. データ前処理・特徴量エンジニアリング
- 欠損値補完・外れ値除去・新規特徴量生成（面積単価・部屋比率など）
- `src/ml/features/engineer.py`で自動化

### 3. モデル訓練・アンサンブル
- `make train-ensemble` でVoting/Stackingアンサンブルを一発訓練
- 単体モデル（RandomForest, XGBoost, GradientBoosting）も比較
- 訓練済みモデルは`src/ml/models/trained/`に保存

### 4. MLflowによる実験管理
- `deployment/mlflow/docker-compose.yaml`でMLflowサーバ起動
- すべての訓練・評価結果を自動記録
- Web UIで履歴・パラメータ・メトリクス・モデル管理

### 5. API/フロントエンド公開
- `docker-compose up`でFastAPI（:8000）・Streamlit（:8501）を同時起動
- FastAPI: `/predict`エンドポイントで推論API
- Streamlit: Web UIでインタラクティブ予測

### 6. CI/CD自動化
- GitHub Actionsでテスト・訓練・リリース自動化
- `Makefile`でローカル開発も効率化

---

## 🛠️ 主要コマンド一覧（Makefile）

| コマンド                | 説明 |
|------------------------|------|
| `make venv`            | 仮想環境作成 |
| `make install`         | 依存関係インストール |
| `make dwh`             | DWH構築・データ投入 |
| `make train-ensemble`  | アンサンブルモデル訓練 |
| `make check-ensemble`  | アンサンブルモデル性能確認 |
| `make test`            | テスト実行 |
| `make lint`            | コード品質チェック |
| `make pipeline`        | 全パイプライン実行 |
| `make status`          | 状態確認 |

---

## 🌐 API/フロントエンドの使い方

### FastAPI
- `http://localhost:8000/docs` でAPIドキュメント
- サンプルリクエスト：
```bash
curl -X POST "http://localhost:8000/predict" \
-H "Content-Type: application/json" \
-d '{"sqft": 1500, "bedrooms": 3, "bathrooms": 2, "location": "suburban", "year_built": 2000, "condition": "fair"}'
```

### Streamlit
- `http://localhost:8501` でWeb UI
- 入力フォームからインタラクティブに予測

---

## 📈 MLflowによる実験管理
- `docker-compose -f deployment/mlflow/docker-compose.yaml up -d` でMLflowサーバ起動
- `http://localhost:5555` でWeb UIアクセス
- すべての訓練・評価・モデルバージョンを一元管理

---

## 🔄 CI/CDパイプライン
- GitHub Actionsで自動テスト・訓練・リリース
- mainブランチpushで全自動実行
- `.github/workflows/` 配下にワークフロー定義

---

## ⚠️ トラブルシューティング・FAQ

- **依存関係エラー**: Python3.12対応済み。`requirements.txt`のバージョンを確認
- **WSL2でのポート問題**: `localhost`でアクセス不可な場合はWSL2のIPアドレスを使用
- **MLflow/モデルファイルが見つからない**: `make train-ensemble`で再訓練
- **Docker/CLI/MLflowの詳細FAQ**: README内該当セクション参照

---

## 🤝 貢献・ライセンス

- Issue・PR・提案歓迎！
- ライセンス: MIT

---

ハッピーMLOps！