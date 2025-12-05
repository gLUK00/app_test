# 前端开发

前端使用简单技术栈，便于维护。

## 技术

*   **模板**：Jinja2
*   **CSS**：Bootstrap 5.3（本地 `static/vendor`）
*   **JavaScript**：原生 JS + 少量 jQuery（遗留）
*   **图标**：FontAwesome 6.4（本地）

## 资源管理

无复杂构建（无 Webpack/Vite），资源直接由 `static/` 提供。

### 本地第三方库
不用 CDN，全部在 `static/vendor/`。

## 动态交互

### 模态框与表单
Bootstrap Modal 处理 “Add Variable”/“Upload File”，JS 以 AJAX 调 API。

### 实时更新
**Socket.IO** 无刷新更新界面。
*   **活动执行**：进度与日志实时。
*   **文件管理**：上传/删除后列表自动更新。

## 新页面添加

1.  在 `routes/web_routes.py` 添加路由。
2.  在 `templates/` 创建模板（继承 `base.html`）。
3.  在导航中添加链接。
