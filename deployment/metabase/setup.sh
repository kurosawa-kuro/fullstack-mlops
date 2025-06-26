#!/bin/bash

# Metabase Setup Script for DuckDB Integration
# DuckDB JDBC Driver Installation and Configuration

set -e

echo "🔧 Metabase DuckDB セットアップ開始..."

# ディレクトリ作成
mkdir -p plugins
mkdir -p data
mkdir -p config

# DuckDB JDBC ドライバのダウンロード
echo "📦 DuckDB JDBC ドライバをダウンロード中..."
DRIVER_VERSION="v0.4.3"
DRIVER_URL="https://github.com/motherduckdb/metabase_duckdb_driver/releases/download/${DRIVER_VERSION}/duckdb.metabase-driver.jar"
DRIVER_PATH="plugins/duckdb.metabase-driver.jar"

if [ ! -f "$DRIVER_PATH" ]; then
    echo "📥 ドライバをダウンロード中: $DRIVER_URL"
    curl -L -o "$DRIVER_PATH" "$DRIVER_URL"
    echo "✅ ドライバダウンロード完了: $DRIVER_PATH"
else
    echo "✅ ドライバは既に存在します: $DRIVER_PATH"
fi

# 権限設定
chmod 644 "$DRIVER_PATH"

# 設定ファイル作成
echo "📝 Metabase設定ファイルを作成中..."
cat > config/metabase.properties << EOF
# Metabase Configuration for DuckDB Integration
MB_DB_TYPE=h2
MB_DB_FILE=/metabase-data/metabase.db
JAVA_OPTS=-Xmx2g -XX:+UseG1GC

# DuckDB Driver Configuration
MB_PLUGINS_DIR=/plugins
MB_PLUGINS_ENABLED=true

# Security Settings
MB_ENCRYPTION_SECRET_KEY=your-secret-key-here
MB_PASSWORD_COMPLEXITY=strong
MB_PASSWORD_LENGTH=8

# Performance Settings
MB_MAX_MEMORY=2g
MB_MIN_MEMORY=512m
EOF

echo "✅ Metabase設定ファイル作成完了"

# サンプルDuckDB接続設定
echo "📋 DuckDB接続設定例:"
echo ""
echo "Metabase起動後、以下の設定でDuckDBに接続してください:"
echo ""
echo "1. Admin → Databases → Add Database"
echo "2. Database Type: DuckDB"
echo "3. Connection String: jdbc:duckdb:/app/data/house_price_dwh.duckdb"
echo "4. または、MotherDuckの場合: jdbc:duckdb:md:your-database"
echo ""
echo "📊 利用可能なテーブル/ビュー:"
echo "- v_house_analytics (メインビュー)"
echo "- house_prices (生データ)"
echo "- house_features (特徴量データ)"
echo ""

echo "🚀 Metabase起動コマンド:"
echo "docker-compose up metabase"
echo ""
echo "🌐 アクセスURL: http://localhost:3000"
echo ""

echo "✅ Metabase DuckDB セットアップ完了！" 