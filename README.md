# Real-Time Data Ingestion System

このプロジェクトは、PostgreSQL CDC、FastAPI、Debezium、Kafka、Schema Registryを使用したリアルタイムデータ取り込みシステムです。

## システム構成

- **PostgreSQL**: CDC（Change Data Capture）が有効化されたデータベース
- **FastAPI**: データベースのCRUD操作を提供するAPI
- **Debezium**: PostgreSQLのトランザクションログを監視してKafkaに送信
- **Kafka**: メッセージストリーミングプラットフォーム
- **Schema Registry**: Avroスキーマの管理
- **Zookeeper**: Kafkaのコーディネーション

## セットアップと起動

### 前提条件
- Docker
- Docker Compose

### 起動手順

1. リポジトリをクローン
```bash
git clone <repository-url>
cd RealTimeDataIngestion
```

2. 全サービスを起動
```bash
docker compose up -d
```

3. サービスの起動確認
```bash
docker compose ps
```

4. Debeziumコネクタをセットアップ（サービス起動後5-10分待ってから実行）
```bash
./setup-debezium.sh
```

## サービスエンドポイント

- **FastAPI**: http://localhost:8000
  - API ドキュメント: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Kafka**: localhost:9092
- **Schema Registry**: http://localhost:8081
- **Debezium Connect**: http://localhost:8083

## FastAPI CRUD操作

### ユーザー操作

- **GET** `/users/` - 全ユーザー取得
- **POST** `/users/` - ユーザー作成
- **GET** `/users/{user_id}` - 特定ユーザー取得
- **PUT** `/users/{user_id}` - ユーザー更新
- **DELETE** `/users/{user_id}` - ユーザー削除

### 商品操作

- **GET** `/products/` - 全商品取得
- **POST** `/products/` - 商品作成
- **GET** `/products/{product_id}` - 特定商品取得
- **PUT** `/products/{product_id}` - 商品更新
- **DELETE** `/products/{product_id}` - 商品削除

### 使用例

```bash
# 新規ユーザー作成
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}'

# 商品更新
curl -X PUT "http://localhost:8000/products/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Laptop", "price": 1199.99}'
```

## Kafkaトピックの確認

CDC イベントを確認するには：

```bash
# Kafkaコンテナに接続
docker exec -it kafka bash

# トピック一覧表示
kafka-topics --bootstrap-server localhost:9092 --list

# ユーザーテーブルの変更を監視
kafka-console-consumer --bootstrap-server localhost:9092 --topic users --from-beginning

# 商品テーブルの変更を監視
kafka-console-consumer --bootstrap-server localhost:9092 --topic products --from-beginning
```

## データベース直接アクセス

```bash
# PostgreSQLコンテナに接続
docker exec -it postgres psql -U postgres -d testdb

# テーブル確認
\dt

# データ確認
SELECT * FROM users;
SELECT * FROM products;
```

## システム停止

```bash
docker compose down -v
```

## トラブルシューティング

1. **Debeziumコネクタが失敗する場合**:
   - PostgreSQLが完全に起動してからコネクタをセットアップしてください
   - `docker compose logs debezium` でログを確認

2. **FastAPIがデータベースに接続できない場合**:
   - PostgreSQLサービスが起動していることを確認
   - `docker compose logs fastapi` でログを確認

3. **Kafkaトピックが作成されない場合**:
   - Debeziumコネクタのステータスを確認: `curl http://localhost:8083/connectors/postgres-connector/status`

## ファイル構成

```
.
├── docker-compose.yml          # メインの構成ファイル
├── .env                        # 環境変数
├── setup-debezium.sh          # Debeziumセットアップスクリプト
├── postgres/
│   ├── postgresql.conf         # PostgreSQL設定（CDC有効化）
│   └── init/
│       └── 01-init.sql        # データベース初期化スクリプト
├── fastapi/
│   ├── Dockerfile             # FastAPIのDockerイメージ
│   ├── requirements.txt       # Python依存関係
│   └── main.py               # FastAPIアプリケーション
└── debezium/
    └── postgres-connector.json # Debeziumコネクタ設定
```