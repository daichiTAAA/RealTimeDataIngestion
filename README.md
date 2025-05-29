# Real-Time Data Ingestion System

このプロジェクトは、PostgreSQL CDC、FastAPI、Debezium、Kafka、Schema Registryを使用したリアルタイムデータ取り込みシステムです。

## システム構成

- **PostgreSQL**: CDC（Change Data Capture）が有効化されたデータベース
- **SQL Server**: CDC（Change Data Capture）が有効化されたデータベース  
- **FastAPI**: PostgreSQLとSQL Serverに対するCRUD操作を提供するAPI
- **Debezium**: PostgreSQLとSQL Serverのトランザクションログを監視してKafkaに送信
- **Kafka**: メッセージストリーミングプラットフォーム
- **Schema Registry**: Avroスキーマの管理
- **Zookeeper**: Kafkaのコーディネーション
- **AKHQ**: KafkaとSchema RegistryのWebベースGUI管理ツール

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
- **SQL Server**: localhost:1433
- **Kafka**: localhost:9092
- **Schema Registry**: http://localhost:8081
- **Debezium Connect**: http://localhost:8083
- **AKHQ (Kafka GUI)**: http://localhost:8080

## FastAPI CRUD操作

### PostgreSQL ユーザー操作

- **GET** `/users/` - 全ユーザー取得
- **POST** `/users/` - ユーザー作成
- **GET** `/users/{user_id}` - 特定ユーザー取得
- **PUT** `/users/{user_id}` - ユーザー更新
- **DELETE** `/users/{user_id}` - ユーザー削除

### PostgreSQL 商品操作

- **GET** `/products/` - 全商品取得
- **POST** `/products/` - 商品作成
- **GET** `/products/{product_id}` - 特定商品取得
- **PUT** `/products/{product_id}` - 商品更新
- **DELETE** `/products/{product_id}` - 商品削除

### SQL Server ユーザー操作

- **GET** `/sqlserver/users/` - 全ユーザー取得
- **POST** `/sqlserver/users/` - ユーザー作成
- **GET** `/sqlserver/users/{user_id}` - 特定ユーザー取得
- **PUT** `/sqlserver/users/{user_id}` - ユーザー更新
- **DELETE** `/sqlserver/users/{user_id}` - ユーザー削除

### SQL Server 商品操作

- **GET** `/sqlserver/products/` - 全商品取得
- **POST** `/sqlserver/products/` - 商品作成
- **GET** `/sqlserver/products/{product_id}` - 特定商品取得
- **PUT** `/sqlserver/products/{product_id}` - 商品更新
- **DELETE** `/sqlserver/products/{product_id}` - 商品削除

### 使用例

```bash
# PostgreSQL: 新規ユーザー作成
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}'

# SQL Server: 新規ユーザー作成
curl -X POST "http://localhost:8000/sqlserver/users/" \
  -H "Content-Type: application/json" \
  -d '{"name": "SQL Test User", "email": "sqltest@example.com"}'

# PostgreSQL: 商品更新
curl -X PUT "http://localhost:8000/products/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Laptop", "price": 1199.99}'

# SQL Server: 商品更新
curl -X PUT "http://localhost:8000/sqlserver/products/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated SQL Laptop", "price": 1299.99}'
```

## Kafkaトピックの確認

CDC イベントを確認するには：

```bash
# Kafkaコンテナに接続
docker exec -it kafka bash

# トピック一覧表示
kafka-topics --bootstrap-server localhost:9092 --list

# PostgreSQL ユーザーテーブルの変更を監視
kafka-console-consumer --bootstrap-server localhost:9092 --topic users --from-beginning

# PostgreSQL 商品テーブルの変更を監視
kafka-console-consumer --bootstrap-server localhost:9092 --topic products --from-beginning

# SQL Server ユーザーテーブルの変更を監視
kafka-console-consumer --bootstrap-server localhost:9092 --topic sqlserver_users --from-beginning

# SQL Server 商品テーブルの変更を監視
kafka-console-consumer --bootstrap-server localhost:9092 --topic sqlserver_products --from-beginning
```

## AKHQ GUI の使用

AKHQはKafkaとSchema RegistryのWebベースGUIです：

1. **Webブラウザでアクセス**: http://localhost:8080

2. **利用可能な機能**:
   - Kafkaトピックの閲覧と管理
   - メッセージの表示と検索
   - Schema Registryのスキーマ管理
   - Debezium Connectコネクタの監視
   - コンシューマーグループの確認

3. **トピック確認**:
   - 左メニューから「Topic」を選択
   - PostgreSQL: `users` と `products` トピック
   - SQL Server: `sqlserver_users` と `sqlserver_products` トピック
   - CDCイベントを確認可能

4. **スキーマ確認**:
   - 左メニューから「Schema Registry」を選択
   - Avroスキーマの管理と確認が可能

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

```bash
# SQL Serverコンテナに接続
docker exec -it sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P SqlServer123!

# データベース選択
USE testdb;
GO

# テーブル確認
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';
GO

# データ確認
SELECT * FROM users;
GO
SELECT * FROM products;
GO
```

## システム停止

```bash
docker compose down -v
```

## トラブルシューティング

1. **Debeziumコネクタが失敗する場合**:
   - PostgreSQLとSQL Serverが完全に起動してからコネクタをセットアップしてください
   - `docker compose logs debezium` でログを確認
   - PostgreSQLコネクタのステータス確認: `curl http://localhost:8083/connectors/postgres-connector/status`
   - SQL Serverコネクタのステータス確認: `curl http://localhost:8083/connectors/sqlserver-connector/status`

2. **FastAPIがデータベースに接続できない場合**:
   - PostgreSQLとSQL Serverサービスが起動していることを確認
   - `docker compose logs fastapi` でログを確認
   - `docker compose logs postgres` でPostgreSQLログを確認
   - `docker compose logs sqlserver` でSQL Serverログを確認

3. **Kafkaトピックが作成されない場合**:
   - 全コネクタのリスト確認: `curl http://localhost:8083/connectors`
   - PostgreSQLトピック: `users`, `products`
   - SQL Serverトピック: `sqlserver_users`, `sqlserver_products`

4. **SQL Server CDC が動作しない場合**:
   - SQL Server Agent が起動していることを確認
   - CDC が有効になっていることを確認: `SELECT is_cdc_enabled FROM sys.databases WHERE name = 'testdb'`

## ファイル構成

```
.
├── docker-compose.yml          # メインの構成ファイル
├── .env                        # 環境変数
├── setup-debezium.sh          # Debeziumセットアップスクリプト
├── postgres/
│   ├── postgresql.conf         # PostgreSQL設定（CDC有効化）
│   └── init/
│       └── 01-init.sql        # PostgreSQLデータベース初期化スクリプト
├── sqlserver/
│   └── init/
│       ├── 01-init.sql        # SQL Serverデータベース初期化スクリプト
│       └── entrypoint.sh      # SQL Server初期化エントリーポイント
├── fastapi/
│   ├── Dockerfile             # FastAPIのDockerイメージ
│   ├── requirements.txt       # Python依存関係
│   └── main.py               # FastAPIアプリケーション
└── debezium/
    ├── postgres-connector.json # PostgreSQL Debeziumコネクタ設定
    └── sqlserver-connector.json # SQL Server Debeziumコネクタ設定
```