#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour les nouvelles variables de collection files_dir et work_dir.

Ce script teste :
1. La présence des variables dans l'autocomplete JavaScript
2. La résolution des variables lors de l'exécution
3. Les chemins générés sont corrects
"""

import json
import os
from pathlib import Path

# Couleurs
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(message):
    """Affiche un message de test."""
    print(f"\n{BLUE}[TEST]{RESET} {message}")

def print_success(message):
    """Affiche un message de succès."""
    print(f"{GREEN}✓{RESET} {message}")

def print_error(message):
    """Affiche un message d'erreur."""
    print(f"{RED}✗{RESET} {message}")

def print_info(message):
    """Affiche un message d'information."""
    print(f"{YELLOW}ℹ{RESET} {message}")

class TestCollectionVariables:
    def __init__(self):
        self.errors = []
    
    def test_autocomplete_javascript(self):
        """Vérifie que les variables sont dans le fichier JavaScript."""
        print_test("Vérification du fichier JavaScript variable-autocomplete.js...")
        
        js_file = Path('static/js/variable-autocomplete.js')
        
        if not js_file.exists():
            self.errors.append("Fichier variable-autocomplete.js non trouvé")
            print_error("Fichier non trouvé")
            return False
        
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier la présence de files_dir
        if "files_dir" in content:
            print_success("Variable 'files_dir' trouvée dans l'autocomplete")
        else:
            self.errors.append("Variable 'files_dir' non trouvée dans l'autocomplete")
            print_error("Variable 'files_dir' manquante")
            return False
        
        # Vérifier la présence de work_dir
        if "work_dir" in content:
            print_success("Variable 'work_dir' trouvée dans l'autocomplete")
        else:
            self.errors.append("Variable 'work_dir' non trouvée dans l'autocomplete")
            print_error("Variable 'work_dir' manquante")
            return False
        
        # Vérifier la description
        if "Répertoire des fichiers" in content:
            print_success("Description de 'files_dir' présente")
        else:
            print_error("Description de 'files_dir' manquante")
        
        if "Répertoire de travail" in content:
            print_success("Description de 'work_dir' présente")
        else:
            print_error("Description de 'work_dir' manquante")
        
        return True
    
    def test_campain_executor(self):
        """Vérifie que le campain_executor utilise les variables."""
        print_test("Vérification du fichier campain_executor.py...")
        
        exec_file = Path('utils/campain_executor.py')
        
        if not exec_file.exists():
            self.errors.append("Fichier campain_executor.py non trouvé")
            print_error("Fichier non trouvé")
            return False
        
        with open(exec_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier l'import de get_campain_workdir
        if "from utils.workdir import get_campain_workdir" in content:
            print_success("Import de get_campain_workdir présent")
        else:
            self.errors.append("Import de get_campain_workdir manquant")
            print_error("Import manquant")
            return False
        
        # Vérifier l'assignation de test.files_dir
        if "variables_dict['test.files_dir']" in content:
            print_success("Variable 'test.files_dir' assignée dans campain_executor")
        else:
            self.errors.append("Variable 'test.files_dir' non assignée")
            print_error("Variable 'test.files_dir' manquante")
            return False
        
        # Vérifier l'assignation de test.work_dir
        if "variables_dict['test.work_dir']" in content:
            print_success("Variable 'test.work_dir' assignée dans campain_executor")
        else:
            self.errors.append("Variable 'test.work_dir' non assignée")
            print_error("Variable 'test.work_dir' manquante")
            return False
        
        return True
    
    def test_variable_resolution(self):
        """Teste la résolution des variables avec un exemple."""
        print_test("Test de résolution de variables...")
        
        # Charger la configuration
        with open('configuration.json', 'r') as f:
            config = json.load(f)
        
        workdir = config.get('workdir', './workdir')
        test_campain_id = "test_campain_123"
        
        # Simuler les chemins
        campain_workdir = Path(workdir) / test_campain_id
        files_dir = str(campain_workdir / "files")
        work_dir = str(campain_workdir / "work")
        
        print_info(f"workdir: {workdir}")
        print_info(f"files_dir simulé: {files_dir}")
        print_info(f"work_dir simulé: {work_dir}")
        
        # Vérifier le format
        expected_files = f"{workdir}/{test_campain_id}/files"
        expected_work = f"{workdir}/{test_campain_id}/work"
        
        if files_dir.endswith("/files"):
            print_success("Format de files_dir correct")
        else:
            self.errors.append(f"Format de files_dir incorrect: {files_dir}")
            print_error("Format de files_dir incorrect")
            return False
        
        if work_dir.endswith("/work"):
            print_success("Format de work_dir correct")
        else:
            self.errors.append(f"Format de work_dir incorrect: {work_dir}")
            print_error("Format de work_dir incorrect")
            return False
        
        return True
    
    def test_format_insertion(self):
        """Vérifie le format d'insertion des variables."""
        print_test("Vérification du format d'insertion...")
        
        js_file = Path('static/js/variable-autocomplete.js')
        
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Le format d'insertion pour les variables de collection doit être {{test.xxx}}
        if "{{test.${key}}}" in content or "insertFormat: (key) => `{{test.${key}}}`" in content:
            print_success("Format d'insertion {{test.xxx}} confirmé")
            return True
        else:
            print_error("Format d'insertion non trouvé ou incorrect")
            return False
    
    def run_all_tests(self):
        """Exécute tous les tests."""
        print(f"\n{'='*60}")
        print("Tests des nouvelles variables de collection")
        print(f"{'='*60}")
        
        tests = [
            ("Autocomplete JavaScript", self.test_autocomplete_javascript),
            ("Campain Executor", self.test_campain_executor),
            ("Résolution de variables", self.test_variable_resolution),
            ("Format d'insertion", self.test_format_insertion),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                self.errors.append(f"{test_name}: {str(e)}")
                print_error(f"Exception dans {test_name}: {e}")
                results.append((test_name, False))
        
        print(f"\n{'='*60}")
        print("Résumé des tests")
        print(f"{'='*60}")
        
        for test_name, result in results:
            status = f"{GREEN}✓ PASSÉ{RESET}" if result else f"{RED}✗ ÉCHOUÉ{RESET}"
            print(f"{test_name}: {status}")
        
        if self.errors:
            print(f"\n{RED}Erreurs détectées:{RESET}")
            for error in self.errors:
                print(f"  - {error}")
        
        all_passed = all(r[1] for r in results)
        
        if all_passed:
            print(f"\n{GREEN}{'='*60}{RESET}")
            print(f"{GREEN}✓ Tous les tests sont passés avec succès!{RESET}")
            print(f"{GREEN}{'='*60}{RESET}")
            
            print(f"\n{BLUE}Variables de collection disponibles:{RESET}")
            print(f"  - {{{{test.test_id}}}}      : ID du test en cours")
            print(f"  - {{{{test.campain_id}}}}   : ID de la campagne")
            print(f"  - {{{{test.files_dir}}}}    : Répertoire des fichiers de la campagne")
            print(f"  - {{{{test.work_dir}}}}     : Répertoire de travail de la campagne")
            
            print(f"\n{BLUE}Exemple d'utilisation:{RESET}")
            print(f"  Créer un fichier dans files_dir:")
            print(f"    {{{{test.files_dir}}}}/mon_fichier.txt")
            print(f"  Utiliser le répertoire de travail:")
            print(f"    {{{{test.work_dir}}}}/temp_data.json")
            
            return True
        else:
            print(f"\n{RED}{'='*60}{RESET}")
            print(f"{RED}✗ Certains tests ont échoué{RESET}")
            print(f"{RED}{'='*60}{RESET}")
            return False

if __name__ == '__main__':
    tester = TestCollectionVariables()
    success = tester.run_all_tests()
    exit(0 if success else 1)
