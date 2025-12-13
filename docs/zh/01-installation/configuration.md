# 配置

应用通过根目录下的 `configuration.json` 配置。

## 结构

```json
{
    "mongo": {
        "user": "root",
        "pass": "mypass",
        "host": "localhost",
        "port": "27017",
        "bdd": "testGyver",
        "prefix": "mgv_",
        "soft_delete": true
    },
    "jwt_secret": "your-secret-key",
    "app": {
        "debug": true,
        "port": 8080,
        "host": "0.0.0.0"
    },
    "pagination": {
        "page_size": 20,
        "max_page_size": 100
    },
    "security": {
        "token_expiration_minutes": 60,
        "password_min_length": 8
    },
    "workdir": "./workdir",
    "version": "1.0.0"
}
```

## 参数说明

### Mongo
*   **user**：MongoDB 用户名。
*   **pass**：密码。
*   **host**：数据库主机（如 `localhost` 或 Docker 中的 `mongo`）。
*   **port**：端口（默认 `27017`）。
*   **bdd**：数据库名。
*   **prefix**：集合前缀（如 `mgv_users`）。
*   **soft_delete**：true 时标记删除而非物理删除。

### 安全
*   **jwt_secret**：JWT 签名密钥，生产环境务必更换。
*   **token_expiration_minutes**：会话时长（分钟）。
*   **password_min_length**：密码最小长度。

### 应用
*   **debug**：Flask 调试模式（自动重载），生产应设为 false。
*   **port**：监听端口。
*   **host**：绑定地址（`0.0.0.0`）。

### Workdir
*   **workdir**：存放活动文件和临时数据的目录。
