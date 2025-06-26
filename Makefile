# ML Model CI/CD Makefile (Refactored)
# 開発者体験向上のための便利コマンド集

.PHONY: help install install-dev install-prod test test-unit test-integration test-e2e format clean train train-force pipeline pipeline-quick release setup-dev check-model status venv dwh dwh-explore dwh-backup dwh-stats dwh-cli dwh-tables dwh-summary dwh-location dwh-condition dwh-price-range dwh-year-built dwh-unlock train-ensemble train-ensemble-voting train-ensemble-stacking check-ensemble ingest dbt train-dbt all metabase-full metabase-setup metabase-up metabase-down metabase-status metabase-logs metabase-check-connection metabase-dashboard-setup metabase-restart metabase-clean metabase-update-driver

# デフォルトターゲット
.DEFAULT_GOAL := help

# ヘルプ表示
help:
	@echo "🏠 House Price Prediction MLOps Pipeline"
	@echo ""
	@echo "📋 利用可能なコマンド:"
	@echo ""
	@echo "🔧 基本コマンド:"
	@echo "  make deps-dev                # 開発用依存関係インストール"
	@echo "  make deps-prod               # 本番用依存関係インストール"
	@echo "  make test-unit               # 単体テスト"
	@echo "  make test-integ              # 統合テスト"
	@echo "  make test-e2e                # E2Eテスト"
	@echo "  make format                  # コードフォーマット"
	@echo "  make clean                   # クリーンアップ"
	@echo ""
	@echo "🗄️ DWH関連:"
	@echo "  make dwh-bronze              # Bronze層データ取り込み"
	@echo "  make dwh-explore             # DWHデータ探索"
	@echo "  make dwh-stats               # DWH統計情報"
	@echo "  make dwh-tables              # DWHテーブル一覧"
	@echo "  make dwh-cli                 # DuckDB CLI起動"
	@echo "  make dwh-unlock              # DWHロック解除"
	@echo ""
	@echo "🛠️ dbt関連:"
	@echo "  make dbt-run                 # dbtでSilver/Gold層作成"
	@echo "  make dbt-train               # dbt学習スクリプト実行"
	@echo "  make dbt-docs                # dbtドキュメント生成"
	@echo ""
	@echo "🚀 パイプライン:"
	@echo "  make pipeline-all            # 一括実行（全パイプライン）"
	@echo "  make pipeline-quick          # クイックパイプライン"
	@echo ""
	@echo "📊 Metabase BI統合:"
	@echo "  make metabase-setup          # Metabaseセットアップ"
	@echo "  make metabase-up             # Metabase起動"
	@echo "  make metabase-down           # Metabase停止"
	@echo "  make metabase-status         # Metabase状態確認"
	@echo "  make metabase-logs           # Metabaseログ確認"
	@echo "  make metabase-check          # Metabase接続確認"
	@echo "  make metabase-dashboard      # ダッシュボード作成支援"
	@echo ""
	@echo "🔧 開発:"
	@echo "  make dev-setup               # 開発環境セットアップ"

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
deps-dev:
	@echo "📦 開発用依存関係インストール中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/pip install -r configs/requirements-dev.txt; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ 開発用依存関係インストール完了"

deps-prod:
	@echo "📦 本番用依存関係インストール中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/pip install -r configs/requirements-prod.txt; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ 本番用依存関係インストール完了"

# 全テスト実行
test: test-unit test-integ test-e2e
	@echo "✅ 全テスト実行完了"

# 単体テスト実行
test-unit:
	@echo "🧪 単体テスト実行中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/pytest tests/unit/ -v; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ 単体テスト実行完了"

# 統合テスト実行
test-integ:
	@echo "🔗 統合テスト実行中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/pytest tests/integration/ -v; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ 統合テスト実行完了"

# E2Eテスト実行
test-e2e:
	@echo "🌐 E2Eテスト実行中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/pytest tests/e2e/ -v; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ E2Eテスト実行完了"

# コードフォーマット
format:
	@echo "🎨 コードフォーマット中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/black src/ tests/; \
		.venv/bin/isort src/ tests/; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ コードフォーマット完了"

# 一時ファイル削除
clean:
	@echo "🧹 一時ファイルを削除中..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "✅ クリーンアップ完了"

# モデル訓練（既存モデルがあればスキップ）
train:
	@echo "🔧 モデル訓練中（既存モデルがあればスキップ）..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python src/ml/models/train_model.py \
			--config src/configs/model_config.yaml \
			--duckdb-path src/ml/data/dwh/data/house_price_dwh.duckdb \
			--models-dir src/ml/models \
			--view-name bronze_raw_house_data; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ モデル訓練完了"

# モデル強制再訓練
train-force:
	@echo "🔧 モデル強制再訓練中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python src/ml/models/train_model.py \
			--config src/configs/model_config.yaml \
			--duckdb-path src/ml/data/dwh/data/house_price_dwh.duckdb \
			--models-dir src/ml/models \
			--view-name bronze_raw_house_data \
			--force-retrain; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ モデル強制再訓練完了"

# 全パイプライン実行（lintスキップ）
pipeline: clean install test train
	@echo "🚀 全パイプライン実行完了"

# 一括実行（全パイプライン）
pipeline-all: clean deps-dev test dwh-bronze dbt train-dbt
	@echo "🚀 一括実行（全パイプライン）完了"

# クイックパイプライン実行（既存モデルがあればスキップ）
pipeline-quick: clean install test train
	@echo "⚡ クイックパイプライン実行完了"

# リリース用タグ作成
release:
	@echo "🏷️ リリース用タグを作成中..."
	@read -p "バージョン番号を入力してください (例: v1.0.0): " version; \
	git tag -a $$version -m "Release $$version"; \
	git push origin $$version; \
	echo "✅ リリースタグ $$version を作成しました"

# 開発環境セットアップ
setup-dev: dev-setup
	@echo "🔧 開発環境セットアップ中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/pre-commit install; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ 開発環境セットアップ完了"

# モデル性能確認
check-model:
	@echo "📊 モデル性能確認中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python test_model.py; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
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
	@ls -la src/ml/models/trained/house_price_prediction_encoders.pkl 2>/dev/null || echo "❌ 前処理器が見つかりません"
	@echo ""
	@echo "🗄️ DWH状態:"
	@ls -la src/ml/data/dwh/data/house_price_dwh.duckdb 2>/dev/null || echo "❌ DWHデータベースが見つかりません"
	@echo "✅ 状態確認完了"

# DWH構築とデータインジェスション
dwh-bronze:
	@echo "🗄️ DWH Bronze層データ取り込み中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python src/ml/data/dwh/scripts/setup_dwh.py --csv-file src/ml/data/raw/house_data.csv; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ DWH Bronze層データ取り込み完了"

# DWHデータの探索・分析
dwh-explore:
	@echo "🔍 DWHデータの探索・分析中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python src/ml/data/dwh/scripts/explore_dwh.py; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ DWH探索完了"

# DWHデータベースのバックアップ
dwh-backup:
	@echo "💾 DWHデータベースのバックアップ中..."
	@mkdir -p src/ml/data/dwh/data/backups
	@DATE=$$(date +%Y%m%d_%H%M%S); \
	if [ -f "src/ml/data/dwh/data/house_price_dwh.duckdb" ]; then \
		cp src/ml/data/dwh/data/house_price_dwh.duckdb src/ml/data/dwh/data/backups/house_price_dwh_$$DATE.duckdb; \
		echo "✅ バックアップ完了: house_price_dwh_$$DATE.duckdb"; \
		ls -lh src/ml/data/dwh/data/backups/house_price_dwh_$$DATE.duckdb; \
	else \
		echo "❌ DWHデータベースが見つかりません。先に 'make dwh-bronze' を実行してください"; \
		exit 1; \
	fi

# DWH統計情報表示
dwh-stats:
	@echo "📊 DWH統計情報表示中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python -c "import duckdb; import os; db_path='src/ml/data/dwh/data/house_price_dwh.duckdb'; \
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
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ DWH統計情報表示完了"

# DWH CLI起動
dwh-cli:
	@echo "🗄️ DuckDB CLIを起動中..."
	@if [ -f "src/ml/data/dwh/data/house_price_dwh.duckdb" ]; then \
		echo "📝 利用可能なコマンド:"; \
		echo "  .tables                    # テーブル一覧表示"; \
		echo "  .schema                    # スキーマ表示"; \
		echo "  SELECT * FROM v_summary_statistics;  # サマリー統計"; \
		echo "  .quit                      # 終了"; \
		echo ""; \
		duckdb src/ml/data/dwh/data/house_price_dwh.duckdb; \
	else \
		echo "❌ DWHデータベースが見つかりません。先に 'make dwh-bronze' を実行してください"; \
		exit 1; \
	fi

# DWHテーブル一覧表示
dwh-tables:
	@echo "📋 DWHテーブル一覧表示中..."
	@if [ -f "src/ml/data/dwh/data/house_price_dwh.duckdb" ]; then \
		duckdb src/ml/data/dwh/data/house_price_dwh.duckdb ".tables"; \
	else \
		echo "❌ DWHデータベースが見つかりません。先に 'make dwh-bronze' を実行してください"; \
		exit 1; \
	fi

# DWHサマリー統計表示
dwh-summary:
	@echo "📊 DWHサマリー統計表示中..."
	@if [ -f "src/ml/data/dwh/data/house_price_dwh.duckdb" ]; then \
		duckdb src/ml/data/dwh/data/house_price_dwh.duckdb "SELECT * FROM v_summary_statistics;"; \
	else \
		echo "❌ DWHデータベースが見つかりません。先に 'make dwh-bronze' を実行してください"; \
		exit 1; \
	fi

# DWH地域別分析表示
dwh-location:
	@echo "📍 DWH地域別分析表示中..."
	@if [ -f "src/ml/data/dwh/data/house_price_dwh.duckdb" ]; then \
		duckdb src/ml/data/dwh/data/house_price_dwh.duckdb "SELECT * FROM v_location_analytics ORDER BY avg_price DESC;"; \
	else \
		echo "❌ DWHデータベースが見つかりません。先に 'make dwh-bronze' を実行してください"; \
		exit 1; \
	fi

# DWH状態別分析表示
dwh-condition:
	@echo "🏠 DWH状態別分析表示中..."
	@if [ -f "src/ml/data/dwh/data/house_price_dwh.duckdb" ]; then \
		duckdb src/ml/data/dwh/data/house_price_dwh.duckdb "SELECT * FROM v_condition_analytics ORDER BY avg_price DESC;"; \
	else \
		echo "❌ DWHデータベースが見つかりません。先に 'make dwh-bronze' を実行してください"; \
		exit 1; \
	fi

# DWH価格帯別分析表示
dwh-price-range:
	@echo "💰 DWH価格帯別分析表示中..."
	@if [ -f "src/ml/data/dwh/data/house_price_dwh.duckdb" ]; then \
		duckdb src/ml/data/dwh/data/house_price_dwh.duckdb "SELECT CASE WHEN price < 300000 THEN 'Under $300k' WHEN price < 500000 THEN '$300k-$500k' WHEN price < 800000 THEN '$500k-$800k' ELSE 'Over $800k' END as price_range, COUNT(*) as house_count, AVG(price) as avg_price FROM fact_house_transactions GROUP BY price_range ORDER BY MIN(price);"; \
	else \
		echo "❌ DWHデータベースが見つかりません。先に 'make dwh-bronze' を実行してください"; \
		exit 1; \
	fi

# DWH築年数別分析表示
dwh-year-built:
	@echo "🏗️ DWH築年数別分析表示中..."
	@if [ -f "src/ml/data/dwh/data/house_price_dwh.duckdb" ]; then \
		duckdb src/ml/data/dwh/data/house_price_dwh.duckdb "SELECT y.decade, AVG(h.price) as avg_price, COUNT(*) as house_count FROM fact_house_transactions h JOIN dim_years y ON h.year_built_id = y.year_id GROUP BY y.decade ORDER BY y.decade;"; \
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

# アンサンブルモデル訓練（デフォルト設定）
train-ensemble:
	@echo "🔧 アンサンブルモデル訓練中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python src/models/training/train_ensemble.py \
			--config configs/app.yaml \
			--duckdb-path src/data/dwh/data/house_price_dwh.duckdb \
			--models-dir src/models \
			--view-name bronze_raw_house_data; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ アンサンブルモデル訓練完了"

# Voting Ensemble訓練
train-ensemble-voting:
	@echo "🔧 Voting Ensemble訓練中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python src/models/training/train_ensemble.py \
			--config configs/app.yaml \
			--duckdb-path src/data/dwh/data/house_price_dwh.duckdb \
			--models-dir src/models \
			--view-name bronze_raw_house_data \
			--ensemble-type voting; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ Voting Ensemble訓練完了"

# Stacking Ensemble訓練
train-ensemble-stacking:
	@echo "🔧 Stacking Ensemble訓練中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python src/models/training/train_ensemble.py \
			--config configs/app.yaml \
			--duckdb-path src/data/dwh/data/house_price_dwh.duckdb \
			--models-dir src/models \
			--view-name bronze_raw_house_data \
			--ensemble-type stacking; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ Stacking Ensemble訓練完了"

# アンサンブルモデル性能確認
check-ensemble:
	@echo "📊 アンサンブルモデル性能確認中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python -c "import joblib; import pandas as pd; import numpy as np; \
model = joblib.load('src/ml/models/trained/house_price_ensemble_duckdb.pkl'); \
preprocessor = joblib.load('src/ml/models/trained/house_price_ensemble_duckdb_preprocessor.pkl'); \
print('✅ アンサンブルモデル読み込み成功'); \
sample_data = pd.DataFrame({'sqft': [2000], 'bedrooms': [3], 'bathrooms': [2.5], 'year_built': [2000], 'location': ['Suburb'], 'condition': ['Good']}); \
current_year = 2025; \
sample_data['house_age'] = current_year - sample_data['year_built']; \
sample_data['price_per_sqft'] = 200; \
sample_data['bed_bath_ratio'] = sample_data['bedrooms'] / sample_data['bathrooms']; \
X_transformed = preprocessor.transform(sample_data); \
print(f'🔧 前処理後データ形状: {X_transformed.shape}'); \
prediction = model.predict(X_transformed); \
print('予測raw:', prediction); \
print('📈 アンサンブル予測結果:', prediction[0] if len(prediction) > 0 else '予測値が空です');" ; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ アンサンブルモデル性能確認完了"

# Bronze層データ取り込み
ingest:
	@echo "🗄️ DWH構築とデータインジェスション中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python src/ml/data/dwh/scripts/setup_dwh.py --csv-file src/ml/data/raw/house_data.csv; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ DWH構築完了"

# dbtで全層（Bronze/Silver/Gold）作成
dbt:
	@echo "🔄 dbtで全層（Bronze/Silver/Gold）作成中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/dbt run --project-dir src/ml/data/dwh/house_price_dbt && \
		.venv/bin/dbt test --project-dir src/ml/data/dwh/house_price_dbt; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi

# dbtドキュメント生成
docs:
	@echo "📄 dbtドキュメント生成中..."
	@if [ -d ".venv" ]; then \
		cd src/ml/data/dwh/house_price_dbt && ../../../.venv/bin/dbt docs generate && ../../../.venv/bin/dbt docs serve; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi

# dbt学習スクリプト実行
train-dbt:
	@echo "🔧 dbt学習スクリプト実行中..."
	@if [ -d ".venv" ]; then \
		.venv/bin/python src/ml/data/dwh/house_price_dbt/train.py; \
	else \
		echo "❌ 仮想環境が見つかりません。先に 'make venv' を実行してください"; \
		exit 1; \
	fi
	@echo "✅ dbt学習スクリプト実行完了"

# 一括実行
all: ingest dbt train-dbt
	@echo "🚀 一括実行完了"

# =============================================================================
# 📊 Metabase BI統合コマンド
# =============================================================================

# Metabaseセットアップ
metabase-setup:
	@echo "🔧 Metabase DuckDB セットアップ中..."
	@cd deployment/metabase && ./setup.sh
	@echo "✅ Metabaseセットアップ完了"

# Metabase起動
metabase-up:
	@echo "🚀 Metabase起動中..."
	@docker-compose -f deployment/docker/docker-compose.yaml up -d metabase
	@echo "✅ Metabase起動完了"
	@echo "🌐 アクセスURL: http://localhost:3000"

# Metabase停止
metabase-down:
	@echo "🛑 Metabase停止中..."
	@docker-compose -f deployment/docker/docker-compose.yaml stop metabase
	@echo "✅ Metabase停止完了"

# Metabase再起動
metabase-restart:
	@echo "🔄 Metabase再起動中..."
	@docker-compose -f deployment/docker/docker-compose.yaml restart metabase
	@echo "✅ Metabase再起動完了"

# Metabaseログ確認
metabase-logs:
	@echo "📋 Metabaseログ表示中..."
	@docker-compose -f deployment/docker/docker-compose.yaml logs -f metabase

# Metabase状態確認
metabase-status:
	@echo "📊 Metabase状態確認中..."
	@docker-compose -f deployment/docker/docker-compose.yaml ps metabase
	@echo ""
	@echo "🔍 ヘルスチェック:"
	@curl -s http://localhost:3000/api/health || echo "❌ Metabaseに接続できません"

# Metabaseデータベース接続確認
metabase-check-connection:
	@echo "🔗 Metabase DuckDB接続確認中..."
	@echo "📋 接続設定例:"
	@echo "  Database Type: DuckDB"
	@echo "  Connection String: jdbc:duckdb:/app/data/house_price_dwh.duckdb"
	@echo ""
	@echo "📊 利用可能なテーブル/ビュー:"
	@if [ -f "src/ml/data/dwh/data/house_price_dwh.duckdb" ]; then \
		duckdb src/ml/data/dwh/data/house_price_dwh.duckdb ".tables"; \
	else \
		echo "❌ DWHデータベースが見つかりません。先に 'make dwh' を実行してください"; \
	fi

# Metabaseダッシュボード作成支援
metabase-dashboard-setup:
	@echo "🎨 Metabaseダッシュボード作成支援..."
	@echo "📋 推奨ダッシュボード構成:"
	@echo ""
	@echo "1. 📊 住宅価格概要ダッシュボード"
	@echo "   - 価格分布ヒストグラム"
	@echo "   - 地域別平均価格"
	@echo "   - 築年数別価格推移"
	@echo "   - 条件別価格比較"
	@echo ""
	@echo "2. 🔮 予測分析ダッシュボード"
	@echo "   - 予測精度メトリクス"
	@echo "   - 特徴量重要度"
	@echo "   - 予測vs実測比較"
	@echo "   - モデル性能推移"
	@echo ""
	@echo "3. 📈 市場分析ダッシュボード"
	@echo "   - 価格トレンド分析"
	@echo "   - 地域別市場動向"
	@echo "   - 季節性分析"
	@echo "   - 価格変動要因"
	@echo ""
	@echo "🌐 アクセスURL: http://localhost:3000"

# Metabase完全セットアップ（セットアップ + 起動）
metabase-full: metabase-setup metabase-up
	@echo "✅ Metabase完全セットアップ完了"
	@echo "🌐 アクセスURL: http://localhost:3000"
	@echo "📋 初期設定: 初回アクセス時に管理者アカウントを作成してください"

# Metabaseクリーンアップ
metabase-clean:
	@echo "🧹 Metabaseクリーンアップ中..."
	@docker-compose -f deployment/docker/docker-compose.yaml down metabase
	@rm -rf deployment/metabase/data/*
	@rm -rf deployment/metabase/plugins/*
	@echo "✅ Metabaseクリーンアップ完了"

# Metabaseドライバ更新
metabase-update-driver:
	@echo "🔄 Metabase DuckDBドライバ更新中..."
	@rm -f deployment/metabase/plugins/duckdb.metabase-driver.jar
	@bash deployment/metabase/setup.sh
	@echo "✅ ドライバ更新完了"
	@echo "🔄 Metabase再起動が必要です: make metabase-restart" 