"""Exemple de plugin d'authentification locale (par défaut)."""
from plugins.auth.auth_base import AuthBase
from werkzeug.security import check_password_hash
import jwt
import datetime
from bson import ObjectId


class LocalAuthPlugin(AuthBase):
    """Plugin d'authentification locale basé sur MongoDB."""
    
    # Métadonnées du plugin
    plugin_name = "local"
    version = "1.0.0"
    author = "TestGyver Team"
    
    def __init__(self):
        """Initialise le plugin."""
        super().__init__()
        self.db = None
        self.secret_key = None
    
    def get_metadata(self):
        """Retourne les métadonnées."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Authentification locale basée sur MongoDB",
            "auth_type": self.get_auth_type()
        }
    
    def validate_config(self, config):
        """Valide la configuration."""
        required_fields = ['db', 'secret_key']
        for field in required_fields:
            if field not in config:
                return (False, f"Le champ '{field}' est obligatoire")
        return (True, "")
    
    def get_auth_type(self):
        """Retourne le type d'authentification."""
        return "local"
    
    def get_configuration_schema(self):
        """Retourne le schéma de configuration."""
        return [
            {
                "name": "db",
                "type": "string",
                "label": "Connexion base de données",
                "required": True
            },
            {
                "name": "secret_key",
                "type": "string",
                "label": "Clé secrète JWT",
                "required": True
            }
        ]
    
    def configure(self, db, secret_key):
        """Configure le plugin avec la base de données et la clé secrète."""
        self.db = db
        self.secret_key = secret_key
    
    def authenticate(self, credentials):
        """
        Authentifie un utilisateur.
        
        Args:
            credentials (dict): Informations d'identification
        
        Returns:
            dict: Résultat de l'authentification
        """
        try:
            if not self.db:
                return {
                    "success": False,
                    "message": "Plugin non configuré",
                    "user": None
                }
            
            email = credentials.get('email')
            password = credentials.get('password')
            
            if not email or not password:
                return {
                    "success": False,
                    "message": "Email et mot de passe requis",
                    "user": None
                }
            
            # Rechercher l'utilisateur
            user = self.db.users.find_one({"email": email})
            
            if not user:
                return {
                    "success": False,
                    "message": "Utilisateur non trouvé",
                    "user": None
                }
            
            # Vérifier le mot de passe
            if not check_password_hash(user['password'], password):
                return {
                    "success": False,
                    "message": "Mot de passe incorrect",
                    "user": None
                }
            
            # Générer un token JWT
            token = jwt.encode({
                'user_id': str(user['_id']),
                'email': user['email'],
                'role': user.get('role', 'user'),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, self.secret_key, algorithm='HS256')
            
            self.authenticated_user = {
                "id": str(user['_id']),
                "name": user.get('name'),
                "email": user['email'],
                "role": user.get('role', 'user')
            }
            
            return {
                "success": True,
                "message": "Authentification réussie",
                "user": self.authenticated_user,
                "token": token
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Erreur d'authentification : {str(e)}",
                "user": None
            }
    
    def validate_token(self, token):
        """
        Valide un token JWT.
        
        Args:
            token (str): Token à valider
        
        Returns:
            dict: Résultat de la validation
        """
        try:
            if not self.secret_key:
                return {
                    "valid": False,
                    "user": None
                }
            
            # Décoder le token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Récupérer l'utilisateur
            if self.db:
                user = self.db.users.find_one({"_id": ObjectId(payload['user_id'])})
                
                if user:
                    return {
                        "valid": True,
                        "user": {
                            "id": str(user['_id']),
                            "name": user.get('name'),
                            "email": user['email'],
                            "role": user.get('role', 'user')
                        }
                    }
            
            return {
                "valid": False,
                "user": None
            }
            
        except jwt.ExpiredSignatureError:
            return {
                "valid": False,
                "user": None,
                "error": "Token expiré"
            }
        except jwt.InvalidTokenError:
            return {
                "valid": False,
                "user": None,
                "error": "Token invalide"
            }
        except Exception as e:
            return {
                "valid": False,
                "user": None,
                "error": str(e)
            }
    
    def logout(self, user_id):
        """
        Déconnecte un utilisateur.
        
        Args:
            user_id (str): ID de l'utilisateur
        
        Returns:
            bool: True si déconnexion réussie
        """
        # Pour l'authentification JWT, il n'y a pas de session côté serveur
        # La déconnexion est gérée côté client en supprimant le token
        self.authenticated_user = None
        return True
    
    def supports_registration(self):
        """Indique si l'enregistrement est supporté."""
        return True
    
    def supports_password_reset(self):
        """Indique si la réinitialisation de mot de passe est supportée."""
        return True
