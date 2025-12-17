import os
import sys
from babel.messages import pofile

# New translations to add
NEW_TRANSLATIONS = {
    "Fichiers de travail": {
        "en": "Work files",
        "es": "Archivos de trabajo",
        "de": "Arbeitsdateien",
        "zh": "工作文件",
        "ja": "作業ファイル"
    },
    "View workdir files": {
        "en": "View workdir files",
        "es": "Ver archivos de trabajo",
        "de": "Arbeitsdateien anzeigen",
        "zh": "查看工作目录文件",
        "ja": "作業ディレクトリファイルを表示"
    },
    "Ce dossier est vide": {
        "en": "This folder is empty",
        "es": "Esta carpeta está vacía",
        "de": "Dieser Ordner ist leer",
        "zh": "此文件夹为空",
        "ja": "このフォルダは空です"
    },
    "Le dossier n'est pas vide": {
        "en": "The folder is not empty",
        "es": "La carpeta no está vacía",
        "de": "Der Ordner ist nicht leer",
        "zh": "文件夹不为空",
        "ja": "フォルダは空ではありません"
    },
    "Êtes-vous sûr de vouloir supprimer ce dossier ?": {
        "en": "Are you sure you want to delete this folder?",
        "es": "¿Está seguro de que desea eliminar esta carpeta?",
        "de": "Sind Sie sicher, dass Sie diesen Ordner löschen möchten?",
        "zh": "您确定要删除此文件夹吗？",
        "ja": "このフォルダを削除してもよろしいですか？"
    },
    "Dossier supprimé avec succès": {
        "en": "Folder deleted successfully",
        "es": "Carpeta eliminada con éxito",
        "de": "Ordner erfolgreich gelöscht",
        "zh": "文件夹已成功删除",
        "ja": "フォルダが正常に削除されました"
    },
    "Fichiers de la campagne": {
        "en": "Campaign files",
        "es": "Archivos de la campaña",
        "de": "Kampagnendateien",
        "zh": "活动文件",
        "ja": "キャンペーンファイル"
    },
    "Impossible de charger les fichiers": {
        "en": "Unable to load files",
        "es": "No se pueden cargar los archivos",
        "de": "Dateien können nicht geladen werden",
        "zh": "无法加载文件",
        "ja": "ファイルを読み込めません"
    }
}

def update_translations():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    translations_dir = os.path.join(base_dir, 'translations')
    
    languages = ['en', 'fr', 'es', 'zh', 'de', 'ja']
    
    for lang in languages:
        po_file_path = os.path.join(translations_dir, lang, 'LC_MESSAGES', 'messages.po')
        
        if not os.path.exists(po_file_path):
            print(f"Fichier non trouvé: {po_file_path}")
            continue
            
        print(f"Traitement de {lang}...")
        
        with open(po_file_path, 'r', encoding='utf-8') as f:
            catalog = pofile.read_po(f)
            
        updated_count = 0
        
        for message in catalog:
            if message.id in NEW_TRANSLATIONS:
                if lang in NEW_TRANSLATIONS[message.id]:
                    # Si c'est le français, on garde le msgid comme traduction si pas spécifié autrement
                    # Mais ici NEW_TRANSLATIONS a les traductions cibles
                    if lang == 'fr':
                        # Pour le français, souvent msgid == msgstr, mais on peut forcer si besoin
                        # Ici on assume que le msgid est en français
                        if not message.string:
                            message.string = message.id
                            updated_count += 1
                    else:
                        if not message.string or 'fuzzy' in message.flags:
                            message.string = NEW_TRANSLATIONS[message.id][lang]
                            if 'fuzzy' in message.flags:
                                message.flags.discard('fuzzy')
                            updated_count += 1
        
        if updated_count > 0:
            with open(po_file_path, 'wb') as f:
                pofile.write_po(f, catalog)
            print(f"  -> {updated_count} traductions mises à jour pour {lang}")
        else:
            print(f"  -> Aucune nouvelle traduction pour {lang}")

if __name__ == "__main__":
    update_translations()
