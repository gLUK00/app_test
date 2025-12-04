import os
import sys
import subprocess

def run_command(command):
    """Exécute une commande shell et lève une exception en cas d'erreur."""
    print(f"Exécution: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande: {e}")
        sys.exit(1)

def main():
    # Se placer à la racine du projet (parent du dossier init)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    print(f"Dossier de travail: {os.getcwd()}")

    # Chemin vers l'exécutable pybabel dans le venv
    # On suppose que pybabel est dans le même dossier que l'interpréteur python (bin/ ou Scripts/)
    python_dir = os.path.dirname(sys.executable)
    pybabel = os.path.join(python_dir, 'pybabel')
    
    # Si pybabel n'existe pas (ex: windows sans extension), essayer juste 'pybabel' ou via module
    if not os.path.exists(pybabel):
        pybabel_cmd = [sys.executable, '-m', 'babel.messages.frontend']
    else:
        pybabel_cmd = [pybabel]

    # Vérifier babel.cfg
    if not os.path.exists("babel.cfg"):
        print("Erreur: babel.cfg non trouvé à la racine du projet.")
        sys.exit(1)

    print("=== Démarrage de la gestion des traductions ===")

    # 1. Extraction
    print("\n1. Extraction des messages...")
    run_command(pybabel_cmd + ['extract', '-F', 'babel.cfg', '-o', 'messages.pot', '.'])

    # 2. Init/Update
    languages = ['en', 'fr', 'es', 'zh', 'de', 'ja']
    print("\n2. Gestion des catalogues (init/update)...")
    
    for lang in languages:
        lang_dir = os.path.join('translations', lang)
        if os.path.isdir(lang_dir):
            print(f"   -> Mise à jour du catalogue pour : {lang}")
            run_command(pybabel_cmd + ['update', '-i', 'messages.pot', '-d', 'translations', '-l', lang])
        else:
            print(f"   -> Initialisation du catalogue pour : {lang}")
            run_command(pybabel_cmd + ['init', '-i', 'messages.pot', '-d', 'translations', '-l', lang])

    # 3. Compilation
    print("\n3. Compilation des traductions...")
    run_command(pybabel_cmd + ['compile', '-d', 'translations'])

    print("\n=== Opérations terminées avec succès ===")

if __name__ == "__main__":
    main()
