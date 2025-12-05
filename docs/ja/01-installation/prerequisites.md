# 前提条件

TestGyver をインストールする前に、以下を確認してください。

## システム要件

*   **OS**: Linux / macOS / Windows（WSL2 推奨）
*   **メモリ**: 推奨 2GB 以上
*   **ディスク**: 約 500MB（コード + 依存）

## ソフトウェア依存

### Python
Python 3.11 以上が必要です。
*   バージョン確認: `python --version`

### MongoDB
メイン DB として MongoDB 6.0 以上。
*   ローカルまたは Docker で利用可。
*   [MongoDB Community Server](https://www.mongodb.com/try/download/community)

### Git
リポジトリをクローンするために必要。
*   [Git ダウンロード](https://git-scm.com/downloads)

### オプション
*   **Docker / Docker Compose**: コンテナ化デプロイやテスト環境（FTP/SFTP）用に推奨。
