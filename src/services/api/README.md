# House Price Prediction API

## プロジェクト構成

```
src/services/api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPIアプリケーション
│   ├── models/              # データモデル
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydanticスキーマ
│   ├── services/            # ビジネスロジック
│   │   ├── __init__.py
│   │   └── inference.py     # 推論サービス
│   └── utils/               # ユーティリティ
│       ├── __init__.py
│       └── helpers.py       # ヘルパー関数
├── requirements.txt
├── Dockerfile
└── README.md
```

## Dockerイメージのビルド手順

### 前提条件
- Base Image: `python:3.12-slim`
- 依存関係のインストール: `pip install requirements.txt`
- ポート: `8000`
- 起動コマンド: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### コンテナ内のディレクトリ構造
```
/app
├── app/
│   ├── main.py
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   └── inference.py
│   └── utils/
│       └── helpers.py
├── requirements.txt
└── models/
    └── trained/
        ├── house_price_prediction.pkl
        └── preprocessor.pkl
```

## API エンドポイント

- `GET /health`: ヘルスチェック
- `POST /predict`: 単一予測
- `POST /batch-predict`: バッチ予測

## 開発者情報

- **Author**: Gourav Shah
- **Organization**: School of Devops
- **License**: Apache 2.0

