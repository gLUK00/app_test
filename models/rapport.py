"""Modèle pour la gestion des rapports d'exécution."""
from bson import ObjectId
from datetime import datetime
from utils.db import get_collection, is_soft_delete_enabled
from models.test import Test

class Rapport:
    """Classe représentant un rapport d'exécution de campagne."""
    
    collection_name = 'rapports'
    
    @staticmethod
    def create(campain_id, result, details, filiere, tests, status='pending', progress=0, stop_on_failure=False):
        """Crée un nouveau rapport."""
        collection = get_collection(Rapport.collection_name)
        
        rapport_data = {
            'campainId': ObjectId(campain_id),
            'dateCreated': datetime.utcnow(),
            'result': result,
            'details': details,
            'filiere': filiere,
            'tests': tests,
            'status': status,  # pending, running, completed, failed
            'progress': progress,  # pourcentage de progression (0-100)
            'stopOnFailure': stop_on_failure,
            'executionTimeMs': 0,  # Temps total d'exécution de la campagne en ms
            'startTime': None,  # Timestamp de début d'exécution
            'endTime': None,  # Timestamp de fin d'exécution
            'isDeleted': False
        }
        
        result = collection.insert_one(rapport_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_id(rapport_id):
        """Trouve un rapport par son ID."""
        collection = get_collection(Rapport.collection_name)
        rapport = collection.find_one({'_id': ObjectId(rapport_id)})
        
        if rapport:
            rapport['_id'] = str(rapport['_id'])
            rapport['campainId'] = str(rapport['campainId'])
            if isinstance(rapport.get('dateCreated'), datetime):
                rapport['dateCreated'] = rapport['dateCreated'].isoformat()
            
            # Convertir les ObjectId dans les tests
            for test in rapport.get('tests', []):
                if 'testId' in test:
                    test['testId'] = str(test['testId'])
            Rapport._enrich_tests_metadata(rapport.get('tests', []))
        
        return rapport
    
    @staticmethod
    def get_by_campain(campain_id):
        """Récupère tous les rapports d'une campagne."""
        collection = get_collection(Rapport.collection_name)
        rapports = list(collection.find({
            'campainId': ObjectId(campain_id),
            'isDeleted': {'$ne': True}
        }).sort('dateCreated', -1))
        
        for rapport in rapports:
            rapport['_id'] = str(rapport['_id'])
            rapport['campainId'] = str(rapport['campainId'])
            if isinstance(rapport.get('dateCreated'), datetime):
                rapport['dateCreated'] = rapport['dateCreated'].isoformat()
            
            for test in rapport.get('tests', []):
                if 'testId' in test:
                    test['testId'] = str(test['testId'])
            Rapport._enrich_tests_metadata(rapport.get('tests', []))
        
        return rapports
    
    @staticmethod
    def get_all():
        """Récupère tous les rapports."""
        collection = get_collection(Rapport.collection_name)
        rapports = list(collection.find({'isDeleted': {'$ne': True}}).sort('dateCreated', -1))
        
        for rapport in rapports:
            rapport['_id'] = str(rapport['_id'])
            rapport['campainId'] = str(rapport['campainId'])
            if isinstance(rapport.get('dateCreated'), datetime):
                rapport['dateCreated'] = rapport['dateCreated'].isoformat()
            
            for test in rapport.get('tests', []):
                if 'testId' in test:
                    test['testId'] = str(test['testId'])
            Rapport._enrich_tests_metadata(rapport.get('tests', []))
        
        return rapports
    
    @staticmethod
    def update(rapport_id, data):
        """Met à jour un rapport."""
        collection = get_collection(Rapport.collection_name)
        
        update_data = {}
        
        if 'result' in data:
            update_data['result'] = data['result']
        
        if 'details' in data:
            update_data['details'] = data['details']
        
        if 'filiere' in data:
            update_data['filiere'] = data['filiere']
        
        if 'tests' in data:
            update_data['tests'] = data['tests']
        
        if 'status' in data:
            update_data['status'] = data['status']
        
        if 'progress' in data:
            update_data['progress'] = data['progress']
        
        if 'stopOnFailure' in data:
            update_data['stopOnFailure'] = data['stopOnFailure']
        
        if 'executionTimeMs' in data:
            update_data['executionTimeMs'] = data['executionTimeMs']
        
        if 'startTime' in data:
            update_data['startTime'] = data['startTime']
        
        if 'endTime' in data:
            update_data['endTime'] = data['endTime']
        
        if update_data:
            collection.update_one({'_id': ObjectId(rapport_id)}, {'$set': update_data})
        
        return True
    
    @staticmethod
    def delete(rapport_id):
        """Supprime un rapport (logiquement ou physiquement selon la configuration)."""
        collection = get_collection(Rapport.collection_name)
        
        if is_soft_delete_enabled():
            # Suppression logique : marquer comme supprimé
            result = collection.update_one(
                {'_id': ObjectId(rapport_id)},
                {'$set': {'isDeleted': True, 'dateDeleted': datetime.utcnow()}}
            )
            return result.modified_count > 0
        else:
            # Suppression physique : supprimer définitivement
            result = collection.delete_one({'_id': ObjectId(rapport_id)})
            return result.deleted_count > 0
    
    @staticmethod
    def get_deleted():
        """Récupère tous les rapports supprimés logiquement."""
        collection = get_collection(Rapport.collection_name)
        rapports = list(collection.find({'isDeleted': True}).sort('dateDeleted', -1))
        
        for rapport in rapports:
            rapport['_id'] = str(rapport['_id'])
            rapport['campainId'] = str(rapport['campainId'])
            if isinstance(rapport.get('dateCreated'), datetime):
                rapport['dateCreated'] = rapport['dateCreated'].isoformat()
            if isinstance(rapport.get('dateDeleted'), datetime):
                rapport['dateDeleted'] = rapport['dateDeleted'].isoformat()
            
            for test in rapport.get('tests', []):
                if 'testId' in test:
                    test['testId'] = str(test['testId'])
            Rapport._enrich_tests_metadata(rapport.get('tests', []))
        
        return rapports
    
    @staticmethod
    def restore(rapport_id):
        """Restaure un rapport supprimé logiquement."""
        collection = get_collection(Rapport.collection_name)
        result = collection.update_one(
            {'_id': ObjectId(rapport_id)},
            {'$set': {'isDeleted': False}, '$unset': {'dateDeleted': ''}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def permanent_delete(rapport_id):
        """Supprime définitivement un rapport (suppression physique)."""
        collection = get_collection(Rapport.collection_name)
        result = collection.delete_one({'_id': ObjectId(rapport_id)})
        return result.deleted_count > 0

    @staticmethod
    def _enrich_tests_metadata(tests):
        """Complète les métadonnées (nom/description) des tests si manquantes."""
        if not tests:
            return
        cache = {}
        for test in tests:
            if not isinstance(test, dict):
                continue
            name = (test.get('name') or '').strip()
            description = (test.get('description') or '').strip()
            test_id = test.get('testId')
            if name and description:
                continue
            if not test_id:
                continue
            if test_id not in cache:
                cache[test_id] = Test.find_by_id(test_id)
            test_doc = cache.get(test_id)
            if not test_doc:
                continue
            if not name and test_doc.get('name'):
                test['name'] = test_doc.get('name')
            if not description and test_doc.get('description'):
                test['description'] = test_doc.get('description')
    
    @staticmethod
    def get_by_name(name):
        """Trouve un rapport par son nom."""
        collection = get_collection(Rapport.collection_name)
        rapport = collection.find_one({'details': name})
        
        if rapport:
            rapport['_id'] = str(rapport['_id'])
            rapport['campainId'] = str(rapport['campainId'])
            if isinstance(rapport.get('dateCreated'), datetime):
                rapport['dateCreated'] = rapport['dateCreated'].isoformat()
        
        return rapport
