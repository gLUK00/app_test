#!/usr/bin/env python3
"""Script de test pour vérifier le chargement des plugins d'actions."""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.plugin_manager import PluginManager
from plugins.actions.action_base import ActionBase

print("=" * 60)
print("Test de chargement des plugins d'actions")
print("=" * 60)

# Créer le gestionnaire de plugins
plugin_manager = PluginManager('actions', ActionBase)

print("\n1. Découverte des plugins...")
plugins = plugin_manager.discover_plugins()

print(f"\n2. Nombre de plugins chargés: {len(plugins)}")

if plugins:
    print("\n3. Liste des plugins chargés:")
    for plugin_key, plugin_class in plugins.items():
        print(f"   - '{plugin_key}' -> {plugin_class.__name__}")
        
        # Tester l'instanciation
        try:
            instance = plugin_class()
            metadata = instance.get_metadata()
            print(f"     ✓ Instanciation réussie")
            print(f"     Métadonnées: {metadata}")
        except Exception as e:
            print(f"     ✗ Erreur d'instanciation: {e}")
else:
    print("\n⚠️  AUCUN PLUGIN CHARGÉ!")

print("\n4. Test de récupération du plugin 'webdav':")
webdav_plugin = plugin_manager.get_plugin('webdav')
if webdav_plugin:
    print(f"   ✓ Plugin 'webdav' trouvé: {webdav_plugin}")
    print(f"   Classe: {type(webdav_plugin).__name__}")
else:
    print("   ✗ Plugin 'webdav' NON TROUVÉ")

print("\n" + "=" * 60)
