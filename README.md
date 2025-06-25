# 🏠 House Price Predictor – エンドツーエンドMLOpsプロジェクト

このプロジェクトは、住宅価格予測のためのMLOpsパイプラインを「データウェアハウス構築」から「特徴量エンジニアリング」「アンサンブル学習」「API/フロントエンド公開」まで一気通貫で体験できる学習用リポジトリです。

- **データ基盤**: DuckDB DWH
- **MLパイプライン**: scikit-learn, XGBoost, アンサンブル（Voting/Stacking）
- **実験管理**: MLflow
- **API/フロント**: FastAPI, Streamlit
- **CI/CD**: GitHub Actions（DuckDB対応）
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
│   │   │   └── dwh/        # DuckDB DWH関連
│   │   ├── features/       # 特徴量エンジニアリング
│   │   ├── models/         # モデル訓練・アンサンブル
│   │   └── pipeline/       # パイプライン統合
│   ├── services/
│   │   ├── api/            # FastAPIサーバ
│   │   └── ui/             # Streamlitフロント
│   └── tests/              # テスト
├── deployment/             # MLflow, K8s等
├── models/trained/         # 訓練済みモデル
└── .github/workflows/      # CI/CDワークフロー
```

---

## 🏗️ パイプライン全体像

1. **データウェアハウス構築**（DuckDB）
2. **データ前処理・特徴量エンジニアリング**
3. **モデル訓練（単体/アンサンブル）**
4. **MLflowによる実験管理・モデル登録**
5. **API/フロントエンド公開（FastAPI/Streamlit）**
6. **CI/CD自動化（GitHub Actions - DuckDB対応）**

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

### 6. CI/CD自動化（DuckDB対応）
- GitHub Actionsでテスト・DWH構築・訓練・リリース自動化
- DuckDBベースのデータウェアハウス構築からモデル訓練まで一気通貫
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

## 🔄 CI/CDパイプライン（DuckDB対応）

### ワークフロー概要
GitHub Actionsで自動テスト・DWH構築・訓練・リリースを実行します。

### 実行トリガー
- **Push**: 全ブランチへのプッシュ
- **Pull Request**: 全ブランチへのPR
- **手動実行**: workflow_dispatchで手動実行可能

### ジョブ構成

#### 1. コード品質チェック（code-quality）
- **Black**: コードフォーマットチェック
- **flake8**: リンター
- **bandit**: セキュリティチェック

#### 2. モデル訓練（train-model）
- **DuckDB DWH構築**: サンプルデータでDWHを構築
- **モデル訓練**: DuckDBベースのモデル訓練
- **アーティファクト保存**: モデル・DWHファイルを保存

#### 3. テスト実行（test）
- **アーティファクト取得**: 訓練済みモデル・DWHファイルを取得
- **テスト実行**: pytestでテスト実行
- **カバレッジ**: Codecovにカバレッジレポート送信

#### 4. モデル性能テスト（model-performance）
- **統合テスト**: DuckDBとモデルの統合テスト
- **性能確認**: モデルファイルサイズ・DWHサイズ確認

#### 5. リリース作成（create-release）
- **タグプッシュ時**: 自動でGitHub Release作成
- **アーティファクト添付**: モデル・DWHファイルをリリースに添付

### DuckDB対応の特徴
- **データソース**: CSV → DuckDB DWHに変更
- **DWH構築**: 自動でDuckDBデータウェアハウスを構築
- **モデル訓練**: DuckDBから直接データを読み込み
- **テスト**: DuckDB統合テストを実行
- **アーティファクト**: モデルとDWHファイルを保存

### テスト戦略
- **スキップ機能**: ファイルが存在しない場合はテストをスキップ
- **統合テスト**: DuckDBとモデルの統合動作確認
- **カバレッジ**: コードカバレッジの測定と報告

### 設定ファイル対応
- **base_models**: アンサンブル用の基本モデル設定
- **ensemble**: アンサンブル手法の設定
- **training**: 訓練パラメータの設定

---

## 🐛 トラブルシューティング

### よくある問題と解決方法

#### 1. 依存関係エラー
```bash
# 仮想環境を再作成
make clean
make venv
make install
```

#### 2. DuckDB DWHエラー
```bash
# DWHを再構築
make clean-dwh
make dwh
```

#### 3. モデル訓練エラー
```bash
# モデルディレクトリをクリアして再訓練
rm -rf src/ml/models/trained/*
make train-ensemble
```

#### 4. CI/CDエラー
- **ブランチ制限**: 全ブランチでCIが実行されるように設定済み
- **テスト失敗**: ファイルが存在しない場合はスキップ機能あり
- **設定ファイル**: base_models, ensemble, trainingセクションが必須

#### 5. コード品質エラー
```bash
# 自動整形
make format
# リンター実行
make lint
```

---

## 📝 開発ガイドライン

### コード品質
- **Black**: コードフォーマット
- **flake8**: リンター
- **bandit**: セキュリティチェック

### テスト
- **pytest**: テストフレームワーク
- **カバレッジ**: コードカバレッジ測定
- **統合テスト**: DuckDBとモデルの統合テスト

### CI/CD
- **自動化**: プッシュ・PRで自動実行
- **アーティファクト**: モデル・DWHファイルの保存
- **リリース**: タグプッシュで自動リリース

---

## 🤝 コントリビューション

1. フォークしてブランチを作成
2. 変更をコミット
3. プルリクエストを作成
4. CI/CDが自動でテスト・訓練を実行

---

## 📄 ライセンス

MIT License

---

## 🙏 謝辞

- DuckDB開発チーム
- scikit-learn開発チーム
- MLflow開発チーム
- FastAPI開発チーム
- Streamlit開発チーム