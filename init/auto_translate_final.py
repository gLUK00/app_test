import os
import sys
from babel.messages import pofile

# New translations to add
NEW_TRANSLATIONS = {
    "-- Sélectionner un type --": {
        "en": "-- Select a type --",
        "es": "-- Seleccionar un tipo --",
        "de": "-- Typ auswählen --",
        "zh": "-- 选择类型 --",
        "ja": "-- タイプを選択 --"
    },
    "Actions du test": {
        "en": "Test actions",
        "es": "Acciones de prueba",
        "de": "Testaktionen",
        "zh": "测试操作",
        "ja": "テストアクション"
    },
    "Ajouter une action": {
        "en": "Add an action",
        "es": "Añadir una acción",
        "de": "Aktion hinzufügen",
        "zh": "添加操作",
        "ja": "アクションを追加"
    },
    "Ajouter une variable": {
        "en": "Add a variable",
        "es": "Añadir una variable",
        "de": "Variable hinzufügen",
        "zh": "添加变量",
        "ja": "変数を追加"
    },
    "Aucun log disponible": {
        "en": "No logs available",
        "es": "No hay registros disponibles",
        "de": "Keine Protokolle verfügbar",
        "zh": "无可用日志",
        "ja": "ログはありません"
    },
    "Aucun test dans ce rapport": {
        "en": "No tests in this report",
        "es": "No hay pruebas en este informe",
        "de": "Keine Tests in diesem Bericht",
        "zh": "此报告中没有测试",
        "ja": "このレポートにはテストがありません"
    },
    "Aucune": {
        "en": "None",
        "es": "Ninguna",
        "de": "Keine",
        "zh": "无",
        "ja": "なし"
    },
    "Aucune action ajoutée. Cliquez sur \"Ajouter une action\" pour commencer.": {
        "en": "No actions added. Click 'Add an action' to start.",
        "es": "No se han añadido acciones. Haga clic en 'Añadir una acción' para comenzar.",
        "de": "Keine Aktionen hinzugefügt. Klicken Sie auf 'Aktion hinzufügen', um zu beginnen.",
        "zh": "未添加操作。点击“添加操作”开始。",
        "ja": "アクションが追加されていません。「アクションを追加」をクリックして開始してください。"
    },
    "Aucune description": {
        "en": "No description",
        "es": "Sin descripción",
        "de": "Keine Beschreibung",
        "zh": "无描述",
        "ja": "説明なし"
    },
    "Aucune variable trouvée": {
        "en": "No variable found",
        "es": "No se encontró ninguna variable",
        "de": "Keine Variable gefunden",
        "zh": "未找到变量",
        "ja": "変数が見つかりません"
    },
    "Caractères alphanumériques et underscore uniquement": {
        "en": "Alphanumeric characters and underscore only",
        "es": "Solo caracteres alfanuméricos y guión bajo",
        "de": "Nur alphanumerische Zeichen und Unterstrich",
        "zh": "仅限字母数字字符和下划线",
        "ja": "英数字とアンダースコアのみ"
    },
    "Champs manquants : {}": {
        "en": "Missing fields: {}",
        "es": "Campos faltantes: {}",
        "de": "Fehlende Felder: {}",
        "zh": "缺少字段：{}",
        "ja": "不足しているフィールド：{}"
    },
    "Configuration d'exécution": {
        "en": "Execution configuration",
        "es": "Configuración de ejecución",
        "de": "Ausführungskonfiguration",
        "zh": "执行配置",
        "ja": "実行構成"
    },
    "Connexion": {
        "en": "Login",
        "es": "Iniciar sesión",
        "de": "Anmelden",
        "zh": "登录",
        "ja": "ログイン"
    },
    "Créer le test": {
        "en": "Create test",
        "es": "Crear prueba",
        "de": "Test erstellen",
        "zh": "创建测试",
        "ja": "テストを作成"
    },
    "Date de création :": {
        "en": "Creation date:",
        "es": "Fecha de creación:",
        "de": "Erstellungsdatum:",
        "zh": "创建日期：",
        "ja": "作成日："
    },
    "Détails du rapport": {
        "en": "Report details",
        "es": "Detalles del informe",
        "de": "Berichtsdetails",
        "zh": "报告详情",
        "ja": "レポートの詳細"
    },
    "Effacer": {
        "en": "Clear",
        "es": "Borrar",
        "de": "Löschen",
        "zh": "清除",
        "ja": "クリア"
    },
    "En cours...": {
        "en": "In progress...",
        "es": "En curso...",
        "de": "In Bearbeitung...",
        "zh": "进行中...",
        "ja": "処理中..."
    },
    "Enregistrer": {
        "en": "Save",
        "es": "Guardar",
        "de": "Speichern",
        "zh": "保存",
        "ja": "保存"
    },
    "Enregistrer et lancer le test": {
        "en": "Save and run test",
        "es": "Guardar y ejecutar prueba",
        "de": "Speichern und Test ausführen",
        "zh": "保存并运行测试",
        "ja": "保存してテストを実行"
    },
    "Environnement :": {
        "en": "Environment:",
        "es": "Entorno:",
        "de": "Umgebung:",
        "zh": "环境：",
        "ja": "環境："
    },
    "Erreur de connexion au serveur": {
        "en": "Server connection error",
        "es": "Error de conexión al servidor",
        "de": "Serververbindungsfehler",
        "zh": "服务器连接错误",
        "ja": "サーバー接続エラー"
    },
    "Erreur lors de l'exécution de la campagne": {
        "en": "Error executing campaign",
        "es": "Error al ejecutar la campaña",
        "de": "Fehler bei der Ausführung der Kampagne",
        "zh": "执行活动时出错",
        "ja": "キャンペーンの実行中にエラーが発生しました"
    },
    "Erreur lors de la création du test: ": {
        "en": "Error creating test: ",
        "es": "Error al crear la prueba: ",
        "de": "Fehler beim Erstellen des Tests: ",
        "zh": "创建测试时出错：",
        "ja": "テストの作成中にエラーが発生しました："
    },
    "Erreur lors de la mise à jour du test: ": {
        "en": "Error updating test: ",
        "es": "Error al actualizar la prueba: ",
        "de": "Fehler beim Aktualisieren des Tests: ",
        "zh": "更新测试时出错：",
        "ja": "テストの更新中にエラーが発生しました："
    },
    "Erreur lors de la suppression de la campagne": {
        "en": "Error deleting campaign",
        "es": "Error al eliminar la campaña",
        "de": "Fehler beim Löschen der Kampagne",
        "zh": "删除活动时出错",
        "ja": "キャンペーンの削除中にエラーが発生しました"
    },
    "Erreur lors du chargement des campagnes": {
        "en": "Error loading campaigns",
        "es": "Error al cargar campañas",
        "de": "Fehler beim Laden der Kampagnen",
        "zh": "加载活动时出错",
        "ja": "キャンペーンの読み込み中にエラーが発生しました"
    },
    "Erreur lors du chargement des environnements": {
        "en": "Error loading environments",
        "es": "Error al cargar entornos",
        "de": "Fehler beim Laden der Umgebungen",
        "zh": "加载环境时出错",
        "ja": "環境の読み込み中にエラーが発生しました"
    },
    "Erreur lors du chargement des variables": {
        "en": "Error loading variables",
        "es": "Error al cargar variables",
        "de": "Fehler beim Laden der Variablen",
        "zh": "加载变量时出错",
        "ja": "変数の読み込み中にエラーが発生しました"
    },
    "Erreur lors du chargement du rapport": {
        "en": "Error loading report",
        "es": "Error al cargar el informe",
        "de": "Fehler beim Laden des Berichts",
        "zh": "加载报告时出错",
        "ja": "レポートの読み込み中にエラーが発生しました"
    },
    "Erreur lors du chargement du test": {
        "en": "Error loading test",
        "es": "Error al cargar la prueba",
        "de": "Fehler beim Laden des Tests",
        "zh": "加载测试时出错",
        "ja": "テストの読み込み中にエラーが発生しました"
    },
    "Erreur lors du lancement du test: ": {
        "en": "Error starting test: ",
        "es": "Error al iniciar la prueba: ",
        "de": "Fehler beim Starten des Tests: ",
        "zh": "启动测试时出错：",
        "ja": "テストの開始中にエラーが発生しました："
    },
    "Exécution de la campagne terminée": {
        "en": "Campaign execution completed",
        "es": "Ejecución de la campaña completada",
        "de": "Kampagnenausführung abgeschlossen",
        "zh": "活动执行完成",
        "ja": "キャンペーンの実行が完了しました"
    },
    "Exécution du test": {
        "en": "Test execution",
        "es": "Ejecución de prueba",
        "de": "Testausführung",
        "zh": "测试执行",
        "ja": "テスト実行"
    },
    "Informations du test": {
        "en": "Test information",
        "es": "Información de la prueba",
        "de": "Testinformationen",
        "zh": "测试信息",
        "ja": "テスト情報"
    },
    "Informations générales": {
        "en": "General information",
        "es": "Información general",
        "de": "Allgemeine Informationen",
        "zh": "一般信息",
        "ja": "一般情報"
    },
    "Lancement...": {
        "en": "Starting...",
        "es": "Iniciando...",
        "de": "Starten...",
        "zh": "正在启动...",
        "ja": "開始中..."
    },
    "Lancer le test": {
        "en": "Run test",
        "es": "Ejecutar prueba",
        "de": "Test ausführen",
        "zh": "运行测试",
        "ja": "テストを実行"
    },
    "Le mot de passe doit contenir au moins {} caractères": {
        "en": "Password must contain at least {} characters",
        "es": "La contraseña debe contener al menos {} caracteres",
        "de": "Das Passwort muss mindestens {} Zeichen enthalten",
        "zh": "密码必须至少包含 {} 个字符",
        "ja": "パスワードは少なくとも {} 文字含む必要があります"
    },
    "Le nom de la campagne ne peut pas être vide": {
        "en": "Campaign name cannot be empty",
        "es": "El nombre de la campaña no puede estar vacío",
        "de": "Kampagnenname darf nicht leer sein",
        "zh": "活动名称不能为空",
        "ja": "キャンペーン名は空にできません"
    },
    "Logs d'exécution": {
        "en": "Execution logs",
        "es": "Registros de ejecución",
        "de": "Ausführungsprotokolle",
        "zh": "执行日志",
        "ja": "実行ログ"
    },
    "Logs d'exécution:": {
        "en": "Execution logs:",
        "es": "Registros de ejecución:",
        "de": "Ausführungsprotokolle:",
        "zh": "执行日志：",
        "ja": "実行ログ："
    },
    "Modifier un test": {
        "en": "Edit test",
        "es": "Editar prueba",
        "de": "Test bearbeiten",
        "zh": "编辑测试",
        "ja": "テストを編集"
    },
    "Modifier utilisateur": {
        "en": "Edit user",
        "es": "Editar usuario",
        "de": "Benutzer bearbeiten",
        "zh": "编辑用户",
        "ja": "ユーザーを編集"
    },
    "Mot de passe": {
        "en": "Password",
        "es": "Contraseña",
        "de": "Passwort",
        "zh": "密码",
        "ja": "パスワード"
    },
    "Mot de passe valide": {
        "en": "Valid password",
        "es": "Contraseña válida",
        "de": "Gültiges Passwort",
        "zh": "有效密码",
        "ja": "有効なパスワード"
    },
    "Nom de la variable *": {
        "en": "Variable name *",
        "es": "Nombre de la variable *",
        "de": "Variablenname *",
        "zh": "变量名称 *",
        "ja": "変数名 *"
    },
    "Nom du test *": {
        "en": "Test name *",
        "es": "Nombre de la prueba *",
        "de": "Testname *",
        "zh": "测试名称 *",
        "ja": "テスト名 *"
    },
    "Nombre d'actions :": {
        "en": "Number of actions:",
        "es": "Número de acciones:",
        "de": "Anzahl der Aktionen:",
        "zh": "操作数量：",
        "ja": "アクション数："
    },
    "Plateforme de test multi-environnements": {
        "en": "Multi-environment test platform",
        "es": "Plataforma de pruebas multi-entorno",
        "de": "Multi-Umgebungs-Testplattform",
        "zh": "多环境测试平台",
        "ja": "マルチ環境テストプラットフォーム"
    },
    "Progression :": {
        "en": "Progress:",
        "es": "Progreso:",
        "de": "Fortschritt:",
        "zh": "进度：",
        "ja": "進捗："
    },
    "Re-exécuter le test": {
        "en": "Rerun test",
        "es": "Volver a ejecutar la prueba",
        "de": "Test erneut ausführen",
        "zh": "重新运行测试",
        "ja": "テストを再実行"
    },
    "Really! Are you serious?": {
        "en": "Really! Are you serious?",
        "es": "¡De verdad! ¿Hablas en serio?",
        "de": "Wirklich! Ist das dein Ernst?",
        "zh": "真的吗！你是认真的吗？",
        "ja": "本当に！本気ですか？"
    },
    "Se connecter": {
        "en": "Login",
        "es": "Conectarse",
        "de": "Verbinden",
        "zh": "连接",
        "ja": "接続"
    },
    "Statut :": {
        "en": "Status:",
        "es": "Estado:",
        "de": "Status:",
        "zh": "状态：",
        "ja": "ステータス："
    },
    "Statut d'exécution": {
        "en": "Execution status",
        "es": "Estado de ejecución",
        "de": "Ausführungsstatus",
        "zh": "执行状态",
        "ja": "実行ステータス"
    },
    "Supprimer le test": {
        "en": "Delete test",
        "es": "Eliminar prueba",
        "de": "Test löschen",
        "zh": "删除测试",
        "ja": "テストを削除"
    },
    "Sélectionnez les variables de sortie que vous souhaitez rendre disponibles pour les actions suivantes.": {
        "en": "Select the output variables you want to make available for subsequent actions.",
        "es": "Seleccione las variables de salida que desea que estén disponibles para las siguientes acciones.",
        "de": "Wählen Sie die Ausgabevariablen aus, die Sie für nachfolgende Aktionen verfügbar machen möchten.",
        "zh": "选择您希望在后续操作中可用的输出变量。",
        "ja": "後続のアクションで使用できるようにする出力変数を選択してください。"
    },
    "Sélectionnez un environnement": {
        "en": "Select an environment",
        "es": "Seleccione un entorno",
        "de": "Wählen Sie eine Umgebung",
        "zh": "选择环境",
        "ja": "環境を選択"
    },
    "Sélectionnez un environnement pour relancer le test": {
        "en": "Select an environment to rerun the test",
        "es": "Seleccione un entorno para volver a ejecutar la prueba",
        "de": "Wählen Sie eine Umgebung, um den Test erneut auszuführen",
        "zh": "选择环境以重新运行测试",
        "ja": "テストを再実行する環境を選択してください"
    },
    "Temps d'exécution :": {
        "en": "Execution time:",
        "es": "Tiempo de ejecución:",
        "de": "Ausführungszeit:",
        "zh": "执行时间：",
        "ja": "実行時間："
    },
    "Temps d'exécution:": {
        "en": "Execution time:",
        "es": "Tiempo de ejecución:",
        "de": "Ausführungszeit:",
        "zh": "执行时间：",
        "ja": "実行時間："
    },
    "Tests exécutés": {
        "en": "Tests executed",
        "es": "Pruebas ejecutadas",
        "de": "Ausgeführte Tests",
        "zh": "已执行的测试",
        "ja": "実行されたテスト"
    },
    "Tous les champs requis sont présents": {
        "en": "All required fields are present",
        "es": "Todos los campos requeridos están presentes",
        "de": "Alle erforderlichen Felder sind vorhanden",
        "zh": "所有必填字段都已存在",
        "ja": "すべての必須フィールドが存在します"
    },
    "Type d'action *": {
        "en": "Action type *",
        "es": "Tipo de acción *",
        "de": "Aktionstyp *",
        "zh": "操作类型 *",
        "ja": "アクションタイプ *"
    },
    "Variables de sortie": {
        "en": "Output variables",
        "es": "Variables de salida",
        "de": "Ausgabevariablen",
        "zh": "输出变量",
        "ja": "出力変数"
    },
    "Variables du test :": {
        "en": "Test variables:",
        "es": "Variables de prueba:",
        "de": "Testvariablen:",
        "zh": "测试变量：",
        "ja": "テスト変数："
    },
    "Veuillez ajouter au moins une action au test": {
        "en": "Please add at least one action to the test",
        "es": "Por favor, añada al menos una acción a la prueba",
        "de": "Bitte fügen Sie dem Test mindestens eine Aktion hinzu",
        "zh": "请至少向测试添加一个操作",
        "ja": "テストに少なくとも1つのアクションを追加してください"
    },
    "Veuillez saisir un nom pour le test": {
        "en": "Please enter a name for the test",
        "es": "Por favor, introduzca un nombre para la prueba",
        "de": "Bitte geben Sie einen Namen für den Test ein",
        "zh": "请输入测试名称",
        "ja": "テストの名前を入力してください"
    },
    "Veuillez sélectionner un environnement": {
        "en": "Please select an environment",
        "es": "Por favor, seleccione un entorno",
        "de": "Bitte wählen Sie eine Umgebung",
        "zh": "请选择环境",
        "ja": "環境を選択してください"
    },
    "Votre session a expiré. Veuillez vous reconnecter.": {
        "en": "Your session has expired. Please log in again.",
        "es": "Su sesión ha expirado. Por favor, inicie sesión de nuevo.",
        "de": "Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.",
        "zh": "您的会话已过期。请重新登录。",
        "ja": "セッションの有効期限が切れました。もう一度ログインしてください。"
    },
    "Êtes-vous sûr de vouloir supprimer cette campagne ?": {
        "en": "Are you sure you want to delete this campaign?",
        "es": "¿Está seguro de que desea eliminar esta campaña?",
        "de": "Sind Sie sicher, dass Sie diese Kampagne löschen möchten?",
        "zh": "您确定要删除此活动吗？",
        "ja": "このキャンペーンを削除してもよろしいですか？"
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
