# Vorhandene Plugins

TestGyver bringt einige eingebaute Plugins mit.

## Netzwerk & Protokolle

### HTTP Request (`http`)
REST-Aufrufe.
*   **Methoden**: GET, POST, PUT, DELETE.
*   **Features**: Headers, JSON-Body, File-Upload.
*   **Outputs**: Statuscode, Response-Body, Response-Time.

### SSH Command (`ssh`)
Remote-Kommandos.
*   **Auth**: User/Pass.
*   **Outputs**: Stdout, Stderr, Exit-Code.

### FTP / SFTP (`ftp`, `sftp`)
Datei-Transfers.
*   **Aktionen**: Upload, Download, List, Delete.

### WebDAV (`webdav`)
Interaktion mit WebDAV-Servern.

## Utilities

### I/O Operations (`io`)
Dateisystem-Operationen im Kampagnen-Workdir.
*   **Operationen**: Ordner anlegen, Datei/Ordner löschen, Variablen in Dateien schreiben/lesen.

### Variable Conversion (`var`)
Typkonvertierung.
*   **Quelle**: Beliebige Variable.
*   **Ziele**: int, float, bool, list, dict, json.
*   **Use Case**: JSON-String aus HTTP in Dict parsen.

### Wait (`wait`)
Pausiert für angegebene Sekunden.
