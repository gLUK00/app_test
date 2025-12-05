# Plugin API Reference

## `ActionBase` Methods

### `get_metadata(self) -> dict`
Must return a dictionary with:
*   `name`: Internal unique name.
*   `version`: Plugin version.
*   `author`: Author name.
*   `description`: Short description.

### `validate_config(self, config: dict) -> tuple[bool, str]`
Called before execution to verify parameters.
*   **Returns**: `(True, "")` if valid, or `(False, "Error message")` if invalid.

### `get_input_mask(self) -> list[dict]`
Defines the UI fields. Each dict represents a field:
*   `name`: Key in the config dictionary.
*   `type`: `string`, `number`, `boolean`, `textarea`, `select`, `select-var-test`.
*   `label`: Display name.
*   `required`: Boolean.
*   `options`: List of values (for `select`).

### `execute(self, context: ActionContext) -> tuple[int, list[str]]`
The main logic.
*   **Returns**: `(status_code, traces)`
    *   `status_code`: `0` for success, `1` for failure.
    *   `traces`: List of strings (logs) to display in the report.

## `ActionContext`

A dictionary-like object passed to `execute()`. It contains:
*   Resolved variables.
*   Environment information.

## Output Variables

To set an output variable during execution:
```python
self.output_variables['my_var'] = "value"
```
This value will be available to subsequent actions as `{{my_var}}`.
