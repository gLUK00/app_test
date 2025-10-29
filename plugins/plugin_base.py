"""Classe de base pour tous les plugins."""
from abc import ABC, abstractmethod


class PluginBase(ABC):
    """
    Classe de base abstraite pour tous les types de plugins.
    Définit l'interface commune que tous les plugins doivent implémenter.
    """
    
    # Métadonnées du plugin (à surcharger dans les sous-classes)
    plugin_name = None  # Nom unique du plugin
    version = "1.0.0"
    author = "TestGyver"
    
    @abstractmethod
    def get_metadata(self):
        """
        Retourne les métadonnées du plugin.
        
        Returns:
            dict: Métadonnées du plugin (nom, version, description, etc.)
        """
        pass
    
    @abstractmethod
    def validate_config(self, config):
        """
        Valide la configuration du plugin.
        
        Args:
            config (dict): Configuration à valider
        
        Returns:
            tuple: (bool, str) - (succès, message d'erreur éventuel)
        """
        pass
