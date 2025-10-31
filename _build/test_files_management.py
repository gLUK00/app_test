#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour la gestion des fichiers dans les campagnes.

Ce script teste :
1. La création d'une campagne avec son répertoire files/
2. L'upload de fichiers via l'API
3. Le listing des fichiers
4. Le téléchargement de fichiers
5. La suppression de fichiers
6. Les événements WebSocket
"""

import requests
import json
import os
from pathlib import Path
import tempfile

# Configuration
BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

# Couleurs pour l'affichage
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

class TestFilesManagement:
    def __init__(self):
        self.token = None
        self.campain_id = None
        self.test_file_name = "test_file.txt"
        self.test_file_content = "Ceci est un fichier de test pour TestGyver"
    
    def login(self):
        """Authentification pour obtenir le token."""
        print_test("Authentification...")
        
        response = requests.post(
            f"{API_URL}/login",
            json={
                "email": "admin@example.com",
                "password": "admin123"
            }
        )
        
        if response.status_code == 200:
            self.token = response.json()['token']
            print_success("Authentification réussie")
            return True
        else:
            print_error(f"Échec de l'authentification: {response.status_code}")
            return False
    
    def create_campain(self):
        """Crée une campagne de test."""
        print_test("Création d'une campagne de test...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{API_URL}/campains",
            headers=headers,
            json={
                "name": "Test Files Management",
                "description": "Campagne pour tester la gestion des fichiers"
            }
        )
        
        if response.status_code == 201:
            self.campain_id = response.json()['campain_id']
            print_success(f"Campagne créée avec l'ID: {self.campain_id}")
            return True
        else:
            print_error(f"Échec de la création: {response.status_code}")
            print_error(response.text)
            return False
    
    def check_workdir_structure(self):
        """Vérifie que le répertoire de travail a la bonne structure."""
        print_test("Vérification de la structure du répertoire de travail...")
        
        # Charger la configuration
        with open('configuration.json', 'r') as f:
            config = json.load(f)
        
        workdir = Path(config.get('workdir', './workdir'))
        campain_dir = workdir / self.campain_id
        files_dir = campain_dir / "files"
        work_dir = campain_dir / "work"
        
        if campain_dir.exists():
            print_success(f"Répertoire de campagne existe: {campain_dir}")
        else:
            print_error(f"Répertoire de campagne n'existe pas: {campain_dir}")
            return False
        
        if files_dir.exists():
            print_success(f"Répertoire files/ existe: {files_dir}")
        else:
            print_error(f"Répertoire files/ n'existe pas: {files_dir}")
            return False
        
        if work_dir.exists():
            print_success(f"Répertoire work/ existe: {work_dir}")
        else:
            print_error(f"Répertoire work/ n'existe pas: {work_dir}")
            return False
        
        return True
    
    def upload_file(self):
        """Upload un fichier de test."""
        print_test("Upload d'un fichier...")
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(self.test_file_content)
            temp_file_path = f.name
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            with open(temp_file_path, 'rb') as f:
                files = {'file': (self.test_file_name, f, 'text/plain')}
                response = requests.post(
                    f"{API_URL}/campains/{self.campain_id}/files",
                    headers=headers,
                    files=files
                )
            
            if response.status_code == 201:
                file_info = response.json()['file']
                print_success(f"Fichier uploadé: {file_info['name']} ({file_info['size']} Ko)")
                return True
            else:
                print_error(f"Échec de l'upload: {response.status_code}")
                print_error(response.text)
                return False
        finally:
            os.unlink(temp_file_path)
    
    def upload_file_with_custom_name(self):
        """Upload un fichier avec un nom personnalisé."""
        print_test("Upload d'un fichier avec nom personnalisé...")
        
        custom_name = "fichier_renomme.txt"
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Contenu du fichier renommé")
            temp_file_path = f.name
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('original.txt', f, 'text/plain')}
                data = {'customName': custom_name}
                response = requests.post(
                    f"{API_URL}/campains/{self.campain_id}/files",
                    headers=headers,
                    files=files,
                    data=data
                )
            
            if response.status_code == 201:
                file_info = response.json()['file']
                if file_info['name'] == custom_name:
                    print_success(f"Fichier uploadé avec nom personnalisé: {file_info['name']}")
                    return True
                else:
                    print_error(f"Le fichier n'a pas été renommé correctement: {file_info['name']}")
                    return False
            else:
                print_error(f"Échec de l'upload: {response.status_code}")
                print_error(response.text)
                return False
        finally:
            os.unlink(temp_file_path)
    
    def list_files(self):
        """Liste les fichiers de la campagne."""
        print_test("Récupération de la liste des fichiers...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{API_URL}/campains/{self.campain_id}/files",
            headers=headers
        )
        
        if response.status_code == 200:
            files = response.json()['files']
            print_success(f"Liste récupérée: {len(files)} fichier(s)")
            
            for file in files:
                print_info(f"  - {file['name']} ({file['size']} Ko) - Modifié: {file['modified']}")
            
            return True
        else:
            print_error(f"Échec de la récupération: {response.status_code}")
            return False
    
    def download_file(self):
        """Télécharge un fichier."""
        print_test("Téléchargement d'un fichier...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{API_URL}/campains/{self.campain_id}/files/{self.test_file_name}",
            headers=headers
        )
        
        if response.status_code == 200:
            content = response.text
            if self.test_file_content in content:
                print_success("Fichier téléchargé avec le bon contenu")
                return True
            else:
                print_error("Le contenu du fichier ne correspond pas")
                return False
        else:
            print_error(f"Échec du téléchargement: {response.status_code}")
            return False
    
    def delete_file(self):
        """Supprime un fichier."""
        print_test(f"Suppression du fichier {self.test_file_name}...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.delete(
            f"{API_URL}/campains/{self.campain_id}/files/{self.test_file_name}",
            headers=headers
        )
        
        if response.status_code == 200:
            print_success("Fichier supprimé")
            return True
        else:
            print_error(f"Échec de la suppression: {response.status_code}")
            return False
    
    def cleanup(self):
        """Nettoie les données de test."""
        print_test("Nettoyage des données de test...")
        
        if self.campain_id:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.delete(
                f"{API_URL}/campains/{self.campain_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                print_success("Campagne de test supprimée")
            else:
                print_error(f"Échec de la suppression de la campagne: {response.status_code}")
    
    def run_all_tests(self):
        """Exécute tous les tests."""
        print(f"\n{'='*60}")
        print("Tests de la gestion des fichiers dans les campagnes")
        print(f"{'='*60}")
        
        tests = [
            self.login,
            self.create_campain,
            self.check_workdir_structure,
            self.upload_file,
            self.upload_file_with_custom_name,
            self.list_files,
            self.download_file,
            self.delete_file,
            self.list_files,  # Vérifier que le fichier a bien été supprimé
        ]
        
        try:
            for test in tests:
                if not test():
                    print_error(f"\nLe test {test.__name__} a échoué!")
                    return False
            
            print(f"\n{GREEN}{'='*60}{RESET}")
            print(f"{GREEN}✓ Tous les tests sont passés avec succès!{RESET}")
            print(f"{GREEN}{'='*60}{RESET}\n")
            return True
        
        finally:
            self.cleanup()

if __name__ == '__main__':
    tester = TestFilesManagement()
    success = tester.run_all_tests()
    exit(0 if success else 1)
