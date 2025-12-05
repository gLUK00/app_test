# 插件 API 参考

## `ActionBase` 方法

### `get_metadata(self) -> dict`
返回 `name`、`version`、`author`、`description`。

### `validate_config(self, config: dict) -> tuple[bool, str]`
执行前验证参数。
*   返回 `(True, "")` 或 `(False, "错误信息")`。

### `get_input_mask(self) -> list[dict]`
定义 UI 字段：
*   `name`, `type` (`string`, `number`, `boolean`, `textarea`, `select`, `select-var-test`), `label`, `required`, `options` (select 用)。

### `execute(self, context: ActionContext) -> tuple[int, list[str]]`
核心逻辑。
*   返回 `(status_code, traces)`，`0` 成功，`1` 失败。

## `ActionContext`

传入 `execute()` 的类字典对象，包含已解析变量与环境信息。

## 输出变量

在执行时设置：
```python
self.output_variables['my_var'] = "value"
```
之后可用 `{{my_var}}` 引用。
