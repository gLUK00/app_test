# 既存プラグイン

TestGyver には組み込みプラグインが含まれます。

## ネットワーク & プロトコル

### HTTP Request (`http`)
REST 呼び出し。
*   **メソッド**: GET / POST / PUT / DELETE
*   **機能**: カスタムヘッダ、JSON ボディ、ファイルアップロード
*   **出力**: ステータスコード、レスポンスボディ、応答時間

### SSH Command (`ssh`)
リモートコマンド実行。
*   **認証**: ユーザー/パスワード
*   **出力**: Stdout, Stderr, Exit code

### FTP / SFTP (`ftp`, `sftp`)
ファイル転送。
*   **操作**: Upload, Download, List, Delete

### WebDAV (`webdav`)
WebDAV サーバーとのやり取り。

## ユーティリティ

### I/O Operations (`io`)
キャンペーン workdir 内のファイル操作。
*   **操作**: ディレクトリ作成、ファイル/ディレクトリ削除、変数の書込/読込。

### Variable Conversion (`var`)
型変換。
*   **入力**: 任意の変数
*   **出力**: int, float, bool, list, dict, json
*   **用途**: HTTP レスポンスの JSON 文字列を辞書化

### Wait (`wait`)
指定秒数の待機。
