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

## Probando tu Plugin

Para facilitar el desarrollo y las pruebas de tus plugins, un entorno local completo está disponible a través de Docker Compose.

### 1. Iniciar el Entorno de Pruebas

Se proporciona un archivo `test-docker-compose.yml` en el directorio `init/`. Configura varios servicios (FTP, SFTP, WebDAV, SSH, S3/MinIO, API HTTP) para probar tus acciones contra objetivos reales.

```bash
sudo docker-compose -f init/test-docker-compose.yml up -d
```

### 2. Importar Datos de Prueba

Para poblar rápidamente tu instancia de TestGyver con una campaña de prueba completa que cubra todas las acciones estándar:

1.  Ve a la página **Campañas** en la aplicación.
2.  Haz clic en **Importar**.
3.  Selecciona el archivo `init/campain_All_tests.json`.

Esta campaña contiene ejemplos de cómo configurar acciones para interactuar con los servicios proporcionados por el entorno de prueba.

### 3. Importar Variables de Entorno

La campaña de prueba depende de variables específicas (nombres de host, credenciales, etc.). Puedes importarlas automáticamente usando el script proporcionado.

Asegúrate de que tu entorno virtual esté activo, luego ejecuta:

```bash
python import_variables.py init/import-var-test-docker.json
```

Esto creará las variables necesarias en el entorno "Global" (o el definido en el archivo JSON) para coincidir con la configuración de `test-docker-compose.yml`.
