# Architettura Sistema Plugin

Sistema plugin estensibile e disaccoppiato. Aggiungi funzionalità senza toccare il core.

## Gerarchia Classi

```mermaid
classDiagram
    class PluginBase {
        <<Abstract>>
        +get_metadata()
        +validate_config()
    }
    class ActionBase {
        <<Abstract>>
        +execute(context)
        +get_input_mask()
        +get_output_variables()
    }
    class HTTPRequestAction {
        +execute()
    }
    class SSHAction {
        +execute()
    }
    
    PluginBase <|-- ActionBase
    ActionBase <|-- HTTPRequestAction
    ActionBase <|-- SSHAction
```

## Plugin Manager

`PluginManager` (`plugins/plugin_manager.py`) gestisce:
1.  **Discovery** di `plugins/actions/`.
2.  **Loading** dinamico.
3.  **Registration**: verifica eredità da `ActionBase` e registra.

## Ciclo di Vita

1.  **Startup**: `app.py` inizializza, plugin in memoria.
2.  **UI**: la UI chiede lista plugin e mask via API.
3.  **Execution**: `CampainExecutor` trova la classe, istanzia, chiama `execute()`.
