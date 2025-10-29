#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migration pour uniformiser la structure des actions.
Convertit toutes les actions de 'parameters' vers 'value'.
"""

import json
from utils.db import get_collection

def migrate_actions():
    """Migre toutes les actions de 'parameters' vers 'value'."""
    collection = get_collection('tests')
    
    # Récupérer tous les tests
    tests = list(collection.find({}))
    
    print(f"Nombre de tests trouvés : {len(tests)}")
    
    migrated_count = 0
    error_count = 0
    
    for test in tests:
        test_id = test['_id']
        actions = test.get('actions', [])
        
        if not actions:
            continue
        
        modified = False
        
        for i, action in enumerate(actions):
            # Si l'action a 'parameters' mais pas 'value'
            if 'parameters' in action and 'value' not in action:
                action['value'] = action['parameters']
                del action['parameters']
                modified = True
                print(f"  Test {test_id}, Action {i}: parameters -> value")
            
            # Si l'action a les deux, garder 'value' et supprimer 'parameters'
            elif 'parameters' in action and 'value' in action:
                del action['parameters']
                modified = True
                print(f"  Test {test_id}, Action {i}: suppression de parameters (doublon)")
        
        # Mettre à jour le test si modifié
        if modified:
            try:
                collection.update_one(
                    {'_id': test_id},
                    {'$set': {'actions': actions}}
                )
                migrated_count += 1
                print(f"✓ Test {test_id} migré avec succès")
            except Exception as e:
                error_count += 1
                print(f"✗ Erreur lors de la migration du test {test_id}: {e}")
    
    print("\n" + "="*50)
    print(f"Migration terminée !")
    print(f"  Tests migrés : {migrated_count}")
    print(f"  Erreurs : {error_count}")
    print("="*50)

if __name__ == '__main__':
    print("="*50)
    print("Migration des actions : parameters -> value")
    print("="*50)
    
    response = input("\nVoulez-vous continuer ? (oui/non) : ")
    
    if response.lower() in ['oui', 'o', 'yes', 'y']:
        migrate_actions()
    else:
        print("Migration annulée.")
