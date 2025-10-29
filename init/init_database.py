#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script d'initialisation de la base de données TestGyver."""
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, CollectionInvalid
from models.user import User
from utils.db import load_config
import getpass

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
    print_info("Vérification de la connexion à MongoDB...")
    
    mongo_config = config['mongo']
    connection_string = f"mongodb://{mongo_config['user']}:{mongo_config['pass']}@{mongo_config['host']}:{mongo_config['port']}/"
    
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        # Tester la connexion
        client.admin.command('ping')
        print_success(f"Connexion à MongoDB réussie ({mongo_config['host']}:{mongo_config['port']})")
        return client
    except ConnectionFailure as e:
        print_error(f"Impossible de se connecter à MongoDB: {e}")
        print_info(f"Assurez-vous que MongoDB est démarré sur {mongo_config['host']}:{mongo_config['port']}")
        return None

def create_database(client, db_name):
    """Crée la base de données si elle n'existe pas."""
    print_info(f"Vérification de la base de données '{db_name}'...")
    
    existing_dbs = client.list_database_names()
    
    if db_name in existing_dbs:
        print_warning(f"La base de données '{db_name}' existe déjà")
        response = input(f"{Colors.YELLOW}Voulez-vous réinitialiser la base de données ? (o/N): {Colors.END}")
        if response.lower() in ['o', 'oui', 'y', 'yes']:
            client.drop_database(db_name)
            print_success(f"Base de données '{db_name}' supprimée")
            db = client[db_name]
            print_success(f"Base de données '{db_name}' créée")
            return db, True
        else:
            print_info("Conservation de la base de données existante")
            return client[db_name], False
    else:
        db = client[db_name]
        print_success(f"Base de données '{db_name}' créée")
        return db, True

def create_collections(db):
    """Crée les collections nécessaires."""
    print_info("Création des collections...")
    
    collections = ['users', 'variables', 'campains', 'tests', 'rapports']
    existing_collections = db.list_collection_names()
    
    for collection_name in collections:
        if collection_name not in existing_collections:
            try:
                db.create_collection(collection_name)
                print_success(f"Collection '{collection_name}' créée")
            except CollectionInvalid:
                print_warning(f"Collection '{collection_name}' existe déjà")
        else:
            print_info(f"Collection '{collection_name}' existe déjà")
    
    # Créer des index pour optimiser les performances
    print_info("Création des index...")
    
    # Index pour les utilisateurs (email unique)
    db.users.create_index('email', unique=True)
    print_success("Index sur 'users.email' créé")
    
    # Index pour les variables (key + filiere unique)
    db.variables.create_index([('key', 1), ('filiere', 1)], unique=True)
    print_success("Index sur 'variables.key + filiere' créé")
    
    # Index pour les campagnes
    db.campains.create_index('dateCreated')
    print_success("Index sur 'campains.dateCreated' créé")
    
    # Index pour les tests
    db.tests.create_index('campainId')
    print_success("Index sur 'tests.campainId' créé")
    
    # Index pour les rapports
    db.rapports.create_index('campainId')
    print_success("Index sur 'rapports.campainId' créé")

def create_admin_user():
    """Crée un utilisateur administrateur."""
    print_header("Création de l'utilisateur administrateur")
    
    print_info("Veuillez fournir les informations pour le compte administrateur")
    print()
    
    # Demander les informations
    name = input(f"{Colors.CYAN}Nom complet: {Colors.END}")
    if not name:
        print_error("Le nom est obligatoire")
        return False
    
    email = input(f"{Colors.CYAN}Email: {Colors.END}")
    if not email:
        print_error("L'email est obligatoire")
        return False
    
    # Validation basique de l'email
    if '@' not in email or '.' not in email:
        print_error("Format d'email invalide")
        return False
    
    password = getpass.getpass(f"{Colors.CYAN}Mot de passe: {Colors.END}")
    if not password:
        print_error("Le mot de passe est obligatoire")
        return False
    
    if len(password) < 8:
        print_error("Le mot de passe doit contenir au moins 8 caractères")
        return False
    
    password_confirm = getpass.getpass(f"{Colors.CYAN}Confirmer le mot de passe: {Colors.END}")
    if password != password_confirm:
        print_error("Les mots de passe ne correspondent pas")
        return False
    
    print()
    print_info("Création de l'utilisateur administrateur en cours...")
    
    try:
        user_id = User.create(
            name=name,
            email=email,
            password=password,
            role='admin'
        )
        print_success(f"Utilisateur administrateur créé avec succès (ID: {user_id})")
        print()
        print_info(f"Vous pouvez maintenant vous connecter avec:")
        print(f"  Email: {Colors.BOLD}{email}{Colors.END}")
        print(f"  Rôle: {Colors.BOLD}Administrateur{Colors.END}")
        return True
    except ValueError as e:
        print_error(f"Erreur lors de la création de l'utilisateur: {e}")
        return False
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        return False

def main():
    """Fonction principale d'initialisation."""
    print_header("INITIALISATION DE LA BASE DE DONNÉES TESTGYVER")
    
    try:
        # Charger la configuration
        print_info("Chargement de la configuration...")
        config = load_config()
        print_success("Configuration chargée")
        
        # Vérifier la connexion MongoDB
        client = check_mongodb_connection(config)
        if not client:
            print_error("Impossible de continuer sans connexion à MongoDB")
            print_info("Démarrez MongoDB avec: docker run -d -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=mypass mongo")
            sys.exit(1)
        
        # Créer/vérifier la base de données
        db, is_new = create_database(client, config['mongo']['bdd'])
        
        # Créer les collections et index
        create_collections(db)
        
        # Créer un utilisateur administrateur
        print()
        if is_new:
            create_admin_user()
        else:
            response = input(f"{Colors.YELLOW}Voulez-vous créer un nouvel utilisateur administrateur ? (o/N): {Colors.END}")
            if response.lower() in ['o', 'oui', 'y', 'yes']:
                create_admin_user()
        
        # Fermer la connexion
        client.close()
        
        print()
        print_header("INITIALISATION TERMINÉE AVEC SUCCÈS")
        print_success("La base de données TestGyver est prête à être utilisée !")
        print()
        print_info("Prochaines étapes:")
        print(f"  1. Démarrez l'application: {Colors.BOLD}python app.py{Colors.END}")
        print(f"  2. Accédez à l'interface: {Colors.BOLD}http://localhost:5000{Colors.END}")
        print(f"  3. Consultez l'API: {Colors.BOLD}http://localhost:5000/swagger{Colors.END}")
        print()
        
    except KeyboardInterrupt:
        print()
        print_warning("Initialisation interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erreur lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
