# 手动安装

按以下步骤在本机安装并运行 TestGyver。

## 1. 克隆仓库

```bash
git clone <repository-url>
cd app_test
```

## 2. 创建虚拟环境

推荐使用虚拟环境管理依赖。

```bash
python3 -m venv .venv

# 激活
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
```

## 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 4. 配置

1.  复制示例配置（如有）或在根目录创建 `configuration.json`。
2.  参阅 [配置指南](configuration.md) 获取详情。

## 5. 初始化数据库（可选）

可预置初始数据和索引。

```bash
python init/init_database.py
```

创建管理员用户：
```bash
python init/create_user.py
```

## 6. 运行应用

```bash
export FLASK_APP=app
export FLASK_ENV=development  # 部署用 'production'

flask run --host=0.0.0.0 --port=8080
```

访问 `http://localhost:8080`。
