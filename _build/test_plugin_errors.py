#!/usr/bin/env python3
"""Script de test pour vérifier le système de gestion des erreurs de plugins."""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.plugin_manager import PluginManager
from plugins.actions.action_base import ActionBase

print("=" * 60)
print("Test du système de gestion des erreurs de plugins")
print("=" * 60)

# Créer le gestionnaire de plugins
plugin_manager = PluginManager('actions', ActionBase)

print("\n1. Chargement des plugins...")
plugins = plugin_manager.discover_plugins()

print(f"\n2. Résultats du chargement:")
print(f"   - Plugins chargés avec succès: {len(plugins)}")
print(f"   - Erreurs détectées: {len(plugin_manager.get_errors())}")

if plugin_manager.has_errors():
    print("\n3. ⚠️  ERREURS DÉTECTÉES:")
    for i, error in enumerate(plugin_manager.get_errors(), 1):
        print(f"\n   Erreur #{i}:")
        print(f"   - Plugin: {error['plugin_name']}")
        print(f"   - Type: {error['plugin_type']}")
        print(f"   - Message: {error['error']}")
        print(f"   - Timestamp: {error['timestamp']}")
        print(f"   - Trace complète:")
        print("   " + "-" * 56)
        for line in error['traceback'].split('\n'):
            print(f"   {line}")
        print("   " + "-" * 56)
else:
    print("\n3. ✅ Aucune erreur détectée - tous les plugins sont OK!")

print("\n4. Plugins chargés avec succès:")
for plugin_key in plugins.keys():
    print(f"   ✓ {plugin_key}")

print("\n" + "=" * 60)
print("Test terminé")
print("=" * 60)
