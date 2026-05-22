# Creare un Nuovo Plugin di Azione

Guida per creare un plugin di azione in TestGyver (API, file, DB...).

## Prerequisiti

*   Conoscenza base Python.
*   Accesso a `plugins/actions/`.

## Passi

### 1. Crea il file

File `.py` in `plugins/actions/` con nome descrittivo (es. `mia_azione.py`).

### 2. Eredita da `ActionBase`

```python
from plugins.actions.action_base import ActionBase

class MyCustomAction(ActionBase):
    """Descrizione"""
    plugin_name = "my_custom_action"
    label = "My Custom Action"
    version = "1.0.0"
    author = "Il tuo nome"
```

### 3. Implementa i metodi

#### `get_metadata(self)`
```python
    def get_metadata(self):
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Descrizione dettagliata."
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
Tipi: `string`, `number`, `boolean`, `textarea`, `select`, `checkbox`, `select-var-test`.
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
            {"name": "execution_result", "description": "Risultato", "type": "string"}
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

### 4. Registrazione

`PluginManager` scopre i plugin in `plugins/actions/`. Nessuna registrazione manuale. Riavvia l'app.

## Best Practice

*   **Error handling**: try/except.
*   **Logging**: tracce dettagliate.
*   **Validazione**: sii rigoroso in `validate_config`.

## Testare il Tuo Plugin

Per facilitare lo sviluppo e il test dei tuoi plugin, è disponibile un ambiente locale completo tramite Docker Compose.

### 1. Avviare l'Ambiente di Test

Un file `test-docker-compose.yml` è fornito nella directory `init/`. Configura vari servizi (FTP, SFTP, WebDAV, SSH, S3/MinIO, API HTTP) per testare le tue azioni contro obiettivi reali.

```bash
sudo docker compose -f init/test-docker-compose.yml up -d
```

### 2. Importare i Dati di Test

Per popolare rapidamente la tua istanza TestGyver con una campagna di test completa che copre tutte le azioni standard:

1.  Vai alla pagina **Campagne** nell'applicazione.
2.  Clicca su **Importa**.
3.  Seleziona il file `init/campain_All_tests.json`.

Questa campagna contiene esempi di come configurare le azioni per interagire con i servizi forniti dall'ambiente di test.

### 3. Importare le Variabili d'Ambiente

La campagna di test si basa su variabili specifiche (nomi host, credenziali, ecc.). Puoi importarle automaticamente utilizzando lo script fornito.

Assicurati che il tuo ambiente virtuale sia attivo, quindi esegui:

```bash
python import_variables.py init/import-var-test-docker.json
```

Questo creerà le variabili necessarie nell'ambiente "Global" (o quello definito nel file JSON) per corrispondere alla configurazione di `test-docker-compose.yml`.
