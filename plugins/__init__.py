"""Module d'initialisation des plugins pour TestGyver."""
from plugins.plugin_manager import PluginManager
from plugins.plugin_base import PluginBase

# Import des gestionnaires de plugins spécialisés
from plugins.actions import action_manager, get_all_actions
from plugins.reports import report_manager, get_all_reports
from plugins.auth import auth_manager, get_all_auth


class PluginRegistry:
    """
    Registre central de tous les types de plugins de l'application.
    Permet d'accéder à tous les gestionnaires de plugins de manière centralisée.
    """
    
    def __init__(self):
        """Initialise le registre des plugins."""
        self.managers = {
            'actions': action_manager,
            'reports': report_manager,
            'auth': auth_manager
        }
    
    def get_manager(self, plugin_type):
        """
        Récupère le gestionnaire de plugins pour un type donné.
        
        Args:
            plugin_type (str): Type de plugin ('actions', 'reports', 'auth')
        
        Returns:
            PluginManager: Gestionnaire de plugins
        """
        return self.managers.get(plugin_type)
    
    def get_all_plugins(self):
        """
        Récupère tous les plugins de tous les types.
        
        Returns:
            dict: Dictionnaire {type: {plugins}}
        """
        return {
            'actions': get_all_actions(),
            'reports': get_all_reports(),
            'auth': get_all_auth()
        }
    
    def reload_all(self):
        """Recharge tous les plugins de tous les types."""
        for manager in self.managers.values():
            manager.reload_plugins()
    
    def get_plugin_count(self):
        """
        Retourne le nombre de plugins chargés par type.
        
        Returns:
            dict: Dictionnaire {type: count}
        """
        return {
            plugin_type: len(manager.get_all_plugins())
            for plugin_type, manager in self.managers.items()
        }
    
    def add_plugin_type(self, plugin_type, base_class):
        """
        Ajoute un nouveau type de plugin au registre.
        
        Args:
            plugin_type (str): Nom du type de plugin
            base_class: Classe de base pour ce type de plugin
        
        Returns:
            PluginManager: Nouveau gestionnaire de plugins créé
        """
        if plugin_type in self.managers:
            print(f"Le type de plugin '{plugin_type}' existe déjà")
            return self.managers[plugin_type]
        
        manager = PluginManager(plugin_type, base_class)
        manager.discover_plugins()
        self.managers[plugin_type] = manager
        return manager


# Instance globale du registre de plugins
plugin_registry = PluginRegistry()


__all__ = [
    'PluginManager',
    'PluginBase',
    'plugin_registry',
    'action_manager',
    'report_manager',
    'auth_manager'
]
