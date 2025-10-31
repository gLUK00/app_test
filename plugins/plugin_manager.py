"""Gestionnaire de plugins générique pour TestGyver."""
import os
import importlib
import inspect
import traceback
from datetime import datetime
from abc import ABC


class PluginManager:
    """
    Gestionnaire de plugins générique permettant le chargement dynamique
    de différents types de plugins (actions, rapports, authentification, etc.).
    """
    
    def __init__(self, plugin_type, base_class):
        """
        Initialise le gestionnaire de plugins.
        
        Args:
            plugin_type (str): Type de plugin ('actions', 'reports', 'auth', etc.)
            base_class: Classe de base que tous les plugins de ce type doivent hériter
        """
        self.plugin_type = plugin_type
        self.base_class = base_class
        self.plugins = {}
        self.errors = []  # Liste des erreurs de chargement
        self._plugin_dir = os.path.join(
            os.path.dirname(__file__),
            plugin_type
        )
    
    def discover_plugins(self):
        """
        Découvre et charge automatiquement tous les plugins du type spécifié.
        
        Returns:
            dict: Dictionnaire des plugins chargés {nom: classe}
        """
        if not os.path.exists(self._plugin_dir):
            print(f"Le répertoire de plugins {self._plugin_dir} n'existe pas")
            return {}
        
        # Parcourir tous les fichiers Python dans le répertoire
        for filename in os.listdir(self._plugin_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                module_name = filename[:-3]  # Retirer .py
                self._load_plugin_from_module(module_name)
        
        return self.plugins
    
    def _load_plugin_from_module(self, module_name):
        """
        Charge un plugin depuis un module Python.
        
        Args:
            module_name (str): Nom du module à charger
        """
        try:
            # Importer le module
            module_path = f'plugins.{self.plugin_type}.{module_name}'
            module = importlib.import_module(module_path)
            
            # Trouver toutes les classes qui héritent de la classe de base
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Vérifier que c'est une sous-classe (pas la classe de base elle-même)
                if (issubclass(obj, self.base_class) and 
                    obj is not self.base_class and
                    not inspect.isabstract(obj)):
                    
                    # Utiliser le nom du module comme clé
                    plugin_key = self._get_plugin_key(obj, module_name)
                    self.plugins[plugin_key] = obj
                    print(f"Plugin '{plugin_key}' chargé avec succès ({obj.__name__})")
        
        except Exception as e:
            error_info = {
                'plugin_name': module_name,
                'plugin_type': self.plugin_type,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            }
            self.errors.append(error_info)
            print(f"❌ Erreur lors du chargement du plugin {module_name}: {str(e)}")
            print(f"   Détails: {traceback.format_exc()}")
    
    def _get_plugin_key(self, plugin_class, module_name):
        """
        Détermine la clé à utiliser pour le plugin.
        
        Args:
            plugin_class: La classe du plugin
            module_name: Le nom du module
        
        Returns:
            str: La clé du plugin
        """
        # Vérifier si la classe a un attribut plugin_name
        if hasattr(plugin_class, 'plugin_name'):
            return plugin_class.plugin_name
        
        # Sinon, utiliser le nom du module en enlevant les suffixes communs
        key = module_name.replace('_action', '').replace('_plugin', '').replace('_', '')
        return key
    
    def get_plugin(self, plugin_name):
        """
        Récupère une instance d'un plugin par son nom.
        
        Args:
            plugin_name (str): Nom du plugin
        
        Returns:
            Instance du plugin ou None si non trouvé
        """
        plugin_class = self.plugins.get(plugin_name)
        if plugin_class:
            return plugin_class()
        return None
    
    def get_all_plugins(self):
        """
        Retourne tous les plugins disponibles.
        
        Returns:
            dict: Dictionnaire {nom: classe}
        """
        return self.plugins
    
    def get_errors(self):
        """
        Retourne la liste des erreurs de chargement de plugins.
        
        Returns:
            list: Liste des erreurs avec détails
        """
        return self.errors
    
    def has_errors(self):
        """
        Vérifie s'il y a des erreurs de chargement.
        
        Returns:
            bool: True si des erreurs existent
        """
        return len(self.errors) > 0
    
    def clear_errors(self):
        """Efface la liste des erreurs."""
        self.errors.clear()
    
    def reload_plugins(self):
        """Recharge tous les plugins (utile pour le développement)."""
        self.plugins.clear()
        self.errors.clear()
        return self.discover_plugins()
    
    def register_plugin(self, plugin_name, plugin_class):
        """
        Enregistre manuellement un plugin.
        
        Args:
            plugin_name (str): Nom du plugin
            plugin_class: Classe du plugin
        
        Returns:
            bool: True si enregistré avec succès
        """
        if not issubclass(plugin_class, self.base_class):
            print(f"Erreur: {plugin_class.__name__} n'hérite pas de {self.base_class.__name__}")
            return False
        
        self.plugins[plugin_name] = plugin_class
        print(f"Plugin '{plugin_name}' enregistré manuellement")
        return True
    
    def unregister_plugin(self, plugin_name):
        """
        Désenregistre un plugin.
        
        Args:
            plugin_name (str): Nom du plugin
        
        Returns:
            bool: True si désenregistré avec succès
        """
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            print(f"Plugin '{plugin_name}' désenregistré")
            return True
        return False
    
    def get_plugin_info(self, plugin_name):
        """
        Récupère les informations sur un plugin.
        
        Args:
            plugin_name (str): Nom du plugin
        
        Returns:
            dict: Informations sur le plugin
        """
        plugin_class = self.plugins.get(plugin_name)
        if not plugin_class:
            return None
        
        info = {
            'name': plugin_name,
            'class': plugin_class.__name__,
            'module': plugin_class.__module__,
        }
        
        # Ajouter la documentation si disponible
        if plugin_class.__doc__:
            info['description'] = plugin_class.__doc__.strip()
        
        # Ajouter les métadonnées personnalisées si disponibles
        for attr in ['version', 'author', 'plugin_name']:
            if hasattr(plugin_class, attr):
                info[attr] = getattr(plugin_class, attr)
        
        return info
    
    def list_plugins(self):
        """
        Liste tous les plugins disponibles avec leurs informations.
        
        Returns:
            list: Liste des informations de plugins
        """
        return [self.get_plugin_info(name) for name in self.plugins.keys()]
