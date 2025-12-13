"""Utilitaires pour la gestion de la base de données MongoDB."""
import json
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def load_config():
    """Charge la configuration depuis le fichier configuration.json."""
    with open('configuration.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
        
    # Surcharge avec les variables d'environnement si présentes
    if 'mongo' in config:
        config['mongo']['host'] = os.environ.get('MONGO_HOST', config['mongo'].get('host'))
        config['mongo']['port'] = os.environ.get('MONGO_PORT', config['mongo'].get('port'))
        config['mongo']['user'] = os.environ.get('MONGO_USER', config['mongo'].get('user'))
        config['mongo']['pass'] = os.environ.get('MONGO_PASS', config['mongo'].get('pass'))
        config['mongo']['bdd'] = os.environ.get('MONGO_DB', config['mongo'].get('bdd'))
        
        # Support du protocole SRV
        config['mongo']['protocol'] = os.environ.get('MONGO_PROTOCOL', config['mongo'].get('protocol', 'standard'))
        config['mongo']['srv'] = os.environ.get('MONGO_SRV', config['mongo'].get('srv'))
        
    return config

def get_db_connection():
    """Établit et retourne une connexion à la base de données MongoDB."""
    config = load_config()
    mongo_config = config['mongo']
    
    if mongo_config.get('protocol') == 'srv' and mongo_config.get('srv'):
        connection_string = mongo_config['srv']
    else:
        connection_string = f"mongodb://{mongo_config['user']}:{mongo_config['pass']}@{mongo_config['host']}:{mongo_config['port']}/"
    
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=8080)
        # Tester la connexion
        client.admin.command('ping')
        db = client[mongo_config['bdd']]
        return db
    except ConnectionFailure as e:
        raise Exception(f"Impossible de se connecter à MongoDB: {e}")

def get_collection(collection_name):
    """Retourne une collection MongoDB spécifique avec le préfixe configuré."""
    db = get_db_connection()
    config = load_config()
    mongo_config = config['mongo']
    
    # Récupérer le préfixe depuis la configuration (vide "" par défaut)
    prefix = mongo_config.get('prefix', '')
    
    # Appliquer le préfixe au nom de la collection
    prefixed_collection_name = f"{prefix}{collection_name}"
    
    return db[prefixed_collection_name]

def is_soft_delete_enabled():
    """Vérifie si la suppression logique est activée dans la configuration."""
    config = load_config()
    mongo_config = config.get('mongo', {})
    return mongo_config.get('soft_delete', False)

