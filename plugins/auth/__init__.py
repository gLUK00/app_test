"""Package auth pour TestGyver."""
from plugins.plugin_manager import PluginManager
from .auth_base import AuthBase

# Initialiser le gestionnaire de plugins pour l'authentification
auth_manager = PluginManager('auth', AuthBase)

# Découvrir et charger automatiquement tous les plugins d'authentification
auth_manager.discover_plugins()

# Registre de tous les plugins d'authentification disponibles
AUTH_REGISTRY = auth_manager.get_all_plugins()


def get_auth(auth_type):
    """
    Retourne une instance du plugin d'authentification correspondant au type.
    
    Args:
        auth_type: Type d'authentification ('ldap', 'oauth', 'saml', 'local', etc.)
    
    Returns:
        Instance du plugin d'authentification ou None si le type n'existe pas
    """
    return auth_manager.get_plugin(auth_type)


def get_all_auth():
    """
    Retourne la liste de tous les plugins d'authentification disponibles.
    
    Returns:
        dict: Dictionnaire {type: {"metadata": {...}, "class": ...}}
    """
    auths = {}
    for auth_type, auth_class in AUTH_REGISTRY.items():
        instance = auth_class()
        auths[auth_type] = {
            "metadata": instance.get_metadata(),
            "class": auth_class.__name__,
            "auth_type": instance.get_auth_type(),
            "configuration_schema": instance.get_configuration_schema(),
            "supports_registration": instance.supports_registration(),
            "supports_password_reset": instance.supports_password_reset()
        }
    return auths


def reload_auth():
    """
    Recharge tous les plugins d'authentification.
    
    Returns:
        dict: Dictionnaire des plugins d'authentification rechargés
    """
    global AUTH_REGISTRY
    auth_manager.reload_plugins()
    AUTH_REGISTRY = auth_manager.get_all_plugins()
    return AUTH_REGISTRY


def register_auth(auth_name, auth_class):
    """
    Enregistre manuellement un nouveau plugin d'authentification.
    
    Args:
        auth_name (str): Nom du plugin d'authentification
        auth_class: Classe du plugin d'authentification
    
    Returns:
        bool: True si enregistré avec succès
    """
    success = auth_manager.register_plugin(auth_name, auth_class)
    if success:
        global AUTH_REGISTRY
        AUTH_REGISTRY = auth_manager.get_all_plugins()
    return success


def list_auth():
    """
    Liste tous les plugins d'authentification disponibles avec leurs informations.
    
    Returns:
        list: Liste des informations de plugins d'authentification
    """
    return auth_manager.list_plugins()


__all__ = [
    'AuthBase',
    'get_auth',
    'get_all_auth',
    'reload_auth',
    'register_auth',
    'list_auth',
    'AUTH_REGISTRY',
    'auth_manager'
]
