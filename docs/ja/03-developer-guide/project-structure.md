# プロジェクト構成

```text
/
├── app.py                  # エントリーポイント
├── configuration.json      # 設定
├── Dockerfile              # コンテナ定義
├── requirements.txt        # 依存
├── docs/                   # ドキュメント
├── init/                   # 初期化スクリプト
├── models/                 # Mongo モデル
├── plugins/                # プラグインシステム
│   ├── actions/            # アクション実装
│   ├── plugin_base.py      # ベースクラス
│   └── plugin_manager.py   # プラグイン検出
├── routes/                 # API / Web ルート
├── static/                 # 静的アセット
├── templates/              # Jinja2 テンプレート
├── translations/           # i18n 翻訳
├── utils/                  # ヘルパー/コアロジック
└── workdir/                # 実行時ストレージ
```

## 主要ディレクトリ

*   **`models/`**: MongoDB ドキュメントと CRUD。
*   **`routes/`**: モジュール単位のロジック（Auth, API, Web UI）。
*   **`plugins/actions/`**: 新機能を追加する場所。
*   **`utils/`**: コア処理（`campain_executor.py` など）。
