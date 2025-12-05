# プラグイン API リファレンス

## `ActionBase` のメソッド

### `get_metadata(self) -> dict`
`name`, `version`, `author`, `description` を返す。

### `validate_config(self, config: dict) -> tuple[bool, str]`
実行前の検証。`(True, "")` または `(False, "エラー")`。

### `get_input_mask(self) -> list[dict]`
UI 項目を定義：
*   `name`
*   `type` (`string`, `number`, `boolean`, `textarea`, `select`, `select-var-test`)
*   `label`, `required`, `options` (select 用)

### `execute(self, context: ActionContext) -> tuple[int, list[str]]`
メインロジック。
*   `status_code`: 0 成功 / 1 失敗
*   `traces`: レポート表示用ログ

## `ActionContext`

`execute()` に渡される辞書風オブジェクト。解決済み変数と環境情報を保持。

## 出力変数

実行中に設定:
```python
self.output_variables['my_var'] = "value"
```
以降 `{{my_var}}` で利用可能。
