# Konfiguration

Die Anwendung wird über `configuration.json` im Root-Verzeichnis konfiguriert.

## Struktur

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
        "port": 8080,
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

## Parameterdetails

### Mongo
*   **user**: MongoDB Benutzername.
*   **pass**: Passwort.
*   **host**: Host (z.B. `localhost` oder `mongo` in Docker).
*   **port**: Port (Standard `27017`).
*   **bdd**: Name der Datenbank.
*   **prefix**: Präfix für Collections (z.B. `mgv_users`).
*   **soft_delete**: Wenn true, werden Einträge nur als gelöscht markiert.

### Sicherheit
*   **jwt_secret**: Langer zufälliger String zum Signieren von JWT. **In Produktion ändern!**
*   **token_expiration_minutes**: Sitzungsdauer in Minuten.
*   **password_min_length**: Mindestlänge für Passwörter.

### App
*   **debug**: Flask-Debug (Auto-Reload). In Produktion `false` setzen.
*   **port**: Port der Anwendung.
*   **host**: Bind-Interface (`0.0.0.0`).

### Workdir
*   **workdir**: Pfad für Kampagnen-Dateien und temporäre Daten.
