"""Modèle pour la gestion des campagnes de tests."""
from bson import ObjectId
from datetime import datetime
from utils.db import get_collection, is_soft_delete_enabled

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
            'description': description,
            'isDeleted': False
        }
        
        result = collection.insert_one(campain_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_id(campain_id):
        """Trouve une campagne par son ID."""
        collection = get_collection(Campain.collection_name)
        campain = collection.find_one({'_id': ObjectId(campain_id)})
        
        if campain:
            # Récupérer les informations de l'utilisateur créateur
            user_collection = get_collection('users')
            user = user_collection.find_one({'_id': campain['userCreated']})
            
            campain['_id'] = str(campain['_id'])
            campain['userCreated'] = str(campain['userCreated'])
            campain['userCreatedName'] = user['name'] if user else 'Utilisateur inconnu'
            if isinstance(campain.get('dateCreated'), datetime):
                campain['dateCreated'] = campain['dateCreated'].isoformat()
        
        return campain
    
    @staticmethod
    def get_all():
        """Récupère toutes les campagnes."""
        collection = get_collection(Campain.collection_name)
        campains = list(collection.find({'isDeleted': {'$ne': True}}).sort('dateCreated', -1))
        
        # Récupérer les informations des utilisateurs
        user_collection = get_collection('users')
        
        for campain in campains:
            user = user_collection.find_one({'_id': campain['userCreated']})
            
            campain['_id'] = str(campain['_id'])
            campain['userCreated'] = str(campain['userCreated'])
            campain['userCreatedName'] = user['name'] if user else 'Utilisateur inconnu'
            if isinstance(campain.get('dateCreated'), datetime):
                campain['dateCreated'] = campain['dateCreated'].isoformat()
        
        return campains
    
    @staticmethod
    def get_by_user(user_id):
        """Récupère toutes les campagnes créées par un utilisateur."""
        collection = get_collection(Campain.collection_name)
        campains = list(collection.find({
            'userCreated': ObjectId(user_id),
            'isDeleted': {'$ne': True}
        }).sort('dateCreated', -1))
        
        # Récupérer les informations de l'utilisateur
        user_collection = get_collection('users')
        user = user_collection.find_one({'_id': ObjectId(user_id)})
        user_name = user['name'] if user else 'Utilisateur inconnu'
        
        for campain in campains:
            campain['_id'] = str(campain['_id'])
            campain['userCreated'] = str(campain['userCreated'])
            campain['userCreatedName'] = user_name
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
        """Supprime une campagne (logiquement ou physiquement selon la configuration)."""
        collection = get_collection(Campain.collection_name)
        
        if is_soft_delete_enabled():
            # Suppression logique : marquer comme supprimé
            result = collection.update_one(
                {'_id': ObjectId(campain_id)},
                {'$set': {'isDeleted': True, 'dateDeleted': datetime.utcnow()}}
            )
            return result.modified_count > 0
        else:
            # Suppression physique : supprimer définitivement
            result = collection.delete_one({'_id': ObjectId(campain_id)})
            return result.deleted_count > 0
    
    @staticmethod
    def get_deleted():
        """Récupère toutes les campagnes supprimées logiquement."""
        collection = get_collection(Campain.collection_name)
        campains = list(collection.find({'isDeleted': True}).sort('dateDeleted', -1))
        
        # Récupérer les informations des utilisateurs
        user_collection = get_collection('users')
        
        for campain in campains:
            user = user_collection.find_one({'_id': campain['userCreated']})
            
            campain['_id'] = str(campain['_id'])
            campain['userCreated'] = str(campain['userCreated'])
            campain['userCreatedName'] = user['name'] if user else 'Utilisateur inconnu'
            if isinstance(campain.get('dateCreated'), datetime):
                campain['dateCreated'] = campain['dateCreated'].isoformat()
            if isinstance(campain.get('dateDeleted'), datetime):
                campain['dateDeleted'] = campain['dateDeleted'].isoformat()
        
        return campains
    
    @staticmethod
    def restore(campain_id):
        """Restaure une campagne supprimée logiquement."""
        collection = get_collection(Campain.collection_name)
        result = collection.update_one(
            {'_id': ObjectId(campain_id)},
            {'$set': {'isDeleted': False}, '$unset': {'dateDeleted': ''}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def permanent_delete(campain_id):
        """Supprime définitivement une campagne (suppression physique)."""
        collection = get_collection(Campain.collection_name)
        result = collection.delete_one({'_id': ObjectId(campain_id)})
        return result.deleted_count > 0
    
    @staticmethod
    def find_by_name(name):
        """Trouve une campagne par son nom."""
        collection = get_collection(Campain.collection_name)
        return collection.find_one({'name': name, 'isDeleted': {'$ne': True}})
