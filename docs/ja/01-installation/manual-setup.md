# 手動インストール

ローカルで TestGyver をセットアップする手順です。

## 1. リポジトリをクローン

```bash
git clone <repository-url>
cd app_test
```

## 2. 仮想環境を作成

依存関係管理のため仮想環境を推奨。

```bash
python3 -m venv .venv

# 有効化
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
```

## 3. 依存をインストール

```bash
pip install -r requirements.txt
```

## 4. 設定

1.  サンプル設定をコピー（ある場合）または `configuration.json` をルートに作成。
2.  詳細は [設定ガイド](configuration.md) を参照。

## 5. DB 初期化（任意）

初期データ・インデックスを投入できます。

```bash
python init/init_database.py
```

管理者ユーザー作成:
```bash
python init/create_user.py
```

## 6. アプリを起動

```bash
export FLASK_APP=app
export FLASK_ENV=development  # 本番は 'production'

flask run --host=0.0.0.0 --port=8080
```

`http://localhost:8080` にアクセス。
