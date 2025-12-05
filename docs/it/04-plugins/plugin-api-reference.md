# Riferimento API Plugin

## Metodi `ActionBase`

### `get_metadata(self) -> dict`
Ritorna `name`, `version`, `author`, `description`.

### `validate_config(self, config: dict) -> tuple[bool, str]`
Verifica parametri prima dell'esecuzione.
*   Ritorna `(True, "")` o `(False, "Messaggio di errore")`.

### `get_input_mask(self) -> list[dict]`
Definisce i campi UI:
*   `name`, `type` (`string`, `number`, `boolean`, `textarea`, `select`, `select-var-test`), `label`, `required`, `options` (per select).

### `execute(self, context: ActionContext) -> tuple[int, list[str]]`
Logica principale.
*   `(status_code, traces)` con `0` successo, `1` errore.

## `ActionContext`

Oggetto tipo dizionario passato a `execute()`, con variabili risolte e info ambiente.

## Variabili di Output

Impostare durante l'esecuzione:
```python
self.output_variables['my_var'] = "value"
```
Disponibile poi come `{{my_var}}`.
