# ML Model CI/CD Makefile
# 開発者体験向上のための便利コマンド集

.PHONY: help install test lint format clean train train-force pipeline pipeline-quick release setup-dev check-model status venv

# デフォルトターゲット
help:
	@echo "🏠 House Price Prediction ML Pipeline"
	@echo ""
	@echo "利用可能なコマンド:"
	@echo "  venv           - 仮想環境を作成・アクティベート"
	@echo "  install        - 依存関係をインストール"
	@echo "  test           - テストを実行"
	@echo "  lint           - コード品質チェック"
	@echo "  format         - コードフォーマット"
	@echo "  clean          - 一時ファイルを削除"
	@echo "  train          - モデルを訓練（既存モデルがあればスキップ）"
	@echo "  train-force    - モデルを強制再訓練"
	@echo "  pipeline       - 全パイプラインを実行"
	@echo "  pipeline-quick - 既存モデルがあればスキップしてパイプライン実行"
	@echo "  release        - リリース用タグを作成"
	@echo "  check-model    - モデル性能確認"
	@echo "  status         - パイプライン状態確認"
	@echo ""

# 仮想環境セットアップ
venv:
	@echo "🐍 仮想環境を作成中..."
	@if [ ! -d ".venv" ]; then \
		python3 -m venv .venv; \
		echo "✅ 仮想環境を作成しました"; \
	else \
		echo "✅ 仮想環境は既に存在します"; \
	fi
	@echo "📝 仮想環境をアクティベートするには: source .venv/bin/activate"
	@echo "📝 または、make install を実行して依存関係をインストールしてください"

# 依存関係インストール
install:
	@echo "📦 依存関係をインストール中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/pip install -r requirements.txt; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'python3 -m venv .venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ インストール完了"

# テスト実行
test:
	@echo "🧪 テストを実行中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/pytest tests/ -v --cov=src --cov-report=html; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'python3 -m venv .venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ テスト完了"

# コード品質チェック
lint:
	@echo "🔍 コード品質チェック中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics; \
		.venv/bin/flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics; \
		.venv/bin/mypy src/ tests/; \
		.venv/bin/bandit -r src/ --severity-level high; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'python3 -m venv .venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ コード品質チェック完了"

# コードフォーマット
format:
	@echo "🎨 コードフォーマット中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/black src/ tests/; \
		.venv/bin/isort src/ tests/; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'python3 -m venv .venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ フォーマット完了"

# 一時ファイル削除
clean:
	@echo "🧹 一時ファイルを削除中..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "✅ クリーンアップ完了"

# モデル訓練（既存モデルがあればスキップ）
train:
	@echo "🔧 モデル訓練中（既存モデルがあればスキップ）..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python src/ml/pipeline/train_pipeline.py; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'python3 -m venv .venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ モデル訓練完了"

# モデル強制再訓練
train-force:
	@echo "🔧 モデル強制再訓練中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python src/ml/pipeline/train_pipeline.py --force-retrain; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'python3 -m venv .venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ モデル強制再訓練完了"

# 全パイプライン実行
pipeline: clean install lint test train
	@echo "🚀 全パイプライン実行完了"

# クイックパイプライン実行（既存モデルがあればスキップ）
pipeline-quick: clean install lint test train
	@echo "⚡ クイックパイプライン実行完了"

# リリース用タグ作成
release:
	@echo "🏷️ リリース用タグを作成中..."
	@read -p "バージョン番号を入力してください (例: v1.0.0): " version; \
	git tag -a $$version -m "Release $$version"; \
	git push origin $$version; \
	echo "✅ リリースタグ $$version を作成しました"

# 開発環境セットアップ
setup-dev: install
	@echo "🔧 開発環境セットアップ中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/pre-commit install; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'python3 -m venv .venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ 開発環境セットアップ完了"

# モデル性能確認
check-model:
	@echo "📊 モデル性能確認中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python -c "import joblib; import pandas as pd; model = joblib.load('src/ml/models/trained/house_price_prediction.pkl'); preprocessor = joblib.load('src/ml/models/trained/preprocessor.pkl'); print('✅ モデル読み込み成功'); sample_data = pd.DataFrame({'sqft': [1500], 'bedrooms': [3], 'bathrooms': [2], 'year_built': [2010], 'location': ['Suburban'], 'condition': ['Good']}); X_transformed = preprocessor.transform(sample_data); prediction = model.predict(X_transformed); print(f'📈 サンプル予測結果: $${prediction[0]:,.2f}')"; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'python3 -m venv .venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ モデル性能確認完了"

# パイプライン状態確認
status:
	@echo "📋 パイプライン状態確認中..."
	@echo "📁 必要なファイル:"
	@ls -la configs/model_config.yaml 2>/dev/null || echo "❌ configs/model_config.yaml が見つかりません"
	@ls -la src/ml/data/raw/house_data.csv 2>/dev/null || echo "❌ src/ml/data/raw/house_data.csv が見つかりません"
	@ls -la src/ml/models/trained/house_price_prediction.pkl 2>/dev/null || echo "❌ 学習済みモデルが見つかりません"
	@ls -la src/ml/models/trained/preprocessor.pkl 2>/dev/null || echo "❌ 前処理器が見つかりません"
	@echo "✅ 状態確認完了" 