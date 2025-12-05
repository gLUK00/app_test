import os
from babel.messages import pofile

BASE_DIR = 'translations'
LANGUAGES = ['en', 'es', 'de', 'zh', 'ja']

def find_missing():
    missing = set()
    for lang in LANGUAGES:
        po_file_path = os.path.join(BASE_DIR, lang, 'LC_MESSAGES', 'messages.po')
        if not os.path.exists(po_file_path):
            continue
            
        with open(po_file_path, 'rb') as f:
            catalog = pofile.read_po(f)
        
        for message in catalog:
            if not message.string and message.id:
                missing.add(message.id)
    
    print("Missing translations for:")
    for msgid in sorted(missing):
        print(f"- {msgid}")

if __name__ == "__main__":
    find_missing()
