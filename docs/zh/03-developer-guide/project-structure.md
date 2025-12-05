# 项目结构

```text
/
├── app.py                  # 入口
├── configuration.json      # 配置
├── Dockerfile              # 容器定义
├── requirements.txt        # 依赖
├── docs/                   # 文档
├── init/                   # 初始化脚本
├── models/                 # Mongo 模型
├── plugins/                # 插件系统
│   ├── actions/            # 动作实现
│   ├── plugin_base.py      # 基类
│   └── plugin_manager.py   # 发现与加载
├── routes/                 # API/Web 路由
├── static/                 # 静态资源
├── templates/              # Jinja2 模板
├── translations/           # i18n 文件
├── utils/                  # 辅助/核心逻辑
└── workdir/                # 运行期存储
```

## 关键目录

*   **`models/`**：MongoDB 文档类与 CRUD。
*   **`routes/`**：按模块拆分（Auth、API、Web UI）。
*   **`plugins/actions/`**：扩展系统能力的地方。
*   **`utils/`**：核心逻辑，如 `campain_executor.py`。
