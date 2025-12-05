# 内置插件

TestGyver 自带一组插件。

## 网络与协议

### HTTP Request (`http`)
REST 调用。
*   **方法**：GET/POST/PUT/DELETE
*   **特性**：自定义 Header、JSON Body、文件上传
*   **输出**：状态码、响应体、耗时

### SSH Command (`ssh`)
远程命令。
*   **认证**：用户名/密码
*   **输出**：Stdout、Stderr、Exit code

### FTP / SFTP (`ftp`, `sftp`)
文件传输。
*   **操作**：Upload、Download、List、Delete

### WebDAV (`webdav`)
与 WebDAV 服务器交互。

## 工具

### I/O Operations (`io`)
在活动 workdir 内操作文件。
*   **操作**：创建目录、删除文件/目录、读写变量到文件。

### Variable Conversion (`var`)
类型转换。
*   **来源**：任意变量。
*   **目标**：int、float、bool、list、dict、json。
*   **用例**：将 HTTP 响应 JSON 字符串解析为字典。

### Wait (`wait`)
按指定秒数暂停。
