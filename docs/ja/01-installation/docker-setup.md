# Docker インストール

Docker で TestGyver を実行することは、すべての依存関係が分離されているため、開始するための最も簡単な方法です。

## イメージのビルド

1.  プロジェクトのルートに移動します:
    ```bash
    cd app_test
    ```

2.  Docker イメージをビルドします:
    ```bash
    docker build -t testgyver:latest .
    ```

## Docker Compose での実行 (推奨)

アプリケーションと MongoDB データベースをオーケストレーションするために、ルートディレクトリに `docker-compose.yml` ファイルを作成します。

```yaml
version: '3.8'

services:
  mongo:
    image: mongo:6.0
    container_name: testgyver-mongo
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: mypass
    volumes:
      - mongo_data:/data/db

  app:
    image: testgyver:latest
    container_name: testgyver-app
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    depends_on:
      - mongo
    volumes:
      - ./configuration.json:/app/configuration.json
      - ./workdir:/app/workdir

volumes:
  mongo_data:
```

スタックを開始します:
```bash
docker-compose up -d
```

アプリケーションは `http://localhost:5000` で利用可能になります。

## Docker での手動実行

コンテナを個別に実行したい場合:

1.  MongoDB を開始します:
    ```bash
    docker run -d --name mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=mypass mongo:6.0
    ```

2.  アプリケーションを実行します。ホストマシン (localhost) で実行されている MongoDB インスタンスに接続するには、次のコマンドを使用します:
    ```bash
    docker run --rm \
      -p 5000:5000 \
      --add-host=host.docker.internal:host-gateway \
      -e MONGO_HOST=host.docker.internal \
      testgyver:latest
    ```
