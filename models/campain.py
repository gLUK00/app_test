"""Modèle pour la gestion des campagnes de tests."""
from bson import ObjectId
from datetime import datetime
from utils.db import get_collection

class Campain:
    """Classe représentant une campagne de tests."""
    
    collection_name = 'campains'
    
    @staticmethod
    def create(user_created, name, description=''):
        """Crée une nouvelle campagne."""
        collection = get_collection(Campain.collection_name)
        
        campain_data = {
            'userCreated': ObjectId(user_created),
            'name': name,
            'dateCreated': datetime.utcnow(),
            'description': description
        }
        
        result = collection.insert_one(campain_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_id(campain_id):
        """Trouve une campagne par son ID."""
        collection = get_collection(Campain.collection_name)
        campain = collection.find_one({'_id': ObjectId(campain_id)})
        
        if campain:
            campain['_id'] = str(campain['_id'])
            campain['userCreated'] = str(campain['userCreated'])
            if isinstance(campain.get('dateCreated'), datetime):
                campain['dateCreated'] = campain['dateCreated'].isoformat()
        
        return campain
    
    @staticmethod
    def get_all():
        """Récupère toutes les campagnes."""
        collection = get_collection(Campain.collection_name)
        campains = list(collection.find().sort('dateCreated', -1))
        
        for campain in campains:
            campain['_id'] = str(campain['_id'])
            campain['userCreated'] = str(campain['userCreated'])
            if isinstance(campain.get('dateCreated'), datetime):
                campain['dateCreated'] = campain['dateCreated'].isoformat()
        
        return campains
    
    @staticmethod
    def get_by_user(user_id):
        """Récupère toutes les campagnes créées par un utilisateur."""
        collection = get_collection(Campain.collection_name)
        campains = list(collection.find({'userCreated': ObjectId(user_id)}).sort('dateCreated', -1))
        
        for campain in campains:
            campain['_id'] = str(campain['_id'])
            campain['userCreated'] = str(campain['userCreated'])
            if isinstance(campain.get('dateCreated'), datetime):
                campain['dateCreated'] = campain['dateCreated'].isoformat()
        
        return campains
    
    @staticmethod
    def update(campain_id, data):
        """Met à jour une campagne."""
        collection = get_collection(Campain.collection_name)
        
        update_data = {}
        
        if 'name' in data:
            update_data['name'] = data['name']
        
        if 'description' in data:
            update_data['description'] = data['description']
        
        if update_data:
            collection.update_one({'_id': ObjectId(campain_id)}, {'$set': update_data})
        
        return True
    
    @staticmethod
    def delete(campain_id):
        """Supprime une campagne."""
        collection = get_collection(Campain.collection_name)
        result = collection.delete_one({'_id': ObjectId(campain_id)})
        return result.deleted_count > 0
