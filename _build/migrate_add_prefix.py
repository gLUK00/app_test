#!/usr/bin/env python3
"""
Script de migration pour ajouter un préfixe aux collections MongoDB existantes.

Ce script permet de migrer des collections existantes (sans préfixe) vers des 
collections préfixées, facilitant ainsi le déploiement de multiples instances 
ou la migration progressive de données.

Usage:
    python3 migrate_add_prefix.py
    
    ou avec options:
    
    python3 migrate_add_prefix.py --dry-run  # Simulation sans modification
    python3 migrate_add_prefix.py --force    # Sans confirmation
"""

import sys
import os
import argparse

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from utils.db import load_config

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
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{message:^70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}\n")

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

def get_db_connection(config):
    """Établit une connexion à la base de données."""
    mongo_config = config['mongo']
    connection_string = f"mongodb://{mongo_config['user']}:{mongo_config['pass']}@{mongo_config['host']}:{mongo_config['port']}/"
    
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client[mongo_config['bdd']]
        return db, client
    except ConnectionFailure as e:
        print_error(f"Impossible de se connecter à MongoDB: {e}")
        return None, None

def check_collections_exist(db, collections):
    """Vérifie quelles collections existent."""
    existing = db.list_collection_names()
    found = {}
    
    for collection_name in collections:
        found[collection_name] = collection_name in existing
    
    return found

def count_documents(db, collection_name):
    """Compte le nombre de documents dans une collection."""
    try:
        return db[collection_name].count_documents({})
    except:
        return 0

def migrate_collection(db, source_name, target_name, dry_run=False):
    """Migre une collection vers un nouveau nom avec préfixe."""
    doc_count = count_documents(db, source_name)
    
    if dry_run:
        print_info(f"[DRY-RUN] Copierait {doc_count} documents de '{source_name}' vers '{target_name}'")
        return True
    
    if doc_count == 0:
        print_warning(f"La collection '{source_name}' est vide, rien à migrer")
        return True
    
    try:
        # Utiliser aggregate avec $out pour copier la collection
        db[source_name].aggregate([{'$out': target_name}])
        
        # Vérifier que la copie a réussi
        target_count = count_documents(db, target_name)
        if target_count == doc_count:
            print_success(f"Migré {doc_count} documents de '{source_name}' vers '{target_name}'")
            return True
        else:
            print_error(f"Erreur: {target_count}/{doc_count} documents copiés")
            return False
    except Exception as e:
        print_error(f"Erreur lors de la migration de '{source_name}': {e}")
        return False

def recreate_indexes(db, prefix):
    """Recrée les index sur les collections préfixées."""
    print_info("Recréation des index...")
    
    try:
        # Index pour les utilisateurs (email unique)
        db[f"{prefix}users"].create_index('email', unique=True)
        print_success(f"Index sur '{prefix}users.email' créé")
        
        # Index pour les variables (key + filiere unique)
        db[f"{prefix}variables"].create_index([('key', 1), ('filiere', 1)], unique=True)
        print_success(f"Index sur '{prefix}variables.key + filiere' créé")
        
        # Index pour les campagnes
        db[f"{prefix}campains"].create_index('dateCreated')
        print_success(f"Index sur '{prefix}campains.dateCreated' créé")
        
        # Index pour les tests
        db[f"{prefix}tests"].create_index('campainId')
        print_success(f"Index sur '{prefix}tests.campainId' créé")
        
        # Index pour les rapports
        db[f"{prefix}rapports"].create_index('campainId')
        print_success(f"Index sur '{prefix}rapports.campainId' créé")
        
        return True
    except Exception as e:
        print_error(f"Erreur lors de la création des index: {e}")
        return False

def main():
    """Fonction principale de migration."""
    parser = argparse.ArgumentParser(description='Migration des collections MongoDB avec préfixe')
    parser.add_argument('--dry-run', action='store_true', help='Simulation sans modification')
    parser.add_argument('--force', action='store_true', help='Pas de confirmation')
    parser.add_argument('--keep-old', action='store_true', help='Conserver les anciennes collections')
    args = parser.parse_args()
    
    print_header("MIGRATION DES COLLECTIONS MONGODB AVEC PRÉFIXE")
    
    # Charger la configuration
    print_info("Chargement de la configuration...")
    config = load_config()
    prefix = config['mongo'].get('prefix', '')
    
    if not prefix:
        print_error("Aucun préfixe configuré dans configuration.json")
        print_info("Ajoutez un champ 'prefix' dans la section 'mongo' de configuration.json")
        sys.exit(1)
    
    print_success(f"Préfixe configuré: '{prefix}'")
    
    # Connexion à MongoDB
    print_info("Connexion à MongoDB...")
    db, client = get_db_connection(config)
    if db is None:
        sys.exit(1)
    
    print_success("Connecté à MongoDB")
    
    # Collections à migrer
    collections = ['users', 'variables', 'campains', 'tests', 'rapports']
    
    # Vérifier les collections existantes
    print_info("Vérification des collections existantes...")
    existing = check_collections_exist(db, collections)
    
    # Afficher l'état actuel
    print("\n" + "="*70)
    print("ÉTAT ACTUEL DES COLLECTIONS")
    print("="*70)
    
    migrations_needed = []
    for collection_name in collections:
        source_exists = existing[collection_name]
        target_name = f"{prefix}{collection_name}"
        target_exists = target_name in db.list_collection_names()
        
        source_count = count_documents(db, collection_name) if source_exists else 0
        target_count = count_documents(db, target_name) if target_exists else 0
        
        status = ""
        if source_exists and source_count > 0:
            if target_exists and target_count > 0:
                status = f"{Colors.YELLOW}⚠ Les deux collections existent{Colors.END}"
            else:
                status = f"{Colors.GREEN}✓ À migrer ({source_count} documents){Colors.END}"
                migrations_needed.append(collection_name)
        else:
            if target_exists and target_count > 0:
                status = f"{Colors.CYAN}ℹ Déjà migrée ({target_count} documents){Colors.END}"
            else:
                status = f"{Colors.CYAN}ℹ Aucune donnée{Colors.END}"
        
        print(f"  {collection_name:15} → {target_name:20} {status}")
    
    if not migrations_needed:
        print("\n" + "="*70)
        print_info("Aucune migration nécessaire, toutes les collections sont déjà préfixées")
        print("="*70)
        client.close()
        sys.exit(0)
    
    # Demander confirmation
    print("\n" + "="*70)
    print("PLAN DE MIGRATION")
    print("="*70)
    
    for collection_name in migrations_needed:
        source_count = count_documents(db, collection_name)
        target_name = f"{prefix}{collection_name}"
        print(f"  {collection_name} → {target_name} ({source_count} documents)")
    
    if args.dry_run:
        print_warning("\nMODE SIMULATION ACTIVÉ - Aucune modification ne sera effectuée")
    
    if not args.force and not args.dry_run:
        print()
        response = input(f"{Colors.YELLOW}Voulez-vous continuer avec la migration ? (o/N): {Colors.END}")
        if response.lower() not in ['o', 'oui', 'y', 'yes']:
            print_info("Migration annulée")
            client.close()
            sys.exit(0)
    
    # Effectuer la migration
    print("\n" + "="*70)
    print("MIGRATION EN COURS")
    print("="*70 + "\n")
    
    success_count = 0
    for collection_name in migrations_needed:
        target_name = f"{prefix}{collection_name}"
        if migrate_collection(db, collection_name, target_name, args.dry_run):
            success_count += 1
    
    # Recréer les index
    if not args.dry_run and success_count > 0:
        print()
        if not recreate_indexes(db, prefix):
            print_warning("Certains index n'ont pas pu être créés")
    
    # Supprimer les anciennes collections si demandé
    if not args.keep_old and not args.dry_run and success_count == len(migrations_needed):
        print("\n" + "="*70)
        print("NETTOYAGE DES ANCIENNES COLLECTIONS")
        print("="*70 + "\n")
        
        if not args.force:
            response = input(f"{Colors.YELLOW}Voulez-vous supprimer les anciennes collections ? (o/N): {Colors.END}")
            if response.lower() not in ['o', 'oui', 'y', 'yes']:
                print_info("Anciennes collections conservées")
            else:
                for collection_name in migrations_needed:
                    db[collection_name].drop()
                    print_success(f"Collection '{collection_name}' supprimée")
        else:
            for collection_name in migrations_needed:
                db[collection_name].drop()
                print_success(f"Collection '{collection_name}' supprimée")
    
    # Résumé final
    print("\n" + "="*70)
    print("RÉSUMÉ DE LA MIGRATION")
    print("="*70)
    print(f"Collections migrées avec succès : {success_count}/{len(migrations_needed)}")
    
    if args.dry_run:
        print_warning("MODE SIMULATION - Aucune modification n'a été effectuée")
        print_info("Exécutez sans --dry-run pour effectuer la migration réelle")
    elif success_count == len(migrations_needed):
        print_success("Migration terminée avec succès !")
        print_info("Vous pouvez maintenant démarrer l'application avec le nouveau préfixe")
    else:
        print_error("Certaines migrations ont échoué")
        print_info("Vérifiez les erreurs ci-dessus et réessayez")
    
    print("="*70 + "\n")
    
    client.close()

if __name__ == '__main__':
    main()
