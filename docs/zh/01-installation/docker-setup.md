# Docker 安装

使用 Docker 运行 TestGyver 是最简单的入门方式，可以确保所有依赖项都被隔离。

## 构建镜像

1.  导航到项目根目录：
    ```bash
    cd app_test
    ```

2.  构建 Docker 镜像：
    ```bash
    docker build -t testgyver:latest .
    ```

## 使用 Docker Compose 运行（推荐）

在根目录下创建一个 `docker-compose.yml` 文件，以编排应用程序和 MongoDB 数据库。

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
      - "8080:8080"
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

启动堆栈：
```bash
docker-compose up -d
```

应用程序将在 `http://localhost:8080` 上可用。

## 使用 Docker 手动运行

如果您更喜欢单独运行容器：

1.  启动 MongoDB：
    ```bash
    docker run -d --name mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=mypass mongo:6.0
    ```

2.  运行应用程序。要连接到主机 (localhost) 上运行的 MongoDB 实例，请使用以下命令：
    ```bash
    docker run --rm \
      -p 8080:8080 \
      --add-host=host.docker.internal:host-gateway \
      -e MONGO_HOST=host.docker.internal \
      testgyver:latest
    ```
