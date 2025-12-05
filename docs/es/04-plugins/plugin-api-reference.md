# Referencia API de Plugins

## Métodos de `ActionBase`

### `get_metadata(self) -> dict`
Debe devolver:
*   `name`: Nombre interno único.
*   `version`: Versión del plugin.
*   `author`: Autor.
*   `description`: Descripción corta.

### `validate_config(self, config: dict) -> tuple[bool, str]`
Verifica parámetros antes de ejecutar.
*   **Retorna**: `(True, "")` si válido, o `(False, "Mensaje de error")` si no.

### `get_input_mask(self) -> list[dict]`
Define campos UI. Cada dict:
*   `name`: Clave en config.
*   `type`: `string`, `number`, `boolean`, `textarea`, `select`, `select-var-test`.
*   `label`: Nombre a mostrar.
*   `required`: Boolean.
*   `options`: Lista de valores (para `select`).

### `execute(self, context: ActionContext) -> tuple[int, list[str]]`
Lógica principal.
*   **Retorna**: `(status_code, traces)`
    *   `status_code`: `0` éxito, `1` fallo.
    *   `traces`: Lista de cadenas (logs) para mostrar en el reporte.

## `ActionContext`

Objeto tipo diccionario pasado a `execute()`. Contiene:
*   Variables resueltas.
*   Información de entorno.

## Variables de Salida

Para definir una variable durante ejecución:
```python
self.output_variables['my_var'] = "value"
```
Estará disponible como `{{my_var}}` en acciones siguientes.
