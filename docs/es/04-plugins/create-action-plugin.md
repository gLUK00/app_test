# Crear un Nuevo Plugin de Acción

Guía para crear un plugin de acción en TestGyver. Permiten añadir nuevas tareas automáticas (APIs, ficheros, BD...).

## Prerrequisitos

*   Conocimientos básicos de Python.
*   Acceso a `plugins/actions/`.

## Paso a Paso

### 1. Crear el Archivo

Crea un `.py` en `plugins/actions/` con nombre descriptivo (ej. `mi_accion.py`).

### 2. Heredar de `ActionBase`

Tu clase debe heredar de `ActionBase` e implementar métodos requeridos.

```python
from plugins.actions.action_base import ActionBase

class MyCustomAction(ActionBase):
    """Descripción de la acción."""
    plugin_name = "my_custom_action"
    label = "My Custom Action"
    version = "1.0.0"
    author = "Tu Nombre"
```

### 3. Implementar Métodos

#### `get_metadata(self)`
Devuelve info básica.

```python
    def get_metadata(self):
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Descripción detallada."
        }
```

#### `validate_config(self, config)`
Valida parámetros antes de ejecutar.

```python
    def validate_config(self, config):
        if 'target_host' not in config:
            return (False, "Target host is required")
        return (True, "")
```

#### `get_input_mask(self)`
Define el formulario UI. Tipos soportados: `string`, `number`, `boolean`, `textarea`, `select`, `checkbox`, `select-var-test`.

```python
    def get_input_mask(self):
        return [
            {"name": "target_host", "type": "string", "label": "Target Host", "placeholder": "192.168.1.1", "required": True},
            {"name": "port", "type": "number", "label": "Port", "placeholder": 8080, "required": False}
        ]
```

#### `get_output_variables(self)`
Define variables de salida.

```python
    def get_output_variables(self):
        return [
            {"name": "execution_result", "description": "Resultado", "type": "string"}
        ]
```

#### `execute(self, context)`
Lógica principal. `context` expone variables y entorno.

```python
    def execute(self, context):
        host = context.get('target_host')
        try:
            # ... lógica ...
            result = "Success"
            self.output_variables['execution_result'] = result
            return (0, ["Connected to " + host, "Operation successful"])
        except Exception as e:
            return (1, [f"Error: {str(e)}"])
```

### 4. Registro

`PluginManager` descubre plugins en `plugins/actions/`. No requiere registro manual. Solo reinicia la app.

## Buenas Prácticas

*   **Errores**: Usa try/except para no romper el runner.
*   **Logging**: Devuelve trazas detalladas para depurar.
*   **Validación**: Sé estricto en `validate_config`.
