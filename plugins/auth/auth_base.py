"""Classe de base pour tous les plugins d'authentification."""
from abc import abstractmethod
from plugins.plugin_base import PluginBase


class AuthBase(PluginBase):
    """
    Classe de base abstraite pour tous les plugins d'authentification.
    Les plugins d'authentification permettent d'intégrer différents systèmes
    d'authentification (LDAP, OAuth, SAML, etc.) à l'application.
    """
    
    # Métadonnées du plugin (à surcharger dans les sous-classes)
    plugin_name = None  # Nom unique du plugin d'authentification
    
    def __init__(self):
        """Initialise le plugin d'authentification."""
        self.authenticated_user = None
    
    @abstractmethod
    def get_metadata(self):
        """
        Retourne les métadonnées du plugin d'authentification.
        
        Returns:
            dict: Métadonnées du plugin
        """
        return {
            "name": self.plugin_name or self.__class__.__name__,
            "version": self.version,
            "author": self.author,
            "description": self.__doc__.strip() if self.__doc__ else "",
            "auth_type": self.get_auth_type()
        }
    
    @abstractmethod
    def validate_config(self, config):
        """
        Valide la configuration du plugin d'authentification.
        
        Args:
            config (dict): Configuration à valider
        
        Returns:
            tuple: (bool, str) - (succès, message d'erreur éventuel)
        """
        return (True, "")
    
    @abstractmethod
    def get_auth_type(self):
        """
        Retourne le type d'authentification.
        
        Returns:
            str: Type d'authentification (ldap, oauth, saml, local, etc.)
        """
        pass
    
    @abstractmethod
    def get_configuration_schema(self):
        """
        Retourne le schéma de configuration du plugin.
        
        Returns:
            list: Liste de champs de configuration
        """
        pass
    
    @abstractmethod
    def authenticate(self, credentials):
        """
        Authentifie un utilisateur avec les informations d'identification fournies.
        
        Args:
            credentials (dict): Informations d'identification
                Exemple: {"username": "user", "password": "pass"}
        
        Returns:
            dict: Résultat de l'authentification
            {
                "success": True/False,
                "message": "Message de succès ou d'erreur",
                "user": {
                    "id": "user_id",
                    "name": "User Name",
                    "email": "user@example.com",
                    "roles": ["role1", "role2"]
                }
            }
        """
        pass
    
    @abstractmethod
    def validate_token(self, token):
        """
        Valide un token d'authentification.
        
        Args:
            token (str): Token à valider
        
        Returns:
            dict: Résultat de la validation
            {
                "valid": True/False,
                "user": {...} ou None
            }
        """
        pass
    
    @abstractmethod
    def logout(self, user_id):
        """
        Déconnecte un utilisateur.
        
        Args:
            user_id (str): ID de l'utilisateur
        
        Returns:
            bool: True si déconnexion réussie
        """
        pass
    
    def get_authenticated_user(self):
        """Retourne l'utilisateur authentifié."""
        return self.authenticated_user
    
    def supports_registration(self):
        """
        Indique si le plugin supporte l'enregistrement de nouveaux utilisateurs.
        
        Returns:
            bool: True si l'enregistrement est supporté
        """
        return False
    
    def supports_password_reset(self):
        """
        Indique si le plugin supporte la réinitialisation de mot de passe.
        
        Returns:
            bool: True si la réinitialisation est supportée
        """
        return False
