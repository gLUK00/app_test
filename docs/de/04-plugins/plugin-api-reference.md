# Plugin-API-Referenz

## `ActionBase` Methoden

### `get_metadata(self) -> dict`
Muss zurückgeben:
*   `name`, `version`, `author`, `description`.

### `validate_config(self, config: dict) -> tuple[bool, str]`
Prüft Parameter vor Ausführung.
*   Rückgabe `(True, "")` oder `(False, "Fehler")`.

### `get_input_mask(self) -> list[dict]`
UI-Felder definieren:
*   `name`, `type` (`string`, `number`, `boolean`, `textarea`, `select`, `select-var-test`), `label`, `required`, `options` (für select).

### `execute(self, context: ActionContext) -> tuple[int, list[str]]`
Hauptlogik.
*   Rückgabe `(status_code, traces)` mit `0` Erfolg, `1` Fehler.

## `ActionContext`

Dictionary-ähnlich, enthält:
*   Aufgelöste Variablen.
*   Umgebungsinfos.

## Output-Variablen

Während der Ausführung setzen:
```python
self.output_variables['my_var'] = "value"
```
Nutzbar als `{{my_var}}` in Folgeschritten.
