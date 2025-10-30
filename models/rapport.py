"""Modèle pour la gestion des rapports d'exécution."""
from bson import ObjectId
from datetime import datetime
from utils.db import get_collection

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
            'stopOnFailure': stop_on_failure
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
        
        return rapport
    
    @staticmethod
    def get_by_campain(campain_id):
        """Récupère tous les rapports d'une campagne."""
        collection = get_collection(Rapport.collection_name)
        rapports = list(collection.find({'campainId': ObjectId(campain_id)}).sort('dateCreated', -1))
        
        for rapport in rapports:
            rapport['_id'] = str(rapport['_id'])
            rapport['campainId'] = str(rapport['campainId'])
            if isinstance(rapport.get('dateCreated'), datetime):
                rapport['dateCreated'] = rapport['dateCreated'].isoformat()
            
            for test in rapport.get('tests', []):
                if 'testId' in test:
                    test['testId'] = str(test['testId'])
        
        return rapports
    
    @staticmethod
    def get_all():
        """Récupère tous les rapports."""
        collection = get_collection(Rapport.collection_name)
        rapports = list(collection.find().sort('dateCreated', -1))
        
        for rapport in rapports:
            rapport['_id'] = str(rapport['_id'])
            rapport['campainId'] = str(rapport['campainId'])
            if isinstance(rapport.get('dateCreated'), datetime):
                rapport['dateCreated'] = rapport['dateCreated'].isoformat()
            
            for test in rapport.get('tests', []):
                if 'testId' in test:
                    test['testId'] = str(test['testId'])
        
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
        
        if update_data:
            collection.update_one({'_id': ObjectId(rapport_id)}, {'$set': update_data})
        
        return True
    
    @staticmethod
    def delete(rapport_id):
        """Supprime un rapport."""
        collection = get_collection(Rapport.collection_name)
        result = collection.delete_one({'_id': ObjectId(rapport_id)})
        return result.deleted_count > 0
    
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
