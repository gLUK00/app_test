"""Utilitaires pour la gestion de la base de données MongoDB."""
import json
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def load_config():
    """Charge la configuration depuis le fichier configuration.json."""
    with open('configuration.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_db_connection():
    """Établit et retourne une connexion à la base de données MongoDB."""
    config = load_config()
    mongo_config = config['mongo']
    
    connection_string = f"mongodb://{mongo_config['user']}:{mongo_config['pass']}@{mongo_config['host']}:{mongo_config['port']}/"
    
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        # Tester la connexion
        client.admin.command('ping')
        db = client[mongo_config['bdd']]
        return db
    except ConnectionFailure as e:
        raise Exception(f"Impossible de se connecter à MongoDB: {e}")

def get_collection(collection_name):
    """Retourne une collection MongoDB spécifique."""
    db = get_db_connection()
    return db[collection_name]
