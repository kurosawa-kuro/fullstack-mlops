# 📊 Metabase - DuckDB BI統合

このディレクトリには、DuckDBデータウェアハウスとMetabaseを連携させるための設定ファイルが含まれています。

## 🎯 概要

Metabaseは、DuckDBのデータを可視化・分析するためのBIツールです。DuckDB JDBCドライバを使用して、DuckDBファイルやMotherDuckクラウドデータベースに直接接続できます。

## 🚀 クイックスタート

### 1. セットアップ実行
```bash
cd deployment/metabase
./setup.sh
```

### 2. Metabase起動
```bash
# 個別起動
docker-compose up metabase

# 全サービス起動
docker-compose up -d
```

### 3. アクセス
- **URL**: http://localhost:3000
- **初期設定**: 初回アクセス時に管理者アカウントを作成

## 🔗 DuckDB接続設定

### ローカルDuckDBファイル接続
1. Admin → Databases → Add Database
2. Database Type: **DuckDB**
3. Connection String: `jdbc:duckdb:/app/data/house_price_dwh.duckdb`

### MotherDuckクラウド接続
1. Admin → Databases → Add Database
2. Database Type: **DuckDB**
3. Connection String: `jdbc:duckdb:md:your-database-name`

## 📊 利用可能なデータ

### テーブル・ビュー一覧
- **v_house_analytics**: メイン分析ビュー（推奨）
- **house_prices**: 生データテーブル
- **house_features**: 特徴量データテーブル
- **house_predictions**: 予測結果テーブル

### 主要メトリクス
- 住宅価格分布
- 地域別価格分析
- 築年数と価格の関係
- 部屋数と価格の相関
- 条件別価格比較

## 🎨 ダッシュボード例

### 1. 住宅価格概要ダッシュボード
- 価格分布ヒストグラム
- 地域別平均価格
- 築年数別価格推移
- 条件別価格比較

### 2. 予測分析ダッシュボード
- 予測精度メトリクス
- 特徴量重要度
- 予測vs実測比較
- モデル性能推移

### 3. 市場分析ダッシュボード
- 価格トレンド分析
- 地域別市場動向
- 季節性分析
- 価格変動要因

## 🔧 設定ファイル

### metabase.properties
```properties
# 基本設定
MB_DB_TYPE=h2
MB_DB_FILE=/metabase-data/metabase.db
JAVA_OPTS=-Xmx2g -XX:+UseG1GC

# DuckDBドライバ設定
MB_PLUGINS_DIR=/plugins
MB_PLUGINS_ENABLED=true

# セキュリティ設定
MB_ENCRYPTION_SECRET_KEY=your-secret-key-here
MB_PASSWORD_COMPLEXITY=strong
MB_PASSWORD_LENGTH=8

# パフォーマンス設定
MB_MAX_MEMORY=2g
MB_MIN_MEMORY=512m
```

## 📈 可視化のベストプラクティス

### 1. データ型に応じた可視化選択
- **数値データ**: ヒストグラム、箱ひげ図、散布図
- **カテゴリデータ**: 棒グラフ、円グラフ、テーブル
- **時系列データ**: 折れ線グラフ、エリアチャート
- **地理データ**: マップ、ヒートマップ

### 2. ダッシュボード設計原則
- **階層構造**: 概要 → 詳細の流れ
- **一貫性**: 色使い・フォントの統一
- **インタラクティブ**: フィルター・ドリルダウン機能
- **レスポンシブ**: 画面サイズ対応

### 3. パフォーマンス最適化
- **クエリ最適化**: インデックス活用
- **キャッシュ設定**: 適切な更新頻度
- **データ量制限**: 表示件数の制限
- **非同期処理**: 長時間クエリの分離

## 🔍 トラブルシューティング

### よくある問題

#### 1. DuckDBドライバが見つからない
```bash
# ドライバの再ダウンロード
cd deployment/metabase
rm -f plugins/duckdb.metabase-driver.jar
./setup.sh
```

#### 2. 接続エラー
- DuckDBファイルのパス確認
- ファイル権限の確認
- ネットワーク設定の確認

#### 3. メモリ不足
```bash
# Docker Compose設定でメモリ制限を調整
environment:
  - JAVA_OPTS=-Xmx4g -XX:+UseG1GC
```

#### 4. パフォーマンス問題
- クエリの最適化
- インデックスの追加
- データの事前集計

## 🔄 データ更新

### 自動更新設定
1. Admin → Databases → DuckDB → Edit
2. Scan for schema changes: **Hourly**
3. Re-scan field values: **Daily**

### 手動更新
```bash
# DWHデータの再構築
make dwh

# Metabaseの再起動
docker-compose restart metabase
```

## 📚 参考資料

- [Metabase公式ドキュメント](https://www.metabase.com/docs/latest/)
- [DuckDB JDBCドライバ](https://github.com/motherduckdb/metabase_duckdb_driver)
- [MotherDuckドキュメント](https://motherduck.com/docs/)

## 🤝 サポート

問題が発生した場合は、以下を確認してください：

1. **ログ確認**: `docker-compose logs metabase`
2. **設定確認**: `deployment/metabase/config/`
3. **ドライバ確認**: `deployment/metabase/plugins/`
4. **データ確認**: `src/ml/data/dwh/data/`

---

**注意**: Metabaseは自己ホスト版でのみDuckDBドライバが利用可能です。Metabase Cloudでは現在サポートされていません。 