# フロントエンド開発

シンプルな技術スタックで保守性を重視。

## 技術

*   **テンプレート**: Jinja2
*   **CSS**: Bootstrap 5.3（`static/vendor` にローカル配置）
*   **JS**: プレーン JS + 少量の jQuery（レガシー）
*   **アイコン**: FontAwesome 6.4（ローカル）

## アセット管理

Webpack/Vite などのビルドなし。`static/` から直接配信。

### ローカルベンダー
CDN 不使用。すべて `static/vendor/` に配置。

## 動的インタラクション

### モーダル & フォーム
"Add Variable" や "Upload File" で Bootstrap Modal を利用。JS が AJAX で API 呼び出し。

### リアルタイム更新
**Socket.IO** でページリロードなしに更新。
*   キャンペーン実行: 進捗・ログをライブ表示。
*   ファイル管理: アップロード/削除で自動反映。

## 新しいページを追加

1.  `routes/web_routes.py` にルートを追加。
2.  `templates/` に `base.html` を継承したテンプレートを作成。
3.  ナビゲーションにリンクを追加。
