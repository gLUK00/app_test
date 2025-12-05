# Plugins Existentes

TestGyver incluye varios plugins incorporados.

## Red y Protocolos

### HTTP Request (`http`)
Hace llamadas REST.
*   **Métodos**: GET, POST, PUT, DELETE.
*   **Características**: Cabeceras personalizadas, cuerpo JSON, subida de ficheros.
*   **Outputs**: Código de estado, cuerpo de respuesta, tiempo de respuesta.

### SSH Command (`ssh`)
Ejecuta comandos remotos.
*   **Auth**: Usuario/Contraseña.
*   **Outputs**: Stdout, Stderr, Exit code.

### FTP / SFTP (`ftp`, `sftp`)
Operaciones de transferencia.
*   **Acciones**: Upload, Download, List, Delete.

### WebDAV (`webdav`)
Interacción con servidores WebDAV.

## Utilidades

### I/O Operations (`io`)
Manipulación de ficheros en el servidor (workdir de la campaña).
*   **Operaciones**: Crear dir, borrar fichero/dir, escribir/leer variables en ficheros.

### Variable Conversion (`var`)
Convierte tipos de variables.
*   **Origen**: Cualquier variable.
*   **Destino**: int, float, bool, list, dict, json.
*   **Caso de uso**: Parsear JSON de una respuesta HTTP a diccionario.

### Wait (`wait`)
Pausa ejecución los segundos indicados.
