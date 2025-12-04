import os
import sys
from babel.messages import pofile

# Dictionary of translations
# msgid -> {lang: translation}
TRANSLATIONS = {
    "Format d'email invalide": {
        "en": "Invalid email format",
        "es": "Formato de correo electrónico inválido",
        "de": "Ungültiges E-Mail-Format",
        "zh": "无效的电子邮件格式",
        "ja": "無効なメール形式"
    },
    "Rôle invalide. Doit être 'admin' ou 'user'": {
        "en": "Invalid role. Must be 'admin' or 'user'",
        "es": "Rol inválido. Debe ser 'admin' o 'user'",
        "de": "Ungültige Rolle. Muss 'admin' oder 'user' sein",
        "zh": "无效的角色。必须是 'admin' 或 'user'",
        "ja": "無効な役割です。'admin' または 'user' である必要があります"
    },
    "Cet email est déjà utilisé": {
        "en": "This email is already in use",
        "es": "Este correo electrónico ya está en uso",
        "de": "Diese E-Mail wird bereits verwendet",
        "zh": "此电子邮件已被使用",
        "ja": "このメールアドレスは既に使用されています"
    },
    "Rôle invalide": {
        "en": "Invalid role",
        "es": "Rol inválido",
        "de": "Ungültige Rolle",
        "zh": "无效的角色",
        "ja": "無効な役割"
    },
    "Email ou mot de passe incorrect": {
        "en": "Incorrect email or password",
        "es": "Correo electrónico o contraseña incorrectos",
        "de": "E-Mail oder Passwort falsch",
        "zh": "电子邮件或密码不正确",
        "ja": "メールアドレスまたはパスワードが間違っています"
    },
    "Authentification réussie": {
        "en": "Authentication successful",
        "es": "Autenticación exitosa",
        "de": "Authentifizierung erfolgreich",
        "zh": "验证成功",
        "ja": "認証に成功しました"
    },
    "Erreur serveur: {}": {
        "en": "Server error: {}",
        "es": "Error del servidor: {}",
        "de": "Serverfehler: {}",
        "zh": "服务器错误：{}",
        "ja": "サーバーエラー：{}"
    },
    "Campagne créée avec succès": {
        "en": "Campaign created successfully",
        "es": "Campaña creada con éxito",
        "de": "Kampagne erfolgreich erstellt",
        "zh": "活动创建成功",
        "ja": "キャンペーンが正常に作成されました"
    },
    "Campagne non trouvée": {
        "en": "Campaign not found",
        "es": "Campaña no encontrada",
        "de": "Kampagne nicht gefunden",
        "zh": "未找到活动",
        "ja": "キャンペーンが見つかりません"
    },
    "Campagne mise à jour avec succès": {
        "en": "Campaign updated successfully",
        "es": "Campaña actualizada con éxito",
        "de": "Kampagne erfolgreich aktualisiert",
        "zh": "活动更新成功",
        "ja": "キャンペーンが正常に更新されました"
    },
    "Erreur serveur: %(error)s": {
        "en": "Server error: %(error)s",
        "es": "Error del servidor: %(error)s",
        "de": "Serverfehler: %(error)s",
        "zh": "服务器错误：%(error)s",
        "ja": "サーバーエラー：%(error)s"
    },
    "Test créé avec succès": {
        "en": "Test created successfully",
        "es": "Prueba creada con éxito",
        "de": "Test erfolgreich erstellt",
        "zh": "测试创建成功",
        "ja": "テストが正常に作成されました"
    },
    "Test non trouvé": {
        "en": "Test not found",
        "es": "Prueba no encontrada",
        "de": "Test nicht gefunden",
        "zh": "未找到测试",
        "ja": "テストが見つかりません"
    },
    "Test mis à jour avec succès": {
        "en": "Test updated successfully",
        "es": "Prueba actualizada con éxito",
        "de": "Test erfolgreich aktualisiert",
        "zh": "测试更新成功",
        "ja": "テストが正常に更新されました"
    },
    "Test supprimé avec succès": {
        "en": "Test deleted successfully",
        "es": "Prueba eliminada con éxito",
        "de": "Test erfolgreich gelöscht",
        "zh": "测试删除成功",
        "ja": "テストが正常に削除されました"
    },
    "Action ajoutée avec succès": {
        "en": "Action added successfully",
        "es": "Acción añadida con éxito",
        "de": "Aktion erfolgreich hinzugefügt",
        "zh": "操作添加成功",
        "ja": "アクションが正常に追加されました"
    },
    "Exécuteur de test non disponible": {
        "en": "Test executor not available",
        "es": "Ejecutor de pruebas no disponible",
        "de": "Testausführer nicht verfügbar",
        "zh": "测试执行器不可用",
        "ja": "テスト実行プログラムが利用できません"
    },
    "Exécution du test lancée": {
        "en": "Test execution started",
        "es": "Ejecución de prueba iniciada",
        "de": "Testausführung gestartet",
        "zh": "测试执行已开始",
        "ja": "テストの実行が開始されました"
    },
    "Impossible de déplacer le test (déjà en première position ou test introuvable)": {
        "en": "Cannot move test (already in first position or test not found)",
        "es": "No se puede mover la prueba (ya está en la primera posición o no se encuentra)",
        "de": "Test kann nicht verschoben werden (bereits an erster Stelle oder nicht gefunden)",
        "zh": "无法移动测试（已在第一个位置或未找到测试）",
        "ja": "テストを移動できません（既に最初の位置にあるか、テストが見つかりません）"
    },
    "Test déplacé vers le haut avec succès": {
        "en": "Test moved up successfully",
        "es": "Prueba movida hacia arriba con éxito",
        "de": "Test erfolgreich nach oben verschoben",
        "zh": "测试成功上移",
        "ja": "テストが正常に上に移動しました"
    },
    "Impossible de déplacer le test (déjà en dernière position ou test introuvable)": {
        "en": "Cannot move test (already in last position or test not found)",
        "es": "No se puede mover la prueba (ya está en la última posición o no se encuentra)",
        "de": "Test kann nicht verschoben werden (bereits an letzter Stelle oder nicht gefunden)",
        "zh": "无法移动测试（已在最后一个位置或未找到测试）",
        "ja": "テストを移動できません（既に最後の位置にあるか、テストが見つかりません）"
    },
    "Test déplacé vers le bas avec succès": {
        "en": "Test moved down successfully",
        "es": "Prueba movida hacia abajo con éxito",
        "de": "Test erfolgreich nach unten verschoben",
        "zh": "测试成功下移",
        "ja": "テストが正常に下に移動しました"
    },
    "Utilisateur créé avec succès": {
        "en": "User created successfully",
        "es": "Usuario creado con éxito",
        "de": "Benutzer erfolgreich erstellt",
        "zh": "用户创建成功",
        "ja": "ユーザーが正常に作成されました"
    },
    "Tableau de bord": {
        "en": "Dashboard",
        "es": "Panel de control",
        "de": "Dashboard",
        "zh": "仪表板",
        "ja": "ダッシュボード"
    },
    "Administration": {
        "en": "Administration",
        "es": "Administración",
        "de": "Verwaltung",
        "zh": "管理",
        "ja": "管理"
    },
    "Utilisateurs": {
        "en": "Users",
        "es": "Usuarios",
        "de": "Benutzer",
        "zh": "用户",
        "ja": "ユーザー"
    },
    "Variables": {
        "en": "Variables",
        "es": "Variables",
        "de": "Variablen",
        "zh": "变量",
        "ja": "変数"
    },
    "Éléments supprimés": {
        "en": "Deleted Items",
        "es": "Elementos eliminados",
        "de": "Gelöschte Elemente",
        "zh": "已删除的项目",
        "ja": "削除されたアイテム"
    },
    "Déconnexion": {
        "en": "Logout",
        "es": "Cerrar sesión",
        "de": "Abmelden",
        "zh": "注销",
        "ja": "ログアウト"
    },
    "Gestion des campagnes": {
        "en": "Campaign Management",
        "es": "Gestión de campañas",
        "de": "Kampagnenverwaltung",
        "zh": "活动管理",
        "ja": "キャンペーン管理"
    },
    "Nouvelle campagne": {
        "en": "New Campaign",
        "es": "Nueva campaña",
        "de": "Neue Kampagne",
        "zh": "新活动",
        "ja": "新しいキャンペーン"
    },
    "Retour": {
        "en": "Back",
        "es": "Volver",
        "de": "Zurück",
        "zh": "返回",
        "ja": "戻る"
    },
    "Informations de la campagne": {
        "en": "Campaign Information",
        "es": "Información de la campaña",
        "de": "Kampagneninformationen",
        "zh": "活动信息",
        "ja": "キャンペーン情報"
    },
    "Nom de la campagne": {
        "en": "Campaign Name",
        "es": "Nombre de la campaña",
        "de": "Kampagnenname",
        "zh": "活动名称",
        "ja": "キャンペーン名"
    },
    "Description": {
        "en": "Description",
        "es": "Descripción",
        "de": "Beschreibung",
        "zh": "描述",
        "ja": "説明"
    },
    "Créer la campagne": {
        "en": "Create Campaign",
        "es": "Crear campaña",
        "de": "Kampagne erstellen",
        "zh": "创建活动",
        "ja": "キャンペーンを作成"
    },
    "Détails de la campagne": {
        "en": "Campaign Details",
        "es": "Detalles de la campaña",
        "de": "Kampagnendetails",
        "zh": "活动详情",
        "ja": "キャンペーンの詳細"
    },
    "Chargement...": {
        "en": "Loading...",
        "es": "Cargando...",
        "de": "Laden...",
        "zh": "正在加载...",
        "ja": "読み込み中..."
    },
    "Renommer la campagne": {
        "en": "Rename Campaign",
        "es": "Renombrar campaña",
        "de": "Kampagne umbenennen",
        "zh": "重命名活动",
        "ja": "キャンペーンの名前を変更"
    },
    "Exporter la campagne": {
        "en": "Export Campaign",
        "es": "Exportar campaña",
        "de": "Kampagne exportieren",
        "zh": "导出活动",
        "ja": "キャンペーンをエクスポート"
    },
    "Informations": {
        "en": "Information",
        "es": "Información",
        "de": "Informationen",
        "zh": "信息",
        "ja": "情報"
    },
    "Nom :": {
        "en": "Name:",
        "es": "Nombre:",
        "de": "Name:",
        "zh": "名称：",
        "ja": "名前："
    },
    "Description :": {
        "en": "Description:",
        "es": "Descripción:",
        "de": "Beschreibung:",
        "zh": "描述：",
        "ja": "説明："
    },
    "Créée le :": {
        "en": "Created on:",
        "es": "Creado el:",
        "de": "Erstellt am:",
        "zh": "创建于：",
        "ja": "作成日："
    },
    "Créée par :": {
        "en": "Created by:",
        "es": "Creado por:",
        "de": "Erstellt von:",
        "zh": "创建者：",
        "ja": "作成者："
    },
    "Fichiers": {
        "en": "Files",
        "es": "Archivos",
        "de": "Dateien",
        "zh": "文件",
        "ja": "ファイル"
    },
    "Ajouter un fichier": {
        "en": "Add File",
        "es": "Añadir archivo",
        "de": "Datei hinzufügen",
        "zh": "添加文件",
        "ja": "ファイルを追加"
    },
    "Nom du fichier": {
        "en": "Filename",
        "es": "Nombre del archivo",
        "de": "Dateiname",
        "zh": "文件名",
        "ja": "ファイル名"
    },
    "Taille (Ko)": {
        "en": "Size (KB)",
        "es": "Tamaño (KB)",
        "de": "Größe (KB)",
        "zh": "大小 (KB)",
        "ja": "サイズ (KB)"
    },
    "Date de modification": {
        "en": "Modification Date",
        "es": "Fecha de modificación",
        "de": "Änderungsdatum",
        "zh": "修改日期",
        "ja": "更新日"
    },
    "Actions": {
        "en": "Actions",
        "es": "Acciones",
        "de": "Aktionen",
        "zh": "操作",
        "ja": "アクション"
    },
    "Aucun fichier dans cette campagne": {
        "en": "No files in this campaign",
        "es": "No hay archivos en esta campaña",
        "de": "Keine Dateien in dieser Kampagne",
        "zh": "此活动中没有文件",
        "ja": "このキャンペーンにはファイルがありません"
    },
    "Tests de la campagne": {
        "en": "Campaign Tests",
        "es": "Pruebas de la campaña",
        "de": "Kampagnentests",
        "zh": "活动测试",
        "ja": "キャンペーンのテスト"
    },
    "Ajouter un test": {
        "en": "Add Test",
        "es": "Añadir prueba",
        "de": "Test hinzufügen",
        "zh": "添加测试",
        "ja": "テストを追加"
    },
    "Bienvenue sur votre espace de gestion des campagnes de tests": {
        "en": "Welcome to your test campaign management area",
        "es": "Bienvenido a su área de gestión de campañas de prueba",
        "de": "Willkommen in Ihrem Testkampagnen-Management-Bereich",
        "zh": "欢迎来到您的测试活动管理区",
        "ja": "テストキャンペーン管理エリアへようこそ"
    },
    "Importer une campagne": {
        "en": "Import Campaign",
        "es": "Importar campaña",
        "de": "Kampagne importieren",
        "zh": "导入活动",
        "ja": "キャンペーンをインポート"
    },
    "Campagnes de tests": {
        "en": "Test Campaigns",
        "es": "Campañas de prueba",
        "de": "Testkampagnen",
        "zh": "测试活动",
        "ja": "テストキャンペーン"
    },
    "Fichier JSON": {
        "en": "JSON File",
        "es": "Archivo JSON",
        "de": "JSON-Datei",
        "zh": "JSON 文件",
        "ja": "JSON ファイル"
    },
    "Sélectionnez un fichier exporté précédemment (.json)": {
        "en": "Select a previously exported file (.json)",
        "es": "Seleccione un archivo exportado anteriormente (.json)",
        "de": "Wählen Sie eine zuvor exportierte Datei (.json)",
        "zh": "选择以前导出的文件 (.json)",
        "ja": "以前にエクスポートしたファイル (.json) を選択してください"
    },
    "Laisser vide pour utiliser le nom par défaut": {
        "en": "Leave empty to use default name",
        "es": "Dejar vacío para usar el nombre predeterminado",
        "de": "Leer lassen, um den Standardnamen zu verwenden",
        "zh": "留空以使用默认名称",
        "ja": "デフォルト名を使用する場合は空のままにしてください"
    },
    "Par défaut : \"Import de [Nom original]\"": {
        "en": "Default: \"Import of [Original Name]\"",
        "es": "Predeterminado: \"Importación de [Nombre original]\"",
        "de": "Standard: \"Import von [Originalname]\"",
        "zh": "默认：“[原始名称] 的导入”",
        "ja": "デフォルト：「[元の名前] のインポート」"
    },
    "Annuler": {
        "en": "Cancel",
        "es": "Cancelar",
        "de": "Abbrechen",
        "zh": "取消",
        "ja": "キャンセル"
    },
    "Importer": {
        "en": "Import",
        "es": "Importar",
        "de": "Importieren",
        "zh": "导入",
        "ja": "インポート"
    },
    "En cours": {
        "en": "In Progress",
        "es": "En curso",
        "de": "In Bearbeitung",
        "zh": "进行中",
        "ja": "進行中"
    },
    "Réussi": {
        "en": "Passed",
        "es": "Aprobado",
        "de": "Bestanden",
        "zh": "通过",
        "ja": "成功"
    },
    "Échoué": {
        "en": "Failed",
        "es": "Fallido",
        "de": "Fehlgeschlagen",
        "zh": "失败",
        "ja": "失敗"
    },
    "Ignoré": {
        "en": "Skipped",
        "es": "Omitido",
        "de": "Übersprungen",
        "zh": "跳过",
        "ja": "スキップ"
    },
    "En attente": {
        "en": "Pending",
        "es": "Pendiente",
        "de": "Ausstehend",
        "zh": "待定",
        "ja": "保留中"
    },
    "Terminé": {
        "en": "Completed",
        "es": "Completado",
        "de": "Abgeschlossen",
        "zh": "已完成",
        "ja": "完了"
    },
    "Gestion des éléments supprimés": {
        "en": "Deleted Items Management",
        "es": "Gestión de elementos eliminados",
        "de": "Verwaltung gelöschter Elemente",
        "zh": "已删除项目管理",
        "ja": "削除されたアイテムの管理"
    },
    "Tests": {
        "en": "Tests",
        "es": "Pruebas",
        "de": "Tests",
        "zh": "测试",
        "ja": "テスト"
    },
    "Campagnes": {
        "en": "Campaigns",
        "es": "Campañas",
        "de": "Kampagnen",
        "zh": "活动",
        "ja": "キャンペーン"
    },
    "Rapports": {
        "en": "Reports",
        "es": "Informes",
        "de": "Berichte",
        "zh": "报告",
        "ja": "レポート"
    },
    "Tests supprimés": {
        "en": "Deleted Tests",
        "es": "Pruebas eliminadas",
        "de": "Gelöschte Tests",
        "zh": "已删除的测试",
        "ja": "削除されたテスト"
    },
    "Restaurer sélection": {
        "en": "Restore Selection",
        "es": "Restaurar selección",
        "de": "Auswahl wiederherstellen",
        "zh": "恢复选择",
        "ja": "選択を復元"
    },
    "Supprimer définitivement": {
        "en": "Permanently Delete",
        "es": "Eliminar permanentemente",
        "de": "Endgültig löschen",
        "zh": "永久删除",
        "ja": "完全に削除"
    },
    "Campagnes supprimées": {
        "en": "Deleted Campaigns",
        "es": "Campañas eliminadas",
        "de": "Gelöschte Kampagnen",
        "zh": "已删除的活动",
        "ja": "削除されたキャンペーン"
    },
    "Rapports supprimés": {
        "en": "Deleted Reports",
        "es": "Informes eliminados",
        "de": "Gelöschte Berichte",
        "zh": "已删除的报告",
        "ja": "削除されたレポート"
    },
    "Nouvel utilisateur": {
        "en": "New User",
        "es": "Nuevo usuario",
        "de": "Neuer Benutzer",
        "zh": "新用户",
        "ja": "新しいユーザー"
    },
    "Informations de l'utilisateur": {
        "en": "User Information",
        "es": "Información del usuario",
        "de": "Benutzerinformationen",
        "zh": "用户信息",
        "ja": "ユーザー情報"
    },
    "Nom complet *": {
        "en": "Full Name *",
        "es": "Nombre completo *",
        "de": "Vollständiger Name *",
        "zh": "全名 *",
        "ja": "氏名 *"
    },
    "Ex: Jean Dupont": {
        "en": "Ex: John Doe",
        "es": "Ej: Juan Pérez",
        "de": "Bsp: Max Mustermann",
        "zh": "例如：张三",
        "ja": "例：山田 太郎"
    },
    "Email *": {
        "en": "Email *",
        "es": "Correo electrónico *",
        "de": "E-Mail *",
        "zh": "电子邮件 *",
        "ja": "メールアドレス *"
    },
    "Ex: jean.dupont@example.com": {
        "en": "Ex: john.doe@example.com",
        "es": "Ej: juan.perez@example.com",
        "de": "Bsp: max.mustermann@example.com",
        "zh": "例如：zhang.san@example.com",
        "ja": "例：yamada.taro@example.com"
    },
    "L'adresse email servira d'identifiant de connexion": {
        "en": "The email address will be used as the login ID",
        "es": "La dirección de correo electrónico se utilizará como ID de inicio de sesión",
        "de": "Die E-Mail-Adresse wird als Anmelde-ID verwendet",
        "zh": "电子邮件地址将用作登录 ID",
        "ja": "メールアドレスはログインIDとして使用されます"
    },
    "Mot de passe *": {
        "en": "Password *",
        "es": "Contraseña *",
        "de": "Passwort *",
        "zh": "密码 *",
        "ja": "パスワード *"
    },
    "Minimum 8 caractères": {
        "en": "Minimum 8 characters",
        "es": "Mínimo 8 caracteres",
        "de": "Mindestens 8 Zeichen",
        "zh": "至少 8 个字符",
        "ja": "8文字以上"
    },
    "Le mot de passe doit contenir au moins 8 caractères": {
        "en": "The password must contain at least 8 characters",
        "es": "La contraseña debe contener al menos 8 caracteres",
        "de": "Das Passwort muss mindestens 8 Zeichen enthalten",
        "zh": "密码必须包含至少 8 个字符",
        "ja": "パスワードは8文字以上である必要があります"
    },
    "Confirmer le mot de passe *": {
        "en": "Confirm Password *",
        "es": "Confirmar contraseña *",
        "de": "Passwort bestätigen *",
        "zh": "确认密码 *",
        "ja": "パスワードの確認 *"
    },
    "Ressaisir le mot de passe": {
        "en": "Re-enter password",
        "es": "Vuelva a introducir la contraseña",
        "de": "Passwort erneut eingeben",
        "zh": "重新输入密码",
        "ja": "パスワードを再入力してください"
    },
    "Rôle *": {
        "en": "Role *",
        "es": "Rol *",
        "de": "Rolle *",
        "zh": "角色 *",
        "ja": "役割 *"
    },
    "Les administrateurs ont accès à toutes les fonctionnalités": {
        "en": "Administrators have access to all features",
        "es": "Los administradores tienen acceso a todas las funciones",
        "de": "Administratoren haben Zugriff auf alle Funktionen",
        "zh": "管理员可以访问所有功能",
        "ja": "管理者はすべての機能にアクセスできます"
    },
    "Créer l'utilisateur": {
        "en": "Create User",
        "es": "Crear usuario",
        "de": "Benutzer erstellen",
        "zh": "创建用户",
        "ja": "ユーザーを作成"
    },
    "Les mots de passe ne correspondent pas": {
        "en": "Passwords do not match",
        "es": "Las contraseñas no coinciden",
        "de": "Passwörter stimmen nicht überein",
        "zh": "密码不匹配",
        "ja": "パスワードが一致しません"
    },
    "Modifier l'utilisateur": {
        "en": "Edit User",
        "es": "Editar usuario",
        "de": "Benutzer bearbeiten",
        "zh": "编辑用户",
        "ja": "ユーザーを編集"
    },
    "Chargement des données...": {
        "en": "Loading data...",
        "es": "Cargando datos...",
        "de": "Daten werden geladen...",
        "zh": "正在加载数据...",
        "ja": "データを読み込んでいます..."
    },
    "L'adresse email sert d'identifiant de connexion": {
        "en": "The email address serves as the login ID",
        "es": "La dirección de correo electrónico sirve como ID de inicio de sesión",
        "de": "Die E-Mail-Adresse dient als Anmelde-ID",
        "zh": "电子邮件地址用作登录 ID",
        "ja": "メールアドレスはログインIDとして機能します"
    },
    "Modifier le mot de passe de l'utilisateur": {
        "en": "Change user password",
        "es": "Cambiar contraseña de usuario",
        "de": "Benutzerpasswort ändern",
        "zh": "更改用户密码",
        "ja": "ユーザーパスワードを変更"
    },
    "Nouveau mot de passe": {
        "en": "New Password",
        "es": "Nueva contraseña",
        "de": "Neues Passwort",
        "zh": "新密码",
        "ja": "新しいパスワード"
    },
    "Saisissez le nouveau mot de passe pour cet utilisateur": {
        "en": "Enter the new password for this user",
        "es": "Introduzca la nueva contraseña para este usuario",
        "de": "Geben Sie das neue Passwort für diesen Benutzer ein",
        "zh": "输入此用户的新密码",
        "ja": "このユーザーの新しいパスワードを入力してください"
    },
    "Nouveau mot de passe *": {
        "en": "New Password *",
        "es": "Nueva contraseña *",
        "de": "Neues Passwort *",
        "zh": "新密码 *",
        "ja": "新しいパスワード *"
    },
    "Confirmer le nouveau mot de passe *": {
        "en": "Confirm New Password *",
        "es": "Confirmar nueva contraseña *",
        "de": "Neues Passwort bestätigen *",
        "zh": "确认新密码 *",
        "ja": "新しいパスワードを確認 *"
    },
    "Enregistrer les modifications": {
        "en": "Save Changes",
        "es": "Guardar cambios",
        "de": "Änderungen speichern",
        "zh": "保存更改",
        "ja": "変更を保存"
    },
    "Gestion des utilisateurs": {
        "en": "User Management",
        "es": "Gestión de usuarios",
        "de": "Benutzerverwaltung",
        "zh": "用户管理",
        "ja": "ユーザー管理"
    },
    "Liste des utilisateurs": {
        "en": "User List",
        "es": "Lista de usuarios",
        "de": "Benutzerliste",
        "zh": "用户列表",
        "ja": "ユーザーリスト"
    },
    "Nom": {
        "en": "Name",
        "es": "Nombre",
        "de": "Name",
        "zh": "名称",
        "ja": "名前"
    },
    "Rôle": {
        "en": "Role",
        "es": "Rol",
        "de": "Rolle",
        "zh": "角色",
        "ja": "役割"
    },
    "Nouvelle variable": {
        "en": "New Variable",
        "es": "Nueva variable",
        "de": "Neue Variable",
        "zh": "新变量",
        "ja": "新しい変数"
    },
    "Informations de la variable": {
        "en": "Variable Information",
        "es": "Información de la variable",
        "de": "Variableninformationen",
        "zh": "变量信息",
        "ja": "変数情報"
    },
    "Clé de la variable *": {
        "en": "Variable Key *",
        "es": "Clave de la variable *",
        "de": "Variablenschlüssel *",
        "zh": "变量键 *",
        "ja": "変数キー *"
    },
    "Ex: API_URL, DATABASE_HOST": {
        "en": "Ex: API_URL, DATABASE_HOST",
        "es": "Ej: API_URL, DATABASE_HOST",
        "de": "Bsp: API_URL, DATABASE_HOST",
        "zh": "例如：API_URL, DATABASE_HOST",
        "ja": "例：API_URL, DATABASE_HOST"
    },
    "Le nom unique de la variable (généralement en MAJUSCULES)": {
        "en": "The unique name of the variable (usually in UPPERCASE)",
        "es": "El nombre único de la variable (generalmente en MAYÚSCULAS)",
        "de": "Der eindeutige Name der Variable (normalerweise in GROSSBUCHSTABEN)",
        "zh": "变量的唯一名称（通常为大写）",
        "ja": "変数の固有名（通常は大文字）"
    },
    "Valeur *": {
        "en": "Value *",
        "es": "Valor *",
        "de": "Wert *",
        "zh": "值 *",
        "ja": "値 *"
    },
    "Ex: https://api.example.com": {
        "en": "Ex: https://api.example.com",
        "es": "Ej: https://api.example.com",
        "de": "Bsp: https://api.example.com",
        "zh": "例如：https://api.example.com",
        "ja": "例：https://api.example.com"
    },
    "Environnement (filière) *": {
        "en": "Environment (Branch) *",
        "es": "Entorno (Rama) *",
        "de": "Umgebung (Zweig) *",
        "zh": "环境（分支）*",
        "ja": "環境（ブランチ）*"
    },
    "Ex: DEV, TEST, STAGING, PROD": {
        "en": "Ex: DEV, TEST, STAGING, PROD",
        "es": "Ej: DEV, TEST, STAGING, PROD",
        "de": "Bsp: DEV, TEST, STAGING, PROD",
        "zh": "例如：DEV, TEST, STAGING, PROD",
        "ja": "例：DEV, TEST, STAGING, PROD"
    },
    "Description de la variable et son utilisation": {
        "en": "Description of the variable and its usage",
        "es": "Descripción de la variable y su uso",
        "de": "Beschreibung der Variable und ihrer Verwendung",
        "zh": "变量及其用法的描述",
        "ja": "変数とその使用法の説明"
    },
    "Variable racine (privilèges élevés)": {
        "en": "Root Variable (Elevated Privileges)",
        "es": "Variable raíz (privilegios elevados)",
        "de": "Root-Variable (erhöhte Rechte)",
        "zh": "根变量（提升的权限）",
        "ja": "ルート変数（昇格された権限）"
    },
    "Cochez cette option si la variable nécessite des privilèges administrateur": {
        "en": "Check this option if the variable requires administrator privileges",
        "es": "Marque esta opción si la variable requiere privilegios de administrador",
        "de": "Aktivieren Sie diese Option, wenn die Variable Administratorrechte erfordert",
        "zh": "如果变量需要管理员权限，请选中此选项",
        "ja": "変数が管理者権限を必要とする場合は、このオプションをオンにしてください"
    },
    "Créer la variable": {
        "en": "Create Variable",
        "es": "Crear variable",
        "de": "Variable erstellen",
        "zh": "创建变量",
        "ja": "変数を作成"
    },
    "Modifier la variable": {
        "en": "Edit Variable",
        "es": "Editar variable",
        "de": "Variable bearbeiten",
        "zh": "编辑变量",
        "ja": "変数を編集"
    },
    "Mettre à jour la variable": {
        "en": "Update Variable",
        "es": "Actualizar variable",
        "de": "Variable aktualisieren",
        "zh": "更新变量",
        "ja": "変数を更新"
    },
    "Supprimer la variable": {
        "en": "Delete Variable",
        "es": "Eliminar variable",
        "de": "Variable löschen",
        "zh": "删除变量",
        "ja": "変数を削除"
    },
    "Gestion des variables": {
        "en": "Variable Management",
        "es": "Gestión de variables",
        "de": "Variablenverwaltung",
        "zh": "变量管理",
        "ja": "変数管理"
    },
    "Toutes": {
        "en": "All",
        "es": "Todas",
        "de": "Alle",
        "zh": "全部",
        "ja": "すべて"
    },
    "Par environnement": {
        "en": "By Environment",
        "es": "Por entorno",
        "de": "Nach Umgebung",
        "zh": "按环境",
        "ja": "環境別"
    },
    "Liste des variables": {
        "en": "Variable List",
        "es": "Lista de variables",
        "de": "Variablenliste",
        "zh": "变量列表",
        "ja": "変数リスト"
    },
    "Clé": {
        "en": "Key",
        "es": "Clave",
        "de": "Schlüssel",
        "zh": "键",
        "ja": "キー"
    },
    "Valeur": {
        "en": "Value",
        "es": "Valor",
        "de": "Wert",
        "zh": "值",
        "ja": "値"
    },
    "Filière": {
        "en": "Branch",
        "es": "Rama",
        "de": "Zweig",
        "zh": "分支",
        "ja": "ブランチ"
    },
    "Root": {
        "en": "Root",
        "es": "Raíz",
        "de": "Root",
        "zh": "根",
        "ja": "ルート"
    },
    "Créer une variable enfant": {
        "en": "Create Child Variable",
        "es": "Crear variable secundaria",
        "de": "Kindvariable erstellen",
        "zh": "创建子变量",
        "ja": "子変数を作成"
    },
    "Modifier": {
        "en": "Edit",
        "es": "Editar",
        "de": "Bearbeiten",
        "zh": "编辑",
        "ja": "編集"
    },
    "Supprimer": {
        "en": "Delete",
        "es": "Eliminar",
        "de": "Löschen",
        "zh": "删除",
        "ja": "削除"
    },
    "Valider": {
        "en": "Submit",
        "es": "Enviar",
        "de": "Absenden",
        "zh": "提交",
        "ja": "送信"
    },
    "Ajouter": {
        "en": "Add",
        "es": "Añadir",
        "de": "Hinzufügen",
        "zh": "添加",
        "ja": "追加"
    },
    "Détails": {
        "en": "Details",
        "es": "Detalles",
        "de": "Details",
        "zh": "详情",
        "ja": "詳細"
    },
    "Rapport": {
        "en": "Report",
        "es": "Informe",
        "de": "Bericht",
        "zh": "报告",
        "ja": "レポート"
    },
    "Statut": {
        "en": "Status",
        "es": "Estado",
        "de": "Status",
        "zh": "状态",
        "ja": "ステータス"
    },
    "Date": {
        "en": "Date",
        "es": "Fecha",
        "de": "Datum",
        "zh": "日期",
        "ja": "日付"
    },
    "Durée": {
        "en": "Duration",
        "es": "Duración",
        "de": "Dauer",
        "zh": "持续时间",
        "ja": "期間"
    },
    "Logs": {
        "en": "Logs",
        "es": "Registros",
        "de": "Protokolle",
        "zh": "日志",
        "ja": "ログ"
    },
    "Télécharger": {
        "en": "Download",
        "es": "Descargar",
        "de": "Herunterladen",
        "zh": "下载",
        "ja": "ダウンロード"
    },
    "Visualiser": {
        "en": "View",
        "es": "Ver",
        "de": "Ansehen",
        "zh": "查看",
        "ja": "表示"
    },
    "Erreur": {
        "en": "Error",
        "es": "Error",
        "de": "Fehler",
        "zh": "错误",
        "ja": "エラー"
    },
    "Succès": {
        "en": "Success",
        "es": "Éxito",
        "de": "Erfolg",
        "zh": "成功",
        "ja": "成功"
    },
    "Attention": {
        "en": "Warning",
        "es": "Advertencia",
        "de": "Warnung",
        "zh": "警告",
        "ja": "警告"
    },
    "Info": {
        "en": "Info",
        "es": "Info",
        "de": "Info",
        "zh": "信息",
        "ja": "情報"
    }
}

LANGUAGES = ['en', 'es', 'de', 'zh', 'ja']
BASE_DIR = 'translations'

def process_translations():
    for lang in LANGUAGES:
        po_file_path = os.path.join(BASE_DIR, lang, 'LC_MESSAGES', 'messages.po')
        if not os.path.exists(po_file_path):
            print(f"File not found: {po_file_path}")
            continue
            
        print(f"Processing {lang}...")
        try:
            with open(po_file_path, 'rb') as f:
                catalog = pofile.read_po(f)
            
            count = 0
            for message in catalog:
                if not message.string and message.id in TRANSLATIONS:
                    if lang in TRANSLATIONS[message.id]:
                        message.string = TRANSLATIONS[message.id][lang]
                        count += 1
            
            with open(po_file_path, 'wb') as f:
                pofile.write_po(f, catalog)
                
            print(f"Updated {count} translations for {lang}")
            
        except Exception as e:
            print(f"Error processing {lang}: {e}")

if __name__ == "__main__":
    process_translations()
