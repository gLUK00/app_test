# 設定

ルートにある `configuration.json` でアプリを設定します。

## 構造

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

## パラメータ

### Mongo
*   **user**: MongoDB ユーザー
*   **pass**: パスワード
*   **host**: DB ホスト（例 `localhost` や Docker の `mongo`）
*   **port**: ポート（デフォルト `27017`）
*   **bdd**: DB 名
*   **prefix**: コレクション接頭辞（例 `mgv_users`）
*   **soft_delete**: true なら論理削除

### セキュリティ
*   **jwt_secret**: JWT 署名キー。**本番で必ず変更**
*   **token_expiration_minutes**: セッション有効時間
*   **password_min_length**: パスワード最小長

### アプリ
*   **debug**: Flask デバッグ（自動リロード）。本番は false
*   **port**: ポート
*   **host**: バインド先（`0.0.0.0`）

### Workdir
*   **workdir**: キャンペーンファイル・一時データ保存先
