"""Modèle pour la gestion des tests."""
from bson import ObjectId
from datetime import datetime
from utils.db import get_collection

class Test:
    """Classe représentant un test avec ses actions."""
    
    collection_name = 'tests'
    
    @staticmethod
    def create(campain_id, user_id, actions):
        """Crée un nouveau test."""
        collection = get_collection(Test.collection_name)
        
        test_data = {
            'campainId': ObjectId(campain_id),
            'userId': ObjectId(user_id),
            'dateCreated': datetime.utcnow(),
            'actions': actions
        }
        
        result = collection.insert_one(test_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_id(test_id):
        """Trouve un test par son ID."""
        collection = get_collection(Test.collection_name)
        test = collection.find_one({'_id': ObjectId(test_id)})
        
        if test:
            test['_id'] = str(test['_id'])
            test['campainId'] = str(test['campainId'])
            test['userId'] = str(test['userId'])
            if isinstance(test.get('dateCreated'), datetime):
                test['dateCreated'] = test['dateCreated'].isoformat()
        
        return test
    
    @staticmethod
    def get_by_campain(campain_id):
        """Récupère tous les tests d'une campagne."""
        collection = get_collection(Test.collection_name)
        tests = list(collection.find({'campainId': ObjectId(campain_id)}).sort('dateCreated', -1))
        
        for test in tests:
            test['_id'] = str(test['_id'])
            test['campainId'] = str(test['campainId'])
            test['userId'] = str(test['userId'])
            if isinstance(test.get('dateCreated'), datetime):
                test['dateCreated'] = test['dateCreated'].isoformat()
        
        return tests
    
    @staticmethod
    def get_all():
        """Récupère tous les tests."""
        collection = get_collection(Test.collection_name)
        tests = list(collection.find().sort('dateCreated', -1))
        
        for test in tests:
            test['_id'] = str(test['_id'])
            test['campainId'] = str(test['campainId'])
            test['userId'] = str(test['userId'])
            if isinstance(test.get('dateCreated'), datetime):
                test['dateCreated'] = test['dateCreated'].isoformat()
        
        return tests
    
    @staticmethod
    def update(test_id, data):
        """Met à jour un test."""
        collection = get_collection(Test.collection_name)
        
        update_data = {}
        
        if 'actions' in data:
            update_data['actions'] = data['actions']
        
        if update_data:
            collection.update_one({'_id': ObjectId(test_id)}, {'$set': update_data})
        
        return True
    
    @staticmethod
    def delete(test_id):
        """Supprime un test."""
        collection = get_collection(Test.collection_name)
        result = collection.delete_one({'_id': ObjectId(test_id)})
        return result.deleted_count > 0
    
    @staticmethod
    def add_action(test_id, action):
        """Ajoute une action à un test."""
        collection = get_collection(Test.collection_name)
        collection.update_one(
            {'_id': ObjectId(test_id)},
            {'$push': {'actions': action}}
        )
        return True
    
    @staticmethod
    def remove_action(test_id, action_index):
        """Supprime une action d'un test par son index."""
        test = Test.find_by_id(test_id)
        if test and 0 <= action_index < len(test['actions']):
            test['actions'].pop(action_index)
            Test.update(test_id, {'actions': test['actions']})
            return True
        return False
