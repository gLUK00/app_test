"""Modèle pour la gestion des tests."""
from bson import ObjectId
from datetime import datetime
from utils.db import get_collection, is_soft_delete_enabled

class Test:
    """Classe représentant un test avec ses actions."""
    
    collection_name = 'tests'
    
    @staticmethod
    def create(campain_id, user_id, actions, name=None, description=None, variables=None):
        """Crée un nouveau test."""
        collection = get_collection(Test.collection_name)
        
        # Déterminer l'ordre du nouveau test (le placer à la fin)
        existing_tests = list(collection.find({'campainId': ObjectId(campain_id), 'isDeleted': {'$ne': True}}))
        if existing_tests:
            max_order = max([test.get('order', 0) for test in existing_tests])
            order = max_order + 1
        else:
            order = 1
        
        test_data = {
            'campainId': ObjectId(campain_id),
            'userId': ObjectId(user_id),
            'dateCreated': datetime.utcnow(),
            'actions': actions,
            'name': name or '',
            'description': description or '',
            'variables': variables or [],
            'order': order,
            'isDeleted': False
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
        """Récupère tous les tests d'une campagne, triés par ordre d'exécution."""
        collection = get_collection(Test.collection_name)
        tests = list(collection.find({
            'campainId': ObjectId(campain_id),
            'isDeleted': {'$ne': True}
        }).sort('order', 1))
        
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
        tests = list(collection.find({'isDeleted': {'$ne': True}}).sort('dateCreated', -1))
        
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
        
        if 'name' in data:
            update_data['name'] = data['name']
        
        if 'description' in data:
            update_data['description'] = data['description']
        
        if 'variables' in data:
            update_data['variables'] = data['variables']
        
        if update_data:
            collection.update_one({'_id': ObjectId(test_id)}, {'$set': update_data})
        
        return True
    
    @staticmethod
    def delete(test_id):
        """Supprime un test (logiquement ou physiquement selon la configuration)."""
        collection = get_collection(Test.collection_name)
        
        if is_soft_delete_enabled():
            # Suppression logique : marquer comme supprimé
            result = collection.update_one(
                {'_id': ObjectId(test_id)},
                {'$set': {'isDeleted': True, 'dateDeleted': datetime.utcnow()}}
            )
            return result.modified_count > 0
        else:
            # Suppression physique : supprimer définitivement
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
    
    @staticmethod
    def move_up(test_id):
        """Déplace un test vers le haut dans l'ordre d'exécution."""
        collection = get_collection(Test.collection_name)
        test = collection.find_one({'_id': ObjectId(test_id)})
        
        if not test:
            return False
        
        current_order = test.get('order', 0)
        campain_id = test['campainId']
        
        # Trouver le test juste avant (ordre inférieur le plus proche)
        previous_test = collection.find_one({
            'campainId': campain_id,
            'order': {'$lt': current_order}
        }, sort=[('order', -1)])
        
        if not previous_test:
            return False  # Déjà en première position
        
        previous_order = previous_test.get('order', 0)
        
        # Échanger les ordres
        collection.update_one({'_id': test['_id']}, {'$set': {'order': previous_order}})
        collection.update_one({'_id': previous_test['_id']}, {'$set': {'order': current_order}})
        
        return True
    
    @staticmethod
    def move_down(test_id):
        """Déplace un test vers le bas dans l'ordre d'exécution."""
        collection = get_collection(Test.collection_name)
        test = collection.find_one({'_id': ObjectId(test_id)})
        
        if not test:
            return False
        
        current_order = test.get('order', 0)
        campain_id = test['campainId']
        
        # Trouver le test juste après (ordre supérieur le plus proche)
        next_test = collection.find_one({
            'campainId': campain_id,
            'order': {'$gt': current_order}
        }, sort=[('order', 1)])
        
        if not next_test:
            return False  # Déjà en dernière position
        
        next_order = next_test.get('order', 0)
        
        # Échanger les ordres
        collection.update_one({'_id': test['_id']}, {'$set': {'order': next_order}})
        collection.update_one({'_id': next_test['_id']}, {'$set': {'order': current_order}})
        
        return True
    
    @staticmethod
    def get_deleted():
        """Récupère tous les tests supprimés logiquement."""
        collection = get_collection(Test.collection_name)
        tests = list(collection.find({'isDeleted': True}).sort('dateDeleted', -1))
        
        for test in tests:
            test['_id'] = str(test['_id'])
            test['campainId'] = str(test['campainId'])
            test['userId'] = str(test['userId'])
            if isinstance(test.get('dateCreated'), datetime):
                test['dateCreated'] = test['dateCreated'].isoformat()
            if isinstance(test.get('dateDeleted'), datetime):
                test['dateDeleted'] = test['dateDeleted'].isoformat()
        
        return tests
    
    @staticmethod
    def restore(test_id):
        """Restaure un test supprimé logiquement."""
        collection = get_collection(Test.collection_name)
        result = collection.update_one(
            {'_id': ObjectId(test_id)},
            {'$set': {'isDeleted': False}, '$unset': {'dateDeleted': ''}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def permanent_delete(test_id):
        """Supprime définitivement un test (suppression physique)."""
        collection = get_collection(Test.collection_name)
        result = collection.delete_one({'_id': ObjectId(test_id)})
        return result.deleted_count > 0

    @staticmethod
    def duplicate(test_id, new_name=None, new_description=None):
        """Duplique un test avec un nouveau nom et une nouvelle description optionnels."""
        collection = get_collection(Test.collection_name)
        original = collection.find_one({'_id': ObjectId(test_id), 'isDeleted': {'$ne': True}})

        if not original:
            return None

        # Déterminer l'ordre du nouveau test (le placer à la fin de la campagne)
        campain_id = original['campainId']
        existing_tests = list(collection.find({'campainId': campain_id, 'isDeleted': {'$ne': True}}))
        if existing_tests:
            max_order = max([test.get('order', 0) for test in existing_tests])
            order = max_order + 1
        else:
            order = 1

        # Nom par défaut si non fourni
        base_name = new_name or (original.get('name') or '')
        if not new_name:
            base_name = f"{original.get('name', 'Test')} (copie)"

        new_test = {
            'campainId': original['campainId'],
            'userId': original['userId'],
            'dateCreated': datetime.utcnow(),
            'actions': original.get('actions', []),
            'name': base_name,
            'description': new_description if new_description is not None else original.get('description', ''),
            'variables': original.get('variables', []),
            'order': order,
            'isDeleted': False
        }

        result = collection.insert_one(new_test)
        return str(result.inserted_id)
