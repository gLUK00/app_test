"""Modèle pour la gestion des variables multi-environnements."""
from bson import ObjectId
from utils.db import get_collection

class Variable:
    """Classe représentant une variable multi-environnement."""
    
    collection_name = 'variables'
    
    @staticmethod
    def create(key, value, filiere, description='', is_root=False):
        """Crée une nouvelle variable."""
        collection = get_collection(Variable.collection_name)
        
        # Vérifier si la variable existe déjà pour cette filière
        existing = collection.find_one({'key': key, 'filiere': filiere})
        if existing:
            raise ValueError(f"La variable '{key}' existe déjà pour la filière '{filiere}'")
        
        variable_data = {
            'key': key,
            'value': value,
            'filiere': filiere,
            'description': description,
            'isRoot': is_root
        }
        
        result = collection.insert_one(variable_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_id(variable_id):
        """Trouve une variable par son ID."""
        collection = get_collection(Variable.collection_name)
        variable = collection.find_one({'_id': ObjectId(variable_id)})
        
        if variable:
            variable['_id'] = str(variable['_id'])
        
        return variable
    
    @staticmethod
    def get_all():
        """Récupère toutes les variables."""
        collection = get_collection(Variable.collection_name)
        variables = list(collection.find())
        
        for variable in variables:
            variable['_id'] = str(variable['_id'])
        
        return variables
    
    @staticmethod
    def get_by_filiere(filiere):
        """Récupère toutes les variables d'une filière."""
        collection = get_collection(Variable.collection_name)
        variables = list(collection.find({'filiere': filiere}))
        
        for variable in variables:
            variable['_id'] = str(variable['_id'])
        
        return variables
    
    @staticmethod
    def get_grouped_by_filiere():
        """Récupère toutes les variables groupées par filière."""
        collection = get_collection(Variable.collection_name)
        variables = list(collection.find())
        
        grouped = {}
        for variable in variables:
            variable['_id'] = str(variable['_id'])
            filiere = variable['filiere']
            
            if filiere not in grouped:
                grouped[filiere] = []
            
            grouped[filiere].append(variable)
        
        return grouped
    
    @staticmethod
    def update(variable_id, data):
        """Met à jour une variable."""
        collection = get_collection(Variable.collection_name)
        
        update_data = {}
        
        if 'key' in data:
            update_data['key'] = data['key']
        
        if 'value' in data:
            update_data['value'] = data['value']
        
        if 'filiere' in data:
            update_data['filiere'] = data['filiere']
        
        if 'description' in data:
            update_data['description'] = data['description']
        
        if 'isRoot' in data:
            update_data['isRoot'] = bool(data['isRoot'])
        
        if update_data:
            collection.update_one({'_id': ObjectId(variable_id)}, {'$set': update_data})
        
        return True
    
    @staticmethod
    def delete(variable_id):
        """Supprime une variable."""
        collection = get_collection(Variable.collection_name)
        result = collection.delete_one({'_id': ObjectId(variable_id)})
        return result.deleted_count > 0
    
    @staticmethod
    def get_root_variables():
        """Récupère les variables marquées comme racine."""
        collection = get_collection(Variable.collection_name)
        variables = list(collection.find({'isRoot': True}))
        
        for variable in variables:
            variable['_id'] = str(variable['_id'])
        
        return variables
