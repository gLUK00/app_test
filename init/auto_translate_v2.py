import os
import sys
from babel.messages import pofile

# New translations to add
NEW_TRANSLATIONS = {
    "Aucun test supprimé": {
        "en": "No test deleted",
        "es": "Ninguna prueba eliminada",
        "de": "Kein Test gelöscht",
        "zh": "没有删除的测试",
        "ja": "削除されたテストはありません"
    },
    "Date de suppression": {
        "en": "Deletion date",
        "es": "Fecha de eliminación",
        "de": "Löschdatum",
        "zh": "删除日期",
        "ja": "削除日"
    },
    "Restaurer sélection": {
        "en": "Restore selection",
        "es": "Restaurar selección",
        "de": "Auswahl wiederherstellen",
        "zh": "恢复选择",
        "ja": "選択を復元"
    },
    "Supprimer définitivement": {
        "en": "Delete permanently",
        "es": "Eliminar permanentemente",
        "de": "Endgültig löschen",
        "zh": "永久删除",
        "ja": "完全に削除"
    },
    "Accès refusé : vous devez être administrateur.": {
        "en": "Access denied: you must be an administrator.",
        "es": "Acceso denegado: debe ser administrador.",
        "de": "Zugriff verweigert: Sie müssen Administrator sein.",
        "zh": "访问被拒绝：您必须是管理员。",
        "ja": "アクセス拒否：管理者である必要があります。"
    },
    "élément(s) restauré(s) avec succès": {
        "en": "item(s) restored successfully",
        "es": "elemento(s) restaurado(s) con éxito",
        "de": "Element(e) erfolgreich wiederhergestellt",
        "zh": "项目恢复成功",
        "ja": "項目が正常に復元されました"
    },
    "Restauration partielle.": {
        "en": "Partial restoration.",
        "es": "Restauración parcial.",
        "de": "Teilweise Wiederherstellung.",
        "zh": "部分恢复。",
        "ja": "部分復元。"
    },
    "erreur(s)": {
        "en": "error(s)",
        "es": "error(es)",
        "de": "Fehler",
        "zh": "错误",
        "ja": "エラー"
    },
    "Erreur lors de la restauration": {
        "en": "Error during restoration",
        "es": "Error durante la restauración",
        "de": "Fehler bei der Wiederherstellung",
        "zh": "恢复时出错",
        "ja": "復元中にエラーが発生しました"
    },
    "élément(s) supprimé(s) définitivement": {
        "en": "item(s) permanently deleted",
        "es": "elemento(s) eliminado(s) permanentemente",
        "de": "Element(e) endgültig gelöscht",
        "zh": "项目永久删除",
        "ja": "項目が完全に削除されました"
    },
    "Suppression partielle.": {
        "en": "Partial deletion.",
        "es": "Eliminación parcial.",
        "de": "Teilweise Löschung.",
        "zh": "部分删除。",
        "ja": "部分削除。"
    },
    "Erreur lors de la suppression": {
        "en": "Error during deletion",
        "es": "Error durante la eliminación",
        "de": "Fehler beim Löschen",
        "zh": "删除时出错",
        "ja": "削除中にエラーが発生しました"
    },
    "Veuillez remplir tous les champs obligatoires": {
        "en": "Please fill in all required fields",
        "es": "Por favor complete todos los campos obligatorios",
        "de": "Bitte füllen Sie alle Pflichtfelder aus",
        "zh": "请填写所有必填字段",
        "ja": "必須項目をすべて入力してください"
    },
    "Utilisateur créé avec succès": {
        "en": "User created successfully",
        "es": "Usuario creado con éxito",
        "de": "Benutzer erfolgreich erstellt",
        "zh": "用户创建成功",
        "ja": "ユーザーが正常に作成されました"
    },
    "Erreur lors de la création de l'utilisateur": {
        "en": "Error creating user",
        "es": "Error al crear usuario",
        "de": "Fehler beim Erstellen des Benutzers",
        "zh": "创建用户时出错",
        "ja": "ユーザー作成中にエラーが発生しました"
    },
    "Clé de la variable *": {
        "en": "Variable key *",
        "es": "Clave de variable *",
        "de": "Variablenschlüssel *",
        "zh": "变量键 *",
        "ja": "変数キー *"
    },
    "Valeur *": {
        "en": "Value *",
        "es": "Valor *",
        "de": "Wert *",
        "zh": "值 *",
        "ja": "値 *"
    },
    "Environnement (filière) *": {
        "en": "Environment (branch) *",
        "es": "Entorno (rama) *",
        "de": "Umgebung (Zweig) *",
        "zh": "环境（分支） *",
        "ja": "環境（ブランチ） *"
    },
    "Variable racine (privilèges élevés)": {
        "en": "Root variable (high privileges)",
        "es": "Variable raíz (privilegios elevados)",
        "de": "Root-Variable (hohe Privilegien)",
        "zh": "根变量（高权限）",
        "ja": "ルート変数（高権限）"
    },
    "Cochez cette option si la variable nécessite des privilèges administrateur": {
        "en": "Check this option if the variable requires administrator privileges",
        "es": "Marque esta opción si la variable requiere privilegios de administrador",
        "de": "Aktivieren Sie diese Option, wenn die Variable Administratorrechte erfordert",
        "zh": "如果变量需要管理员权限，请选中此选项",
        "ja": "変数に管理者権限が必要な場合は、このオプションをオンにします"
    },
    "Créer la variable": {
        "en": "Create variable",
        "es": "Crear variable",
        "de": "Variable erstellen",
        "zh": "创建变量",
        "ja": "変数を作成"
    },
    "Erreur lors du chargement de la variable": {
        "en": "Error loading variable",
        "es": "Error al cargar la variable",
        "de": "Fehler beim Laden der Variable",
        "zh": "加载变量时出错",
        "ja": "変数の読み込み中にエラーが発生しました"
    },
    "Variable mise à jour avec succès": {
        "en": "Variable updated successfully",
        "es": "Variable actualizada con éxito",
        "de": "Variable erfolgreich aktualisiert",
        "zh": "变量更新成功",
        "ja": "変数が正常に更新されました"
    },
    "Erreur lors de la mise à jour de la variable": {
        "en": "Error updating variable",
        "es": "Error al actualizar la variable",
        "de": "Fehler beim Aktualisieren der Variable",
        "zh": "更新变量时出错",
        "ja": "変数の更新中にエラーが発生しました"
    },
    "Êtes-vous sûr de vouloir supprimer cette variable ?": {
        "en": "Are you sure you want to delete this variable?",
        "es": "¿Está seguro de que desea eliminar esta variable?",
        "de": "Sind Sie sicher, dass Sie diese Variable löschen möchten?",
        "zh": "您确定要删除此变量吗？",
        "ja": "この変数を削除してもよろしいですか？"
    },
    "Variable supprimée avec succès": {
        "en": "Variable deleted successfully",
        "es": "Variable eliminada con éxito",
        "de": "Variable erfolgreich gelöscht",
        "zh": "变量删除成功",
        "ja": "変数が正常に削除されました"
    },
    "Erreur lors de la suppression de la variable": {
        "en": "Error deleting variable",
        "es": "Error al eliminar la variable",
        "de": "Fehler beim Löschen der Variable",
        "zh": "删除变量时出错",
        "ja": "変数の削除中にエラーが発生しました"
    },
    "Aucun utilisateur trouvé": {
        "en": "No user found",
        "es": "Ningún usuario encontrado",
        "de": "Kein Benutzer gefunden",
        "zh": "未找到用户",
        "ja": "ユーザーが見つかりません"
    },
    "Erreur lors du chargement des utilisateurs": {
        "en": "Error loading users",
        "es": "Error al cargar usuarios",
        "de": "Fehler beim Laden der Benutzer",
        "zh": "加载用户时出错",
        "ja": "ユーザーの読み込み中にエラーが発生しました"
    },
    "Êtes-vous sûr de vouloir supprimer cet utilisateur ?": {
        "en": "Are you sure you want to delete this user?",
        "es": "¿Está seguro de que desea eliminar este usuario?",
        "de": "Sind Sie sicher, dass Sie diesen Benutzer löschen möchten?",
        "zh": "您确定要删除此用户吗？",
        "ja": "このユーザーを削除してもよろしいですか？"
    },
    "Utilisateur supprimé avec succès": {
        "en": "User deleted successfully",
        "es": "Usuario eliminado con éxito",
        "de": "Benutzer erfolgreich gelöscht",
        "zh": "用户删除成功",
        "ja": "ユーザーが正常に削除されました"
    },
    "Erreur lors de la suppression de l'utilisateur": {
        "en": "Error deleting user",
        "es": "Error al eliminar usuario",
        "de": "Fehler beim Löschen des Benutzers",
        "zh": "删除用户时出错",
        "ja": "ユーザーの削除中にエラーが発生しました"
    },
    "Modifier le mot de passe de l'utilisateur": {
        "en": "Change user password",
        "es": "Cambiar contraseña de usuario",
        "de": "Benutzerpasswort ändern",
        "zh": "更改用户密码",
        "ja": "ユーザーパスワードを変更"
    },
    "Nouveau mot de passe": {
        "en": "New password",
        "es": "Nueva contraseña",
        "de": "Neues Passwort",
        "zh": "新密码",
        "ja": "新しいパスワード"
    },
    "Saisissez le nouveau mot de passe pour cet utilisateur": {
        "en": "Enter the new password for this user",
        "es": "Ingrese la nueva contraseña para este usuario",
        "de": "Geben Sie das neue Passwort für diesen Benutzer ein",
        "zh": "输入此用户的新密码",
        "ja": "このユーザーの新しいパスワードを入力してください"
    },
    "Nouveau mot de passe *": {
        "en": "New password *",
        "es": "Nueva contraseña *",
        "de": "Neues Passwort *",
        "zh": "新密码 *",
        "ja": "新しいパスワード *"
    },
    "Confirmer le nouveau mot de passe *": {
        "en": "Confirm new password *",
        "es": "Confirmar nueva contraseña *",
        "de": "Neues Passwort bestätigen *",
        "zh": "确认新密码 *",
        "ja": "新しいパスワードを確認 *"
    },
    "Veuillez remplir les deux champs de mot de passe": {
        "en": "Please fill in both password fields",
        "es": "Por favor complete ambos campos de contraseña",
        "de": "Bitte füllen Sie beide Passwortfelder aus",
        "zh": "请填写两个密码字段",
        "ja": "両方のパスワードフィールドを入力してください"
    },
    "Les mots de passe ne correspondent pas": {
        "en": "Passwords do not match",
        "es": "Las contraseñas no coinciden",
        "de": "Passwörter stimmen nicht überein",
        "zh": "密码不匹配",
        "ja": "パスワードが一致しません"
    },
    "Le mot de passe doit contenir au moins 8 caractères": {
        "en": "Password must contain at least 8 characters",
        "es": "La contraseña debe contener al menos 8 caracteres",
        "de": "Das Passwort muss mindestens 8 Zeichen enthalten",
        "zh": "密码必须至少包含 8 个字符",
        "ja": "パスワードは少なくとも8文字含む必要があります"
    },
    "Utilisateur modifié avec succès": {
        "en": "User modified successfully",
        "es": "Usuario modificado con éxito",
        "de": "Benutzer erfolgreich geändert",
        "zh": "用户修改成功",
        "ja": "ユーザーが正常に変更されました"
    },
    "Erreur lors de la modification de l'utilisateur": {
        "en": "Error modifying user",
        "es": "Error al modificar usuario",
        "de": "Fehler beim Ändern des Benutzers",
        "zh": "修改用户时出错",
        "ja": "ユーザーの変更中にエラーが発生しました"
    },
    "Ex: ma_variable": {
        "en": "Ex: my_variable",
        "es": "Ej: mi_variable",
        "de": "Bsp: meine_variable",
        "zh": "例如：my_variable",
        "ja": "例：my_variable"
    },
    "Nom": {
        "en": "Name",
        "es": "Nombre",
        "de": "Name",
        "zh": "名称",
        "ja": "名前"
    },
    "Description": {
        "en": "Description",
        "es": "Descripción",
        "de": "Beschreibung",
        "zh": "描述",
        "ja": "説明"
    },
    "Actions": {
        "en": "Actions",
        "es": "Acciones",
        "de": "Aktionen",
        "zh": "操作",
        "ja": "アクション"
    },
    "Sans nom": {
        "en": "Unnamed",
        "es": "Sin nombre",
        "de": "Unbenannt",
        "zh": "未命名",
        "ja": "名前なし"
    },
    "Aucune campagne supprimée": {
        "en": "No campaign deleted",
        "es": "Ninguna campaña eliminada",
        "de": "Keine Kampagne gelöscht",
        "zh": "没有删除的活动",
        "ja": "削除されたキャンペーンはありません"
    },
    "Aucun rapport supprimé": {
        "en": "No report deleted",
        "es": "Ningún informe eliminado",
        "de": "Kein Bericht gelöscht",
        "zh": "没有删除的报告",
        "ja": "削除されたレポートはありません"
    },
    "Filière": {
        "en": "Branch",
        "es": "Rama",
        "de": "Zweig",
        "zh": "分支",
        "ja": "ブランチ"
    },
    "Email": {
        "en": "Email",
        "es": "Correo electrónico",
        "de": "E-Mail",
        "zh": "电子邮件",
        "ja": "メール"
    },
    "Rôle": {
        "en": "Role",
        "es": "Rol",
        "de": "Rolle",
        "zh": "角色",
        "ja": "役割"
    },
    "Administrateur": {
        "en": "Administrator",
        "es": "Administrador",
        "de": "Administrator",
        "zh": "管理员",
        "ja": "管理者"
    },
    "Utilisateur": {
        "en": "User",
        "es": "Usuario",
        "de": "Benutzer",
        "zh": "用户",
        "ja": "ユーザー"
    }
}

BASE_DIR = 'translations'
LANGUAGES = ['en', 'es', 'de', 'zh', 'ja']

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
                if not message.string and message.id in NEW_TRANSLATIONS:
                    if lang in NEW_TRANSLATIONS[message.id]:
                        message.string = NEW_TRANSLATIONS[message.id][lang]
                        count += 1
            
            with open(po_file_path, 'wb') as f:
                pofile.write_po(f, catalog)
                
            print(f"Updated {count} translations for {lang}")
            
        except Exception as e:
            print(f"Error processing {lang}: {e}")

if __name__ == "__main__":
    process_translations()
