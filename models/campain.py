"""Modèle pour la gestion des campagnes de tests."""
from bson import ObjectId
from datetime import datetime
import uuid
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
            'isDeleted': False,
            'plugin_data_structures': []
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
    
    # ==================== Plugin Data Structures ====================
    
    @staticmethod
    def get_plugin_data_structures(campain_id):
        """Récupère les structures de données des plugins d'une campagne."""
        collection = get_collection(Campain.collection_name)
        campain = collection.find_one({'_id': ObjectId(campain_id)})
        
        if campain:
            return campain.get('plugin_data_structures', [])
        return []
    
    @staticmethod
    def add_plugin_data_structure(campain_id, name, plugin_type, values):
        """
        Ajoute une structure de données de plugin à une campagne.
        
        Args:
            campain_id: ID de la campagne
            name: Nom de la structure (unique par type de plugin)
            plugin_type: Type de plugin (ex: 'webdav', 'ftp', 's3')
            values: Dictionnaire des valeurs de la structure
            
        Returns:
            str: ID de la structure créée ou None en cas d'erreur
        """
        collection = get_collection(Campain.collection_name)
        
        # Vérifier que le nom est unique pour ce type de plugin dans cette campagne
        campain = collection.find_one({'_id': ObjectId(campain_id)})
        if not campain:
            return None
            
        existing_structures = campain.get('plugin_data_structures', [])
        for struct in existing_structures:
            if struct['name'] == name and struct['plugin_type'] == plugin_type:
                return None  # Nom déjà existant pour ce type
        
        structure_id = str(uuid.uuid4())
        structure = {
            'id': structure_id,
            'name': name,
            'plugin_type': plugin_type,
            'values': values,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        collection.update_one(
            {'_id': ObjectId(campain_id)},
            {'$push': {'plugin_data_structures': structure}}
        )
        
        return structure_id
    
    @staticmethod
    def update_plugin_data_structure(campain_id, structure_id, name=None, values=None):
        """
        Met à jour une structure de données de plugin.
        
        Args:
            campain_id: ID de la campagne
            structure_id: ID de la structure à modifier
            name: Nouveau nom (optionnel)
            values: Nouvelles valeurs (optionnel)
            
        Returns:
            bool: True si la mise à jour a réussi
        """
        collection = get_collection(Campain.collection_name)
        
        # Récupérer la campagne
        campain = collection.find_one({'_id': ObjectId(campain_id)})
        if not campain:
            return False
            
        structures = campain.get('plugin_data_structures', [])
        
        # Trouver et mettre à jour la structure
        for i, struct in enumerate(structures):
            if struct['id'] == structure_id:
                if name is not None:
                    # Vérifier l'unicité du nom
                    for other in structures:
                        if other['id'] != structure_id and other['name'] == name and other['plugin_type'] == struct['plugin_type']:
                            return False  # Nom déjà pris
                    structures[i]['name'] = name
                
                if values is not None:
                    structures[i]['values'] = values
                    
                structures[i]['updated_at'] = datetime.utcnow().isoformat()
                
                collection.update_one(
                    {'_id': ObjectId(campain_id)},
                    {'$set': {'plugin_data_structures': structures}}
                )
                return True
        
        return False
    
    @staticmethod
    def delete_plugin_data_structure(campain_id, structure_id):
        """
        Supprime une structure de données de plugin.
        
        Args:
            campain_id: ID de la campagne
            structure_id: ID de la structure à supprimer
            
        Returns:
            bool: True si la suppression a réussi
        """
        collection = get_collection(Campain.collection_name)
        
        result = collection.update_one(
            {'_id': ObjectId(campain_id)},
            {'$pull': {'plugin_data_structures': {'id': structure_id}}}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def get_plugin_data_structure_by_id(campain_id, structure_id):
        """
        Récupère une structure de données de plugin par son ID.
        
        Args:
            campain_id: ID de la campagne
            structure_id: ID de la structure
            
        Returns:
            dict: La structure ou None si non trouvée
        """
        structures = Campain.get_plugin_data_structures(campain_id)
        
        for struct in structures:
            if struct['id'] == structure_id:
                return struct
        
        return None
