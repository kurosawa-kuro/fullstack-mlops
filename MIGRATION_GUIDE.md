# 🔄 リファクタリング移行ガイド

このガイドでは、既存のプロジェクト構造から新しいリファクタリング版への移行手順を説明します。

## 📋 移行概要

### 移行前後の主な変更点

| 項目 | 移行前 | 移行後 |
|------|--------|--------|
| 設定管理 | 分散した設定ファイル | 統一された設定管理（`src/core/config.py`） |
| ログ | 標準logging | 構造化ログ（`src/core/logging.py`） |
| 例外処理 | 標準例外 | カスタム例外（`src/core/exceptions.py`） |
| 依存関係 | 単一requirements.txt | 環境別分離（dev/prod） |
| テスト | 単一ディレクトリ | 階層化（unit/integration/e2e） |
| プロジェクト構造 | フラット | レイヤー分離 |

## 🚀 段階的移行手順

### Phase 1: 準備作業

#### 1.1 バックアップ作成
```bash
# 現在のプロジェクトをバックアップ
cp -r mlops/fullstack-mlops mlops/fullstack-mlops.backup
```

#### 1.2 新しいディレクトリ構造作成
```bash
# 新しいディレクトリ構造を作成
mkdir -p src/core
mkdir -p src/data/{dwh,ingestion,validation}
mkdir -p src/features
mkdir -p src/models/{base,ensemble,training,inference}
mkdir -p src/services/{api,ui,monitoring}
mkdir -p src/mlflow
mkdir -p tests/{unit,integration,e2e,fixtures}
mkdir -p configs/environments
mkdir -p deployment/{docker,kubernetes,terraform,scripts}
mkdir -p docs/diagrams
mkdir -p scripts
```

### Phase 2: コア機能移行

#### 2.1 設定管理移行
```bash
# 新しい設定ファイルをコピー
cp PROJECT_STRUCTURE.md ./
cp configs/app.yaml ./
cp src/core/config.py ./
cp src/core/logging.py ./
cp src/core/exceptions.py ./
```

#### 2.2 依存関係分離
```bash
# 新しい依存関係ファイルをコピー
cp requirements-dev.txt ./
cp requirements-prod.txt ./
```

#### 2.3 Makefile更新
```bash
# 新しいMakefileをコピー
cp Makefile.refactored ./Makefile
```

### Phase 3: コード移行

#### 3.1 データ層移行
```bash
# 既存のデータ処理コードを新しい構造に移行
# src/ml/data/ → src/data/
```

#### 3.2 モデル層移行
```bash
# 既存のモデルコードを新しい構造に移行
# src/ml/models/ → src/models/
```

#### 3.3 サービス層移行
```bash
# 既存のサービスコードを新しい構造に移行
# src/services/ → src/services/
```

### Phase 4: テスト移行

#### 4.1 テスト構造化
```bash
# 既存のテストを新しい構造に移行
# tests/ → tests/unit/
# 統合テストを tests/integration/ に移動
# E2Eテストを tests/e2e/ に移動
```

### Phase 5: 設定更新

#### 5.1 環境変数設定
```bash
# .env.example を作成
cp .env.example .env
# 環境変数を設定
```

#### 5.2 設定ファイル更新
```bash
# 既存の設定を新しい形式に変換
python scripts/migrate_config.py
```

## 🔧 移行スクリプト

### 設定移行スクリプト
```python
# scripts/migrate_config.py
import yaml
import json
from pathlib import Path

def migrate_config():
    """既存の設定を新しい形式に移行"""
    
    # 既存の設定ファイルを読み込み
    old_configs = {
        'base_models': Path('src/configs/base_models.yaml'),
        'ensemble': Path('src/configs/ensemble.yaml'),
        'training': Path('src/configs/training.yaml')
    }
    
    # 新しい設定ファイルを作成
    new_config = {}
    
    for name, path in old_configs.items():
        if path.exists():
            with open(path, 'r') as f:
                config_data = yaml.safe_load(f)
                new_config[name] = config_data
    
    # 新しい設定ファイルに保存
    with open('configs/app.yaml', 'w') as f:
        yaml.dump(new_config, f, default_flow_style=False)
    
    print("✅ 設定移行完了")

if __name__ == "__main__":
    migrate_config()
```

### コード移行スクリプト
```python
# scripts/migrate_code.py
import shutil
from pathlib import Path

def migrate_code():
    """既存のコードを新しい構造に移行"""
    
    # データ層移行
    if Path('src/ml/data').exists():
        shutil.move('src/ml/data', 'src/data')
    
    # モデル層移行
    if Path('src/ml/models').exists():
        shutil.move('src/ml/models', 'src/models')
    
    # 特徴量移行
    if Path('src/ml/features').exists():
        shutil.move('src/ml/features', 'src/features')
    
    # パイプライン移行
    if Path('src/ml/pipeline').exists():
        shutil.move('src/ml/pipeline', 'src/pipeline')
    
    print("✅ コード移行完了")

if __name__ == "__main__":
    migrate_code()
```

## 🧪 移行後のテスト

### 1. 基本動作確認
```bash
# 新しいセットアップ
make setup-dev

# 基本テスト
make test-unit

# コード品質チェック
make lint
make type-check
```

### 2. 機能テスト
```bash
# DWH構築
make dwh

# モデル訓練
make train-ensemble

# 性能確認
make check-model
```

### 3. 統合テスト
```bash
# 統合テスト
make test-integration

# E2Eテスト
make test-e2e
```

## 🔍 移行チェックリスト

### 設定関連
- [ ] `configs/app.yaml` が正しく設定されている
- [ ] 環境変数が適切に設定されている
- [ ] 設定管理クラスが正常に動作する

### ログ関連
- [ ] 構造化ログが正常に出力される
- [ ] ログローテーションが機能する
- [ ] ログレベルが適切に設定されている

### 例外処理
- [ ] カスタム例外が適切に定義されている
- [ ] 例外ハンドラーが正常に動作する
- [ ] エラーレスポンスが適切に返される

### 依存関係
- [ ] 開発用依存関係が正しくインストールされる
- [ ] 本番用依存関係が正しくインストールされる
- [ ] 依存関係の競合がない

### テスト
- [ ] 単体テストが正常に実行される
- [ ] 統合テストが正常に実行される
- [ ] E2Eテストが正常に実行される
- [ ] テストカバレッジが適切に測定される

### ビルド・デプロイ
- [ ] Makefileが正常に動作する
- [ ] Dockerビルドが成功する
- [ ] CI/CDパイプラインが正常に動作する

## 🚨 注意事項

### 1. 後方互換性
- 既存のAPIエンドポイントは維持
- 既存の設定ファイルは段階的に移行
- 既存のデータベース構造は変更しない

### 2. 段階的移行
- 一度に全てを移行せず、段階的に実施
- 各段階でテストを実行
- 問題が発生した場合はロールバック可能

### 3. チーム連携
- 移行計画をチームで共有
- 移行中の作業分担を明確化
- 移行完了後の確認を実施

## 🔄 ロールバック手順

### 緊急時ロールバック
```bash
# バックアップから復元
rm -rf mlops/fullstack-mlops
cp -r mlops/fullstack-mlops.backup mlops/fullstack-mlops

# 依存関係を再インストール
cd mlops/fullstack-mlops
make install
```

### 部分ロールバック
```bash
# 特定のファイルのみ復元
cp mlops/fullstack-mlops.backup/src/ml/models/train_model.py src/ml/models/
cp mlops/fullstack-mlops.backup/Makefile ./
```

## 📞 サポート

### 移行中の問題
- [GitHub Issues](https://github.com/your-repo/issues) で問題報告
- [GitHub Discussions](https://github.com/your-repo/discussions) で質問・議論

### ドキュメント
- [アーキテクチャドキュメント](./docs/architecture.md)
- [開発ガイド](./docs/development.md)
- [トラブルシューティング](./docs/troubleshooting.md)

## 🎯 移行完了後の次のステップ

### 1. パフォーマンス最適化
- プロファイリング実行
- ボトルネック特定
- 最適化実施

### 2. 監視・アラート強化
- メトリクス収集強化
- アラート設定
- ダッシュボード作成

### 3. セキュリティ強化
- セキュリティスキャン
- 脆弱性修正
- セキュリティテスト

### 4. ドキュメント更新
- API仕様書更新
- アーキテクチャ図更新
- 運用ドキュメント更新 