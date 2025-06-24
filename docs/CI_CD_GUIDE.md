# 🚀 MLモデル CI/CD ガイド

このドキュメントでは、House Price PredictionプロジェクトのCI/CDパイプラインの使用方法と構成について説明します。

## 📋 概要

このCI/CDパイプラインは以下の機能を提供します：

- ✅ **自動コード品質チェック** (lint, format, type check)
- ✅ **自動テスト実行** (unit tests, model validation)
- ✅ **自動モデル訓練** (データ処理 → 特徴量エンジニアリング → モデル訓練)
- ✅ **自動成果物管理** (GitHub Artifacts, Releases)
- ✅ **モデル性能監視** (予測テスト, ファイル整合性チェック)

## 🏗️ パイプライン構成

### 1. コード品質チェック (code-quality)
```yaml
- Black (コードフォーマット)
- isort (インポート整理)
- flake8 (リント)
- mypy (型チェック)
- bandit (セキュリティチェック)
```

### 2. テスト実行 (test)
```yaml
- pytest (ユニットテスト)
- カバレッジレポート生成
- Codecov連携
```

### 3. モデル訓練 (train-model)
```yaml
- データ処理 (src/ml/data/run_processing.py)
- 特徴量エンジニアリング (src/ml/features/engineer.py)
- モデル訓練 (src/ml/models/train_model.py)
- 成果物アップロード (GitHub Artifacts)
```

### 4. モデル性能テスト (model-performance)
```yaml
- モデル読み込みテスト
- 予測実行テスト
- ファイルサイズ確認
```

### 5. リリース作成 (create-release)
```yaml
- GitHub Release自動作成
- モデルファイル添付
- リリースノート生成
```

## 🚀 使用方法

### ローカル開発

#### 1. 依存関係インストール
```bash
make install
# または
pip install -r requirements.txt
```

#### 2. コード品質チェック
```bash
make lint
```

#### 3. コードフォーマット
```bash
make format
```

#### 4. テスト実行
```bash
make test
```

#### 5. モデル訓練
```bash
make train
# または
python src/ml/pipeline/train_pipeline.py
```

#### 6. 全パイプライン実行
```bash
make pipeline
```

### GitHub Actions

#### 自動実行
- **push to main/develop**: コード品質チェック + テスト
- **push to main**: モデル訓練 + 性能テスト
- **tag push**: GitHub Release作成

#### 手動実行
1. GitHubリポジトリの "Actions" タブに移動
2. "ML Model CI/CD" ワークフローを選択
3. "Run workflow" ボタンをクリック

## 📦 成果物管理

### GitHub Artifacts
- **trained-models**: 学習済みモデルと前処理器
- **processed-data**: 処理済みデータセット
- **retention-days**: 30日間保存

### GitHub Releases
- タグプッシュ時に自動作成
- モデルファイル (.pkl) を添付
- リリースノート自動生成

## 🔧 設定ファイル

### model_config.yaml
```yaml
name: "house_price_prediction"
model:
  best_model: "RandomForest"
  parameters:
    n_estimators: 100
    max_depth: 10
    random_state: 42
```

### 環境変数
- `GITHUB_TOKEN`: GitHub API認証 (自動設定)

## 🧪 テスト構成

### test_model_pipeline.py
- モデルファイル存在確認
- モデル読み込みテスト
- 予測実行テスト
- 設定ファイル検証
- データファイル検証

## 📊 監視とアラート

### 成功条件
- ✅ すべてのテストが通過
- ✅ コード品質チェックが通過
- ✅ モデル訓練が成功
- ✅ 予測テストが成功

### 失敗時の対応
1. GitHub Actionsログを確認
2. ローカルで `make test` を実行
3. 必要に応じて `make format` を実行
4. 修正後に再プッシュ

## 🔄 ワークフロー例

### 通常の開発フロー
```bash
# 1. コード修正
vim src/ml/models/train_model.py

# 2. コード品質チェック
make lint

# 3. フォーマット
make format

# 4. テスト実行
make test

# 5. コミット・プッシュ
git add .
git commit -m "feat: improve model training"
git push origin main
```

### リリースフロー
```bash
# 1. バージョンタグ作成
make release
# バージョン番号を入力 (例: v1.0.0)

# 2. GitHub Releaseが自動作成される
# 3. モデルファイルが自動添付される
```

## 🛠️ トラブルシューティング

### よくある問題

#### 1. 依存関係エラー
```bash
# 解決方法
make clean
make install
```

#### 2. コード品質エラー
```bash
# 解決方法
make format
make lint
```

#### 3. テスト失敗
```bash
# 解決方法
make test  # 詳細なエラーを確認
```

#### 4. モデル訓練エラー
```bash
# 解決方法
make status  # ファイル存在確認
make train   # 再実行
```

### ログ確認
- GitHub Actions: リポジトリの "Actions" タブ
- ローカル: 各コマンドの出力を確認

## 📈 パフォーマンス最適化

### キャッシュ戦略
- pip依存関係キャッシュ
- テスト結果キャッシュ
- モデルアーティファクトキャッシュ

### 並列実行
- コード品質チェックとテストを並列実行
- モデル訓練と性能テストを並列実行

## 🔒 セキュリティ

### セキュリティチェック
- banditによるセキュリティリント
- 依存関係の脆弱性スキャン
- シークレット管理

### アクセス制御
- GitHub Actionsの権限最小化
- アーティファクトのアクセス制限
- リリースの承認プロセス

## 📞 サポート

問題が発生した場合は以下を確認してください：

1. **ログ**: GitHub Actionsの実行ログ
2. **ドキュメント**: このガイドとREADME
3. **テスト**: `make test` でローカル確認
4. **状態確認**: `make status` でファイル確認

---

**🎯 このCI/CDパイプラインにより、MLモデルの開発・訓練・配布が自動化され、品質と信頼性が向上します！** 