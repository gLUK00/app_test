#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migration pour ajouter le champ isDeleted aux collections existantes.
Ce script ajoute le champ isDeleted: false à tous les documents existants
dans les collections tests, campains et rapports.
"""

import sys
import os

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db import get_collection

def migrate_soft_delete():
    """Ajoute le champ isDeleted: false aux documents existants."""
    
    print("\n" + "="*80)
    print("MIGRATION - Ajout du champ isDeleted aux collections")
    print("="*80 + "\n")
    
    collections_to_migrate = ['tests', 'campains', 'rapports']
    
    for collection_name in collections_to_migrate:
        print(f"\n📋 Migration de la collection '{collection_name}'...")
        
        try:
            collection = get_collection(collection_name)
            
            # Compter les documents sans le champ isDeleted
            count_without_field = collection.count_documents({
                'isDeleted': {'$exists': False}
            })
            
            if count_without_field == 0:
                print(f"  ✅ Aucune migration nécessaire (tous les documents ont déjà le champ)")
                continue
            
            print(f"  📊 {count_without_field} document(s) à migrer")
            
            # Ajouter le champ isDeleted: false aux documents qui ne l'ont pas
            result = collection.update_many(
                {'isDeleted': {'$exists': False}},
                {'$set': {'isDeleted': False}}
            )
            
            print(f"  ✅ Migration terminée : {result.modified_count} document(s) mis à jour")
            
        except Exception as e:
            print(f"  ❌ Erreur lors de la migration de '{collection_name}': {e}")
            return False
    
    print("\n" + "="*80)
    print("✅ MIGRATION TERMINÉE AVEC SUCCÈS")
    print("="*80 + "\n")
    
    return True

def verify_migration():
    """Vérifie que tous les documents ont bien le champ isDeleted."""
    
    print("\n" + "="*80)
    print("VÉRIFICATION - État des collections après migration")
    print("="*80 + "\n")
    
    collections_to_verify = ['tests', 'campains', 'rapports']
    all_ok = True
    
    for collection_name in collections_to_verify:
        print(f"\n📋 Vérification de la collection '{collection_name}'...")
        
        try:
            collection = get_collection(collection_name)
            
            total_docs = collection.count_documents({})
            docs_with_field = collection.count_documents({'isDeleted': {'$exists': True}})
            docs_deleted = collection.count_documents({'isDeleted': True})
            docs_active = collection.count_documents({'isDeleted': False})
            
            print(f"  📊 Total de documents : {total_docs}")
            print(f"  ✅ Documents avec isDeleted : {docs_with_field}")
            print(f"  🗑️  Documents supprimés logiquement : {docs_deleted}")
            print(f"  ✓  Documents actifs : {docs_active}")
            
            if total_docs != docs_with_field:
                print(f"  ⚠️  ATTENTION : {total_docs - docs_with_field} document(s) sans le champ isDeleted")
                all_ok = False
            else:
                print(f"  ✅ Tous les documents ont le champ isDeleted")
            
        except Exception as e:
            print(f"  ❌ Erreur lors de la vérification de '{collection_name}': {e}")
            all_ok = False
    
    print("\n" + "="*80)
    if all_ok:
        print("✅ VÉRIFICATION TERMINÉE : Tout est OK")
    else:
        print("⚠️  VÉRIFICATION TERMINÉE : Des problèmes ont été détectés")
    print("="*80 + "\n")
    
    return all_ok

if __name__ == '__main__':
    print("\n🚀 Démarrage de la migration pour la suppression logique\n")
    
    # Effectuer la migration
    if migrate_soft_delete():
        # Vérifier la migration
        verify_migration()
    else:
        print("\n❌ La migration a échoué\n")
        sys.exit(1)
    
    print("\n✅ Script terminé avec succès\n")
