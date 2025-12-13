#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script de création d'utilisateur pour TestGyver."""
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from models.user import User
from utils.db import load_config
import getpass
import argparse

class Colors:
    """Codes couleurs ANSI pour l'affichage."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(message):
    """Affiche un en-tête coloré."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{message:^60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_success(message):
    """Affiche un message de succès."""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    """Affiche un message d'erreur."""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    """Affiche un message d'information."""
    print(f"{Colors.CYAN}ℹ {message}{Colors.END}")

def print_warning(message):
    """Affiche un message d'avertissement."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def check_mongodb_connection(config):
    """Vérifie la connexion à MongoDB."""
    try:
        mongo = config['mongo']
        if mongo.get('protocol') == 'srv' and mongo.get('srv'):
            connection_string = mongo['srv']
        else:
            connection_string = f"mongodb://{mongo['user']}:{mongo['pass']}@{mongo['host']}:{mongo['port']}/"
        client = MongoClient(connection_string, serverSelectionTimeoutMS=8080)
        # Forcer la connexion pour vérifier
        client.admin.command('ping')
        print_success("Connexion à MongoDB établie")
        return client
    except ConnectionFailure as e:
        print_error(f"Impossible de se connecter à MongoDB: {str(e)}")
        return None
    except Exception as e:
        print_error(f"Erreur lors de la connexion à MongoDB: {str(e)}")
        return None

def validate_email(email):
    """Valide le format de l'email."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Valide le mot de passe (minimum 8 caractères)."""
    return len(password) >= 8

def create_user_interactive():
    """Crée un utilisateur en mode interactif."""
    print_header("CRÉATION D'UTILISATEUR - MODE INTERACTIF")
    
    # Saisie du nom
    while True:
        name = input(f"{Colors.CYAN}Nom de l'utilisateur: {Colors.END}").strip()
        if name:
            break
        print_error("Le nom ne peut pas être vide")
    
    # Saisie de l'email
    while True:
        email = input(f"{Colors.CYAN}Email: {Colors.END}").strip()
        if not email:
            print_error("L'email ne peut pas être vide")
            continue
        if not validate_email(email):
            print_error("Format d'email invalide")
            continue
        break
    
    # Saisie du mot de passe
    while True:
        password = getpass.getpass(f"{Colors.CYAN}Mot de passe (min. 8 caractères): {Colors.END}")
        if not password:
            print_error("Le mot de passe ne peut pas être vide")
            continue
        if not validate_password(password):
            print_error("Le mot de passe doit contenir au moins 8 caractères")
            continue
        
        password_confirm = getpass.getpass(f"{Colors.CYAN}Confirmez le mot de passe: {Colors.END}")
        if password != password_confirm:
            print_error("Les mots de passe ne correspondent pas")
            continue
        break
    
    # Saisie du rôle
    while True:
        print(f"\n{Colors.CYAN}Rôle de l'utilisateur:{Colors.END}")
        print(f"  1. {Colors.GREEN}admin{Colors.END} (administrateur)")
        print(f"  2. {Colors.BLUE}user{Colors.END} (utilisateur standard)")
        choice = input(f"{Colors.CYAN}Choix (1 ou 2): {Colors.END}").strip()
        
        if choice == '1':
            role = 'admin'
            break
        elif choice == '2':
            role = 'user'
            break
        else:
            print_error("Choix invalide, veuillez entrer 1 ou 2")
    
    return {
        'name': name,
        'email': email,
        'password': password,
        'role': role
    }

def create_user_from_args(args):
    """Crée un utilisateur à partir des arguments de ligne de commande."""
    print_header("CRÉATION D'UTILISATEUR - MODE LIGNE DE COMMANDE")
    
    # Validation email
    if not validate_email(args.email):
        print_error("Format d'email invalide")
        return None
    
    # Validation mot de passe
    if not validate_password(args.password):
        print_error("Le mot de passe doit contenir au moins 8 caractères")
        return None
    
    # Validation rôle
    if args.role not in ['admin', 'user']:
        print_error("Le rôle doit être 'admin' ou 'user'")
        return None
    
    return {
        'name': args.name,
        'email': args.email,
        'password': args.password,
        'role': args.role
    }

def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description='Créer un utilisateur dans TestGyver',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  Mode interactif:
    python3 init/create_user.py

  Ligne de commande:
    python3 init/create_user.py -n "John Doe" -e john@example.com -p MyPassword123 -r admin
    python3 init/create_user.py --name "Jane Doe" --email jane@example.com --password Secret123 --role user
        """
    )
    
    parser.add_argument('-n', '--name', help='Nom de l\'utilisateur')
    parser.add_argument('-e', '--email', help='Email de l\'utilisateur')
    parser.add_argument('-p', '--password', help='Mot de passe de l\'utilisateur')
    parser.add_argument('-r', '--role', choices=['admin', 'user'], help='Rôle de l\'utilisateur (admin ou user)')
    
    args = parser.parse_args()
    
    # Charger la configuration
    print_info("Chargement de la configuration...")
    config = load_config()
    
    # Vérifier la connexion à MongoDB
    client = check_mongodb_connection(config)
    if not client:
        print_error("Impossible de se connecter à MongoDB")
        sys.exit(1)
    
    # Déterminer le mode (interactif ou ligne de commande)
    if args.name and args.email and args.password and args.role:
        # Mode ligne de commande
        user_data = create_user_from_args(args)
    else:
        # Mode interactif
        if any([args.name, args.email, args.password, args.role]):
            print_warning("Arguments incomplets, passage en mode interactif")
        user_data = create_user_interactive()
    
    if not user_data:
        print_error("Données utilisateur invalides")
        client.close()
        sys.exit(1)
    
    # Créer l'utilisateur
    try:
        print_info(f"\nCréation de l'utilisateur '{user_data['name']}'...")
        
        user_id = User.create(
            name=user_data['name'],
            email=user_data['email'],
            password=user_data['password'],
            role=user_data['role']
        )
        
        print_success(f"Utilisateur créé avec succès!")
        print_info(f"  ID: {user_id}")
        print_info(f"  Nom: {user_data['name']}")
        print_info(f"  Email: {user_data['email']}")
        print_info(f"  Rôle: {user_data['role']}")
        
    except DuplicateKeyError:
        print_error(f"Un utilisateur avec l'email '{user_data['email']}' existe déjà")
        client.close()
        sys.exit(1)
    except Exception as e:
        print_error(f"Erreur lors de la création de l'utilisateur: {str(e)}")
        client.close()
        sys.exit(1)
    
    # Fermer la connexion
    client.close()
    print_success("\nOpération terminée avec succès!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Opération annulée par l'utilisateur{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Erreur inattendue: {str(e)}")
        sys.exit(1)
