#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification de Socket.IO
Vérifie que Socket.IO est correctement configuré dans l'application.
"""

import os
from pathlib import Path

# Couleurs
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check_file(path, description):
    """Vérifie qu'un fichier existe."""
    if Path(path).exists():
        print(f"{GREEN}✓{RESET} {description}: {path}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {path} (MANQUANT)")
        return False

def check_content(path, search_text, description):
    """Vérifie qu'un fichier contient un texte spécifique."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print(f"{GREEN}✓{RESET} {description}")
                return True
            else:
                print(f"{RED}✗{RESET} {description} (NON TROUVÉ)")
                return False
    except Exception as e:
        print(f"{RED}✗{RESET} {description} (ERREUR: {e})")
        return False

def main():
    print("\n" + "="*60)
    print("Vérification de la configuration Socket.IO")
    print("="*60 + "\n")
    
    all_checks = []
    
    # Vérifier la présence des fichiers
    print("📁 Fichiers requis:")
    all_checks.append(check_file(
        'static/vendor/socket.io/socket.io.min.js',
        'Bibliothèque Socket.IO client'
    ))
    
    all_checks.append(check_file(
        'templates/base.html',
        'Template de base'
    ))
    
    all_checks.append(check_file(
        'templates/campain_details.html',
        'Template de détails de campagne'
    ))
    
    all_checks.append(check_file(
        'static/test-socketio.html',
        'Page de test Socket.IO'
    ))
    
    print("\n📝 Configuration:")
    
    # Vérifier que base.html charge Socket.IO
    all_checks.append(check_content(
        'templates/base.html',
        'socket.io/socket.io.min.js',
        'Socket.IO chargé dans base.html'
    ))
    
    # Vérifier que campain_details.html utilise Socket.IO
    all_checks.append(check_content(
        'templates/campain_details.html',
        'const socket = io()',
        'Initialisation Socket.IO dans campain_details.html'
    ))
    
    # Vérifier que app.py définit les gestionnaires WebSocket
    all_checks.append(check_content(
        'app.py',
        '@socketio.on(\'join\')',
        'Gestionnaire join dans app.py'
    ))
    
    all_checks.append(check_content(
        'app.py',
        '@socketio.on(\'leave\')',
        'Gestionnaire leave dans app.py'
    ))
    
    # Vérifier que les routes émettent des événements
    all_checks.append(check_content(
        'routes/campains_routes.py',
        'emit_files_updated',
        'Fonction emit_files_updated dans campains_routes.py'
    ))
    
    print("\n" + "="*60)
    
    if all(all_checks):
        print(f"{GREEN}✓ Tous les tests sont passés!{RESET}")
        print("\n📋 Prochaines étapes:")
        print("1. Démarrer l'application: python3 app.py")
        print("2. Ouvrir http://localhost:5000/static/test-socketio.html")
        print("3. Vérifier que la connexion WebSocket fonctionne")
        print("4. Tester l'upload de fichier dans une campagne")
        return 0
    else:
        print(f"{RED}✗ Certains tests ont échoué{RESET}")
        print("\n🔧 Actions correctives:")
        print("1. Vérifier que tous les fichiers existent")
        print("2. Vérifier le contenu des templates")
        print("3. Consulter docs/FILES_MANAGEMENT_QUICKSTART.md")
        return 1

if __name__ == '__main__':
    exit(main())
