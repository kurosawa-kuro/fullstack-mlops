# ML Model CI/CD Makefile
# 開発者体験向上のための便利コマンド集

.PHONY: help install test lint format clean train train-force pipeline pipeline-quick release setup-dev check-model status venv dwh dwh-explore dwh-backup dwh-stats dwh-cli dwh-tables dwh-summary dwh-location dwh-condition dwh-price-range dwh-year-built dwh-unlock

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
	@echo "🗄️ DuckDB DWH関連:"
	@echo "  dwh            - DWH構築とデータインジェスション"
	@echo "  dwh-force      - DWH強制再構築"
	@echo "  dwh-explore    - DWHデータの探索・分析"
	@echo "  dwh-backup     - DWHデータベースのバックアップ"
	@echo "  dwh-stats      - DWH統計情報表示"
	@echo "  dwh-cli        - DuckDB CLI起動"
	@echo "  dwh-tables     - DWHテーブル一覧表示"
	@echo "  dwh-summary    - DWHサマリー統計表示"
	@echo "  dwh-location   - DWH地域別分析表示"
	@echo "  dwh-condition  - DWH状態別分析表示"
	@echo "  dwh-price-range - DWH価格帯別分析表示"
	@echo "  dwh-year-built - DWH築年数別分析表示"
	@echo "  dwh-unlock     - DWHロック解除"
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
		.venv/bin/pytest src/tests/ -v --cov=src --cov-report=html; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'python3 -m venv .venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ テスト完了"

# コード品質チェック
lint:
	@echo "🔍 コード品質チェック中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/flake8 src/ src/tests/ --count --select=E9,F63,F7,F82 --show-source --statistics; \
		.venv/bin/flake8 src/ src/tests/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics; \
		.venv/bin/mypy src/ src/tests/; \
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
		.venv/bin/black src/ src/tests/; \
		.venv/bin/isort src/ src/tests/; \
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
		.venv/bin/python src/ml/pipeline/train_pipeline.py --data-dir src/ml/data --models-dir src/ml/models; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'python3 -m venv .venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ モデル訓練完了"

# モデル強制再訓練
train-force:
	@echo "🔧 モデル強制再訓練中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python src/ml/pipeline/train_pipeline.py --force-retrain --data-dir src/ml/data --models-dir src/ml/models; \
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
	@ls -la src/configs/model_config.yaml 2>/dev/null || echo "❌ src/configs/model_config.yaml が見つかりません"
	@ls -la src/ml/data/raw/house_data.csv 2>/dev/null || echo "❌ src/ml/data/raw/house_data.csv が見つかりません"
	@ls -la src/ml/models/trained/house_price_prediction.pkl 2>/dev/null || echo "❌ 学習済みモデルが見つかりません"
	@ls -la src/ml/models/trained/preprocessor.pkl 2>/dev/null || echo "❌ 前処理器が見つかりません"
	@echo ""
	@echo "🗄️ DWH状態:"
	@ls -la src/ml/data/dwh/house_price_dwh.duckdb 2>/dev/null || echo "❌ DWHデータベースが見つかりません"
	@echo "✅ 状態確認完了"

# DWH構築とデータインジェスション
dwh:
	@echo "🗄️ DWH構築とデータインジェスション中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python src/ml/data/dwh/setup_dwh.py --csv-file src/ml/data/raw/house_data.csv; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'python3 -m venv .venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ DWH構築完了"

# DWH強制再構築
dwh-force:
	@echo "🗄️ DWH強制再構築中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python src/ml/data/dwh/setup_dwh.py --csv-file src/ml/data/raw/house_data.csv --force-schema; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'python3 -m venv .venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ DWH強制再構築完了"

# DWHデータの探索・分析
dwh-explore:
	@echo "🔍 DWHデータの探索・分析中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python src/ml/data/dwh/explore_dwh.py; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'python3 -m venv .venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ DWH探索完了"

# DWHデータベースのバックアップ
dwh-backup:
	@echo "💾 DWHデータベースのバックアップ中..."
	@mkdir -p src/ml/data/dwh/backups
	@DATE=$$(date +%Y%m%d_%H%M%S); \
	if [ -f "src/ml/data/dwh/house_price_dwh.duckdb" ]; then \
		cp src/ml/data/dwh/house_price_dwh.duckdb src/ml/data/dwh/backups/house_price_dwh_$$DATE.duckdb; \
		echo "✅ バックアップ完了: house_price_dwh_$$DATE.duckdb"; \
		ls -lh src/ml/data/dwh/backups/house_price_dwh_$$DATE.duckdb; \
	else \
		echo "❌ DWHデータベースが見つかりません。先に 'make dwh' を実行してください"; \
		exit 1; \
	fi

# DWH統計情報表示
dwh-stats:
	@echo "📊 DWH統計情報表示中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python -c "import duckdb; import os; db_path='src/ml/data/dwh/house_price_dwh.duckdb'; \
		if os.path.exists(db_path): \
			con = duckdb.connect(db_path); \
			result = con.execute('SELECT COUNT(*) FROM fact_house_transactions').fetchone(); \
			print(f'📈 総レコード数: {result[0]:,}'); \
			stats = con.execute('SELECT * FROM v_summary_statistics').fetchone(); \
			print(f'💰 平均価格: $${stats[1]:,.2f}'); \
			print(f'📏 平均面積: {stats[5]:,.0f} sqft'); \
			con.close(); \
		else: \
			print('❌ DWHデータベースが見つかりません'); \
		"; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'python3 -m venv .venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ DWH統計情報表示完了"

# DWH CLI起動
dwh-cli:
	@echo "🗄️ DuckDB CLIを起動中..."
	@if [ -f "src/ml/data/dwh/house_price_dwh.duckdb" ]; then \
		echo "📝 利用可能なコマンド:"; \
		echo "  .tables                    # テーブル一覧表示"; \
		echo "  .schema                    # スキーマ表示"; \
		echo "  SELECT * FROM v_summary_statistics;  # サマリー統計"; \
		echo "  .quit                      # 終了"; \
		echo ""; \
		duckdb src/ml/data/dwh/house_price_dwh.duckdb; \
	else \
		echo "❌ DWHデータベースが見つかりません。先に 'make dwh' を実行してください"; \
		exit 1; \
	fi

# DWHテーブル一覧表示
dwh-tables:
	@echo "📋 DWHテーブル一覧表示中..."
	@if [ -f "src/ml/data/dwh/house_price_dwh.duckdb" ]; then \
		duckdb src/ml/data/dwh/house_price_dwh.duckdb ".tables"; \
	else \
		echo "❌ DWHデータベースが見つかりません。先に 'make dwh' を実行してください"; \
		exit 1; \
	fi

# DWHサマリー統計表示
dwh-summary:
	@echo "📊 DWHサマリー統計表示中..."
	@if [ -f "src/ml/data/dwh/house_price_dwh.duckdb" ]; then \
		duckdb src/ml/data/dwh/house_price_dwh.duckdb "SELECT * FROM v_summary_statistics;"; \
	else \
		echo "❌ DWHデータベースが見つかりません。先に 'make dwh' を実行してください"; \
		exit 1; \
	fi

# DWH地域別分析表示
dwh-location:
	@echo "📍 DWH地域別分析表示中..."
	@if [ -f "src/ml/data/dwh/house_price_dwh.duckdb" ]; then \
		duckdb src/ml/data/dwh/house_price_dwh.duckdb "SELECT * FROM v_location_analytics ORDER BY avg_price DESC;"; \
	else \
		echo "❌ DWHデータベースが見つかりません。先に 'make dwh' を実行してください"; \
		exit 1; \
	fi

# DWH状態別分析表示
dwh-condition:
	@echo "🏠 DWH状態別分析表示中..."
	@if [ -f "src/ml/data/dwh/house_price_dwh.duckdb" ]; then \
		duckdb src/ml/data/dwh/house_price_dwh.duckdb "SELECT * FROM v_condition_analytics ORDER BY avg_price DESC;"; \
	else \
		echo "❌ DWHデータベースが見つかりません。先に 'make dwh' を実行してください"; \
		exit 1; \
	fi

# DWH価格帯別分析表示
dwh-price-range:
	@echo "💰 DWH価格帯別分析表示中..."
	@if [ -f "src/ml/data/dwh/house_price_dwh.duckdb" ]; then \
		duckdb src/ml/data/dwh/house_price_dwh.duckdb "SELECT CASE WHEN price < 300000 THEN 'Under $300k' WHEN price < 500000 THEN '$300k-$500k' WHEN price < 800000 THEN '$500k-$800k' ELSE 'Over $800k' END as price_range, COUNT(*) as house_count, AVG(price) as avg_price FROM fact_house_transactions GROUP BY price_range ORDER BY MIN(price);"; \
	else \
		echo "❌ DWHデータベースが見つかりません。先に 'make dwh' を実行してください"; \
		exit 1; \
	fi

# DWH築年数別分析表示
dwh-year-built:
	@echo "🏗️ DWH築年数別分析表示中..."
	@if [ -f "src/ml/data/dwh/house_price_dwh.duckdb" ]; then \
		duckdb src/ml/data/dwh/house_price_dwh.duckdb "SELECT y.decade, AVG(h.price) as avg_price, COUNT(*) as house_count FROM fact_house_transactions h JOIN dim_years y ON h.year_built_id = y.year_id GROUP BY y.decade ORDER BY y.decade;"; \
	else \
		echo "❌ DWHデータベースが見つかりません。先に 'make dwh' を実行してください"; \
		exit 1; \
	fi

# DWHロック解除
dwh-unlock:
	@echo "🔓 DWHロック解除中..."
	@echo "📋 既存のDuckDBプロセスを確認中..."
	@ps aux | grep duckdb | grep -v grep || echo "✅ DuckDBプロセスが見つかりません"
	@echo "🔄 ユーザープロセスを終了中..."
	@-pkill -f duckdb 2>/dev/null || true
	@echo "✅ ユーザープロセス終了処理完了"
	@echo "🔄 Pythonプロセスを終了中..."
	@-pkill -f python.*duckdb 2>/dev/null || true
	@echo "✅ Pythonプロセス終了処理完了"
	@echo "✅ DWHロック解除完了"
	@echo "📝 再度 'make dwh-tables' などを実行してください" 