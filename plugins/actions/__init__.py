"""Package actions pour TestGyver."""
from .action_base import ActionBase
from .http_request_action import HTTPRequestAction
from .ssh_action import SSHAction
from .webdav_action import WebdavAction
from .ftp_action import FTPAction
from .sftp_action import SFTPAction

# Registre de toutes les actions disponibles
ACTION_REGISTRY = {
    'http': HTTPRequestAction,
    'ssh': SSHAction,
    'webdav': WebdavAction,
    'ftp': FTPAction,
    'sftp': SFTPAction
}

def get_action(action_type):
    """
    Retourne une instance de l'action correspondante au type.
    
    Args:
        action_type: Type de l'action ('http', 'ssh', etc.)
    
    Returns:
        Instance de l'action ou None si le type n'existe pas
    """
    action_class = ACTION_REGISTRY.get(action_type)
    if action_class:
        return action_class()
    return None

def get_all_actions():
    """
    Retourne la liste de toutes les actions disponibles avec leurs masques de saisie.
    
    Returns:
        dict: Dictionnaire {type: {"mask": [...], "class": ...}}
    """
    actions = {}
    for action_type, action_class in ACTION_REGISTRY.items():
        instance = action_class()
        actions[action_type] = {
            "mask": instance.get_input_mask(),
            "class": action_class.__name__
        }
    return actions

__all__ = [
    'ActionBase',
    'HTTPRequestAction',
    'SSHAction',
    'WebdavAction',
    'FTPAction',
    'SFTPAction',
    'get_action',
    'get_all_actions',
    'ACTION_REGISTRY'
]
