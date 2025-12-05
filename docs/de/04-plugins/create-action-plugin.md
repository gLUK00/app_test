# Neues Action-Plugin erstellen

So erstellst du ein Action-Plugin für TestGyver. Damit erweiterst du die App um neue Aufgaben (APIs, Dateien, DB ...).

## Voraussetzungen

*   Grundkenntnisse in Python.
*   Zugriff auf `plugins/actions/`.

## Schritte

### 1. Plugin-Datei anlegen

Erstelle eine `.py` in `plugins/actions/` mit aussagekräftigem Namen (z.B. `my_custom_action.py`).

### 2. Von `ActionBase` erben

Klasse muss `ActionBase` erben und Pflichtmethoden implementieren.

```python
from plugins.actions.action_base import ActionBase

class MyCustomAction(ActionBase):
    """Beschreibung"""
    plugin_name = "my_custom_action"
    label = "My Custom Action"
    version = "1.0.0"
    author = "Dein Name"
```

### 3. Methoden implementieren

#### `get_metadata(self)`
```python
    def get_metadata(self):
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Detailbeschreibung"
        }
```

#### `validate_config(self, config)`
```python
    def validate_config(self, config):
        if 'target_host' not in config:
            return (False, "Target host is required")
        return (True, "")
```

#### `get_input_mask(self)`
Unterstützte Typen: `string`, `number`, `boolean`, `textarea`, `select`, `checkbox`, `select-var-test`.
```python
    def get_input_mask(self):
        return [
            {"name": "target_host", "type": "string", "label": "Target Host", "placeholder": "192.168.1.1", "required": True},
            {"name": "port", "type": "number", "label": "Port", "placeholder": 8080, "required": False}
        ]
```

#### `get_output_variables(self)`
```python
    def get_output_variables(self):
        return [
            {"name": "execution_result", "description": "Resultat", "type": "string"}
        ]
```

#### `execute(self, context)`
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

### 4. Registrierung

`PluginManager` findet Plugins automatisch in `plugins/actions/`. Kein manuelles Registrieren. App neu starten.

## Best Practices

*   **Fehlerbehandlung**: try/except nutzen.
*   **Logging**: Detaillierte Traces zurückgeben.
*   **Validierung**: Streng in `validate_config`.
