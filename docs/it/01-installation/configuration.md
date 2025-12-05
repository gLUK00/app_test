# Configurazione

L'app è configurata tramite `configuration.json` nella directory root.

## Struttura

```json
{
    "mongo": {
        "user": "root",
        "pass": "mypass",
        "host": "localhost",
        "port": "27017",
        "bdd": "testGyver",
        "prefix": "mgv_",
        "soft_delete": true
    },
    "jwt_secret": "your-secret-key",
    "app": {
        "debug": true,
        "port": 5000,
        "host": "0.0.0.0"
    },
    "pagination": {
        "page_size": 20,
        "max_page_size": 100
    },
    "security": {
        "token_expiration_minutes": 60,
        "password_min_length": 8
    },
    "workdir": "./workdir",
    "version": "1.0.0"
}
```

## Dettaglio Parametri

### Mongo
*   **user**: Utente MongoDB.
*   **pass**: Password.
*   **host**: Host DB (es: `localhost` o `mongo` in Docker).
*   **port**: Porta (default `27017`).
*   **bdd**: Nome del database.
*   **prefix**: Prefisso per le collezioni (es: `mgv_users`).
*   **soft_delete**: Se true, marca come eliminato invece di cancellare.

### Sicurezza
*   **jwt_secret**: Stringa lunga/random per JWT. **Cambiala in produzione**.
*   **token_expiration_minutes**: Durata sessione (minuti).
*   **password_min_length**: Lunghezza minima password.

### App
*   **debug**: Modalità debug Flask (auto-reload). Metti `false` in prod.
*   **port**: Porta dell'app.
*   **host**: Interfaccia (`0.0.0.0`).

### Workdir
*   **workdir**: Directory per file campagne e dati temporanei.
