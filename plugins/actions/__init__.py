"""Package actions pour TestGyver."""
from plugins.plugin_manager import PluginManager
from .action_base import ActionBase

# Initialiser le gestionnaire de plugins pour les actions
action_manager = PluginManager('actions', ActionBase)

# Découvrir et charger automatiquement tous les plugins d'actions
action_manager.discover_plugins()

# Registre de toutes les actions disponibles (pour compatibilité ascendante)
ACTION_REGISTRY = action_manager.get_all_plugins()


def get_action(action_type):
    """
    Retourne une instance de l'action correspondante au type.
    
    Args:
        action_type: Type de l'action ('http', 'ssh', etc.)
    
    Returns:
        Instance de l'action ou None si le type n'existe pas
    """
    return action_manager.get_plugin(action_type)


def get_all_actions():
    """
    Retourne la liste de toutes les actions disponibles avec leurs masques de saisie.
    
    Returns:
        dict: Dictionnaire {type: {"mask": [...], "class": ..., "metadata": {...}}}
    """
    actions = {}
    for action_type, action_class in ACTION_REGISTRY.items():
        instance = action_class()
        actions[action_type] = {
            "mask": instance.get_input_mask(),
            "class": action_class.__name__,
            "metadata": instance.get_metadata()
        }
    return actions


def reload_actions():
    """
    Recharge tous les plugins d'actions.
    Utile en développement ou pour ajouter de nouvelles actions à chaud.
    
    Returns:
        dict: Dictionnaire des actions rechargées
    """
    global ACTION_REGISTRY
    action_manager.reload_plugins()
    ACTION_REGISTRY = action_manager.get_all_plugins()
    return ACTION_REGISTRY


def register_action(action_name, action_class):
    """
    Enregistre manuellement une nouvelle action.
    
    Args:
        action_name (str): Nom de l'action
        action_class: Classe de l'action
    
    Returns:
        bool: True si enregistrée avec succès
    """
    success = action_manager.register_plugin(action_name, action_class)
    if success:
        global ACTION_REGISTRY
        ACTION_REGISTRY = action_manager.get_all_plugins()
    return success


def get_action_info(action_name):
    """
    Récupère les informations détaillées sur une action.
    
    Args:
        action_name (str): Nom de l'action
    
    Returns:
        dict: Informations sur l'action
    """
    return action_manager.get_plugin_info(action_name)


def list_actions():
    """
    Liste toutes les actions disponibles avec leurs informations.
    
    Returns:
        list: Liste des informations d'actions
    """
    return action_manager.list_plugins()


__all__ = [
    'ActionBase',
    'get_action',
    'get_all_actions',
    'reload_actions',
    'register_action',
    'get_action_info',
    'list_actions',
    'ACTION_REGISTRY',
    'action_manager'
]
