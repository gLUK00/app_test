# テストとアクション

**テスト** は複数の **アクション** から成り、順に実行されます。

## テスト作成

1.  キャンペーン内で **Add Test**。
2.  名前・説明を入力。
3.  必要に応じてテスト変数を追加（例 `username`）。

## アクション追加

1.  **Add Action** をクリック。
2.  HTTP / SSH / Wait などのタイプを選択。
3.  パラメータを設定。

> **[SCREENSHOT]** HTTP アクション設定フォーム。

### 変数オートコンプリート
入力時に利用可能な変数を提案：

> **[SCREENSHOT]** `{{` 入力時のドロップダウン。

*   <span style="color:blue">**グローバル変数**</span>: `{{variable_name}}`
*   <span style="color:green">**テスト変数**</span>: `{{app.variable_name}}`
*   <span style="color:red">**コレクション変数**</span>: `{{test.test_id}}`, `{{test.files_dir}}`

### 出力変数
一部のアクションは出力を生成（例: HTTP ボディ）。
*   設定画面に **Output Variables** として表示。
*   後続アクションで利用可能。

## 実行順
リスト順に実行。ドラッグ&ドロップや矢印で並べ替え。

## 実行
テスト詳細から単体実行し、全キャンペーン前に動作確認可能。
