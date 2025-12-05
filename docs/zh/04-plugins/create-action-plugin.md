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
