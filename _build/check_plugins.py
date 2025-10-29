#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script de vérification du système de plugins."""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugins import plugin_registry


def main():
    """Vérifie que tous les plugins sont chargés correctement."""
    print("=" * 60)
    print("Verification du systeme de plugins TestGyver")
    print("=" * 60)
    print()
    
    # Récupérer tous les plugins
    all_plugins = plugin_registry.get_all_plugins()
    
    # Afficher les statistiques
    counts = plugin_registry.get_plugin_count()
    total = sum(counts.values())
    
    print("Statistiques globales:")
    print(f"   Total de plugins charges: {total}")
    print()
    
    # Afficher les plugins par type
    for plugin_type, count in counts.items():
        print(f"{plugin_type.upper()}: {count} plugin(s)")
        
        # Récupérer le gestionnaire
        manager = plugin_registry.get_manager(plugin_type)
        if manager:
            plugins_list = manager.list_plugins()
            for plugin_info in plugins_list:
                name = plugin_info.get('name', 'N/A')
                version = plugin_info.get('version', 'N/A')
                description = plugin_info.get('description', 'N/A')
                print(f"   OK {name} (v{version})")
                print(f"     {description}")
        print()
    
    # Vérifier que les plugins essentiels sont chargés
    print("Verification des plugins essentiels:")
    essential_plugins = {
        'actions': ['http', 'ssh', 'ftp', 'sftp', 'webdav'],
        'reports': ['html'],
        'auth': ['local']
    }
    
    all_ok = True
    for plugin_type, plugin_names in essential_plugins.items():
        manager = plugin_registry.get_manager(plugin_type)
        if not manager:
            print(f"   ERREUR: Gestionnaire '{plugin_type}' non trouve")
            all_ok = False
            continue
        
        for plugin_name in plugin_names:
            plugin = manager.get_plugin(plugin_name)
            if plugin:
                print(f"   OK {plugin_type}/{plugin_name}")
            else:
                print(f"   ERREUR: {plugin_type}/{plugin_name} MANQUANT")
                all_ok = False
    
    print()
    print("=" * 60)
    if all_ok:
        print("SUCCES: Tous les plugins essentiels sont charges correctement!")
        return 0
    else:
        print("ERREUR: Certains plugins essentiels sont manquants!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
