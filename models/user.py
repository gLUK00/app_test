"""Modèle pour la gestion des utilisateurs."""
from bson import ObjectId
import bcrypt
from utils.db import get_collection
from utils.validation import validate_email, validate_password

class User:
    """Classe représentant un utilisateur."""
    
    collection_name = 'users'
    
    @staticmethod
    def create(name, email, password, role='user'):
        """Crée un nouvel utilisateur."""
        # Validation
        if not validate_email(email):
            raise ValueError("Format d'email invalide")
        
        is_valid, message = validate_password(password)
        if not is_valid:
            raise ValueError(message)
        
        if role not in ['admin', 'user']:
            raise ValueError("Rôle invalide. Doit être 'admin' ou 'user'")
        
        # Vérifier si l'email existe déjà
        collection = get_collection(User.collection_name)
        if collection.find_one({'email': email}):
            raise ValueError("Cet email est déjà utilisé")
        
        # Hasher le mot de passe
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            'name': name,
            'email': email,
            'password': password_hash,
            'role': role
        }
        
        result = collection.insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_id(user_id):
        """Trouve un utilisateur par son ID."""
        collection = get_collection(User.collection_name)
        user = collection.find_one({'_id': ObjectId(user_id)})
        
        if user:
            user['_id'] = str(user['_id'])
            # Ne pas retourner le mot de passe
            user.pop('password', None)
        
        return user
    
    @staticmethod
    def find_by_email(email):
        """Trouve un utilisateur par son email."""
        collection = get_collection(User.collection_name)
        user = collection.find_one({'email': email})
        
        if user:
            user['_id'] = str(user['_id'])
        
        return user
    
    @staticmethod
    def verify_password(email, password):
        """Vérifie le mot de passe d'un utilisateur."""
        user = User.find_by_email(email)
        
        if not user:
            return False
        
        return bcrypt.checkpw(password.encode('utf-8'), user['password'])
    
    @staticmethod
    def get_all():
        """Récupère tous les utilisateurs."""
        collection = get_collection(User.collection_name)
        users = list(collection.find())
        
        for user in users:
            user['_id'] = str(user['_id'])
            user.pop('password', None)
        
        return users
    
    @staticmethod
    def update(user_id, data):
        """Met à jour un utilisateur."""
        collection = get_collection(User.collection_name)
        
        update_data = {}
        
        if 'name' in data:
            update_data['name'] = data['name']
        
        if 'email' in data:
            if not validate_email(data['email']):
                raise ValueError("Format d'email invalide")
            update_data['email'] = data['email']
        
        if 'password' in data:
            is_valid, message = validate_password(data['password'])
            if not is_valid:
                raise ValueError(message)
            update_data['password'] = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        if 'role' in data:
            if data['role'] not in ['admin', 'user']:
                raise ValueError("Rôle invalide")
            update_data['role'] = data['role']
        
        if update_data:
            collection.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
        
        return True
    
    @staticmethod
    def delete(user_id):
        """Supprime un utilisateur."""
        collection = get_collection(User.collection_name)
        result = collection.delete_one({'_id': ObjectId(user_id)})
        return result.deleted_count > 0
