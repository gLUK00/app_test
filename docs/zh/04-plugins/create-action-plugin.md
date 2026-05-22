# 创建新的动作插件

本指南说明如何为 TestGyver 编写动作插件，扩展 API、文件、数据库等能力。

## 前提

*   具备基础 Python 知识。
*   可访问 `plugins/actions/`。

## 步骤

### 1. 创建文件

在 `plugins/actions/` 下建一个描述性的 `.py` 文件（如 `my_custom_action.py`）。

### 2. 继承 `ActionBase`

```python
from plugins.actions.action_base import ActionBase

class MyCustomAction(ActionBase):
    """动作说明"""
    plugin_name = "my_custom_action"
    label = "My Custom Action"
    version = "1.0.0"
    author = "Your Name"
```

### 3. 实现方法

#### `get_metadata(self)`
返回基本信息。

```python
    def get_metadata(self):
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "详细描述"
        }
```

#### `validate_config(self, config)`
执行前校验参数。

```python
    def validate_config(self, config):
        if 'target_host' not in config:
            return (False, "Target host is required")
        return (True, "")
```

#### `get_input_mask(self)`
定义 UI 表单。支持 `string`, `number`, `boolean`, `textarea`, `select`, `checkbox`, `select-var-test`。

```python
    def get_input_mask(self):
        return [
            {"name": "target_host", "type": "string", "label": "Target Host", "placeholder": "192.168.1.1", "required": True},
            {"name": "port", "type": "number", "label": "Port", "placeholder": 8080, "required": False}
        ]
```

#### `get_output_variables(self)`
声明输出变量。

```python
    def get_output_variables(self):
        return [
            {"name": "execution_result", "description": "结果", "type": "string"}
        ]
```

#### `execute(self, context)`
核心逻辑，`context` 提供变量与环境。

```python
    def execute(self, context):
        host = context.get('target_host')
        try:
            result = "Success"
            self.output_variables['execution_result'] = result
            return (0, ["Connected to " + host, "Operation successful"])
        except Exception as e:
            return (1, [f"Error: {str(e)}"])
```

### 4. 注册

`PluginManager` 会自动发现 `plugins/actions/` 下的插件，无需手动登记。重启应用即可。

## 最佳实践

*   **错误处理**：使用 try/except，避免崩溃。
*   **日志**：返回详细 traces 便于调试。
*   **校验**：在 `validate_config` 中尽早拦截错误。

## 测试您的插件

为了方便插件的开发和测试，可以通过 Docker Compose 使用完整的本地环境。

### 1. 启动测试环境

`init/` 目录中提供了一个 `test-docker-compose.yml` 文件。它设置了各种服务（FTP、SFTP、WebDAV、SSH、S3/MinIO、HTTP API），以便针对真实目标测试您的操作。

```bash
sudo docker compose -f init/test-docker-compose.yml up -d
```

### 2. 导入测试数据

要使用涵盖所有标准操作的综合测试活动快速填充您的 TestGyver 实例：

1.  转到应用程序中的 **活动** 页面。
2.  点击 **导入**。
3.  选择文件 `init/campain_All_tests.json`。

此活动包含有关如何配置操作以与测试环境提供的服务进行交互的示例。

### 3. 导入环境变量

测试活动依赖于特定的变量（主机名、凭据等）。您可以使用提供的脚本自动导入它们。

确保您的虚拟环境处于活动状态，然后运行：

```bash
python import_variables.py init/import-var-test-docker.json
```

这将在“全局”环境（或 JSON 文件中定义的环境）中创建必要的变量，以匹配 `test-docker-compose.yml` 配置。
