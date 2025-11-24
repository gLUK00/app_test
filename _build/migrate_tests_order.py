#!/usr/bin/env python3
"""
Script de migration pour ajouter le champ 'order' aux tests existants.

Ce script :
- Parcourt toutes les campagnes
- Pour chaque campagne, récupère ses tests
- Attribue un ordre séquentiel aux tests qui n'en ont pas
- Basé sur la date de création (les plus anciens en premier)
"""

import sys
import os
from bson import ObjectId

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.campain import Campain
from utils.db import get_collection

def migrate_tests_order():
    """Migre les tests existants pour ajouter le champ 'order'."""
    
    print("=" * 80)
    print("🔄 MIGRATION: Ajout du champ 'order' aux tests existants")
    print("=" * 80)
    
    try:
        # Récupérer toutes les campagnes
        print("\n📝 Étape 1: Récupération des campagnes")
        campains = Campain.get_all()
        print(f"   ✓ {len(campains)} campagne(s) trouvée(s)")
        
        if not campains:
            print("\n✅ Aucune campagne à migrer")
            return True
        
        # Pour chaque campagne, mettre à jour ses tests
        test_collection = get_collection('tests')
        total_updated = 0
        
        print("\n📝 Étape 2: Mise à jour des tests par campagne")
        
        for campain in campains:
            campain_id = campain['_id']
            campain_name = campain.get('name', 'Sans nom')
            
            # Récupérer les tests de la campagne triés par date de création
            tests = list(test_collection.find({
                'campainId': ObjectId(campain_id)
            }).sort('dateCreated', 1))
            
            if not tests:
                continue
            
            print(f"\n   Campagne: {campain_name} ({campain_id})")
            print(f"      {len(tests)} test(s) à traiter")
            
            # Compter combien de tests ont déjà un ordre
            tests_with_order = sum(1 for test in tests if 'order' in test)
            tests_without_order = len(tests) - tests_with_order
            
            if tests_without_order == 0:
                print(f"      ✓ Tous les tests ont déjà un ordre")
                continue
            
            print(f"      ⚠ {tests_without_order} test(s) sans ordre")
            
            # Attribuer un ordre séquentiel
            order = 1
            for test in tests:
                if 'order' not in test:
                    # Mettre à jour le test avec un ordre
                    test_collection.update_one(
                        {'_id': test['_id']},
                        {'$set': {'order': order}}
                    )
                    total_updated += 1
                    print(f"         - Test {test['_id']}: ordre = {order}")
                else:
                    # Récupérer l'ordre existant pour continuer la séquence
                    order = test['order']
                
                order += 1
        
        print("\n" + "=" * 80)
        print(f"✅ MIGRATION TERMINÉE: {total_updated} test(s) mis à jour")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = migrate_tests_order()
    sys.exit(0 if success else 1)
