# アクションプラグインを作成する

TestGyver に新しい自動タスク（API、ファイル、DB 等）を追加する手順です。

## 前提

*   Python の基礎
*   `plugins/actions/` へのアクセス

## 手順

### 1. ファイルを作る
`plugins/actions/` に説明的な `.py` を作成（例: `my_custom_action.py`）。

### 2. `ActionBase` を継承
```python
from plugins.actions.action_base import ActionBase

class MyCustomAction(ActionBase):
    """アクションの説明"""
    plugin_name = "my_custom_action"
    label = "My Custom Action"
    version = "1.0.0"
    author = "Your Name"
```

### 3. 必須メソッド

#### `get_metadata`
```python
    def get_metadata(self):
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "詳細説明"
        }
```

#### `validate_config`
```python
    def validate_config(self, config):
        if 'target_host' not in config:
            return (False, "Target host is required")
        return (True, "")
```

#### `get_input_mask`
UI フォーム定義。`string`, `number`, `boolean`, `textarea`, `select`, `checkbox`, `select-var-test` に対応。
```python
    def get_input_mask(self):
        return [
            {"name": "target_host", "type": "string", "label": "Target Host", "placeholder": "192.168.1.1", "required": True},
            {"name": "port", "type": "number", "label": "Port", "placeholder": 8080, "required": False}
        ]
```

#### `get_output_variables`
```python
    def get_output_variables(self):
        return [
            {"name": "execution_result", "description": "結果", "type": "string"}
        ]
```

#### `execute`
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

### 4. 登録
`PluginManager` が `plugins/actions/` を自動スキャンするため手動登録不要。アプリを再起動するだけ。

## ベストプラクティス

*   **エラー処理**: try/except で runner を落とさない。
*   **ログ**: 詳細な trace を返す。
*   **バリデーション**: `validate_config` で早期に検証。
