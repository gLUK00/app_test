# Existing Plugins

TestGyver comes with a set of built-in plugins.

## Network & Protocols

### HTTP Request (`http`)
Performs REST API calls.
*   **Methods**: GET, POST, PUT, DELETE.
*   **Features**: Custom headers, JSON body, file upload.
*   **Outputs**: Status code, Response body, Response time.

### SSH Command (`ssh`)
Executes shell commands on a remote server.
*   **Auth**: Username/Password.
*   **Outputs**: Stdout, Stderr, Exit code.

### FTP / SFTP (`ftp`, `sftp`)
File transfer operations.
*   **Actions**: Upload, Download, List, Delete.

### WebDAV (`webdav`)
Interacts with WebDAV servers.

## Utilities

### I/O Operations (`io`)
File system manipulation on the TestGyver server (within the campaign's workdir).
*   **Operations**: Create dir, Delete file/dir, Write/Read variables to files.

### Variable Conversion (`var`)
Converts variable types.
*   **Source**: Any variable.
*   **Targets**: int, float, bool, list, dict, json.
*   **Use Case**: Parsing a JSON string from an HTTP response into a usable dictionary.

### Wait (`wait`)
Pauses execution for a specified number of seconds.
