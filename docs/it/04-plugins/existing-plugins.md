# Plugin Esistenti

TestGyver include plugin built-in.

## Rete & Protocolli

### HTTP Request (`http`)
Chiamate REST.
*   **Metodi**: GET, POST, PUT, DELETE.
*   **Feature**: Header custom, body JSON, upload file.
*   **Output**: Status code, body, response time.

### SSH Command (`ssh`)
Esegue comandi remoti.
*   **Auth**: User/Password.
*   **Output**: Stdout, Stderr, Exit code.

### FTP / SFTP (`ftp`, `sftp`)
Trasferimento file.
*   **Azioni**: Upload, Download, List, Delete.

### WebDAV (`webdav`)
Interazione con server WebDAV.

## Utilities

### I/O Operations (`io`)
Manipolazione file nel workdir della campagna.
*   **Operazioni**: Crea dir, elimina file/dir, scrivi/leggi variabili su file.

### Variable Conversion (`var`)
Conversione tipi.
*   **Sorgente**: Qualsiasi variabile.
*   **Target**: int, float, bool, list, dict, json.
*   **Use case**: Parsare JSON HTTP in dizionario.

### Wait (`wait`)
Pausa per i secondi indicati.
