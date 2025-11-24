#!/usr/bin/env python3
"""
Script de test pour valider la fonctionnalité d'ordre des tests dans une campagne.

Ce script teste :
- La création de tests avec ordre automatique
- Le tri des tests par ordre d'exécution
- Le déplacement de tests (move_up / move_down)
- La persistance de l'ordre lors de l'exécution
"""

import sys
import os
from datetime import datetime
from bson import ObjectId

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.test import Test
from models.campain import Campain
from models.user import User
from utils.db import get_collection

def cleanup_test_data(campain_id):
    """Nettoie les données de test créées."""
    print("\n🧹 Nettoyage des données de test...")
    
    # Supprimer les tests de la campagne
    test_collection = get_collection(Test.collection_name)
    result = test_collection.delete_many({'campainId': ObjectId(campain_id)})
    print(f"   ✓ {result.deleted_count} test(s) supprimé(s)")
    
    # Supprimer la campagne
    campain_collection = get_collection(Campain.collection_name)
    campain_collection.delete_one({'_id': ObjectId(campain_id)})
    print(f"   ✓ Campagne supprimée")

def test_order_functionality():
    """Teste la fonctionnalité d'ordre des tests."""
    
    print("=" * 80)
    print("🧪 TEST DE LA FONCTIONNALITÉ D'ORDRE DES TESTS")
    print("=" * 80)
    
    try:
        # 1. Créer un utilisateur de test ou récupérer le premier
        print("\n📝 Étape 1: Préparation des données")
        user_collection = get_collection(User.collection_name)
        user = user_collection.find_one()
        if not user:
            print("   ❌ Aucun utilisateur trouvé. Créez un utilisateur d'abord.")
            return False
        
        user_id = str(user['_id'])
        print(f"   ✓ Utilisateur: {user['name']} ({user_id})")
        
        # 2. Créer une campagne de test
        campain_id = Campain.create(
            user_created=user_id,
            name=f"Test Ordre - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description="Campagne de test pour valider l'ordre des tests"
        )
        print(f"   ✓ Campagne créée: {campain_id}")
        
        # 3. Créer plusieurs tests
        print("\n📝 Étape 2: Création de 5 tests")
        test_ids = []
        for i in range(1, 6):
            test_id = Test.create(
                campain_id=campain_id,
                user_id=user_id,
                actions=[{
                    'type': 'http',
                    'value': {
                        'method': 'GET',
                        'url': f'https://example.com/test{i}'
                    }
                }],
                name=f"Test {i}",
                description=f"Test numéro {i}"
            )
            test_ids.append(test_id)
            print(f"   ✓ Test {i} créé: {test_id}")
        
        # 4. Vérifier l'ordre initial
        print("\n📝 Étape 3: Vérification de l'ordre initial")
        tests = Test.get_by_campain(campain_id)
        
        if len(tests) != 5:
            print(f"   ❌ Erreur: {len(tests)} tests trouvés au lieu de 5")
            cleanup_test_data(campain_id)
            return False
        
        print("   Ordre actuel:")
        for idx, test in enumerate(tests):
            order = test.get('order', 'N/A')
            print(f"      {idx + 1}. {test['name']} (order={order})")
        
        # Vérifier que l'ordre est séquentiel
        expected_orders = [1, 2, 3, 4, 5]
        actual_orders = [test.get('order') for test in tests]
        
        if actual_orders != expected_orders:
            print(f"   ❌ Ordre incorrect. Attendu: {expected_orders}, Obtenu: {actual_orders}")
            cleanup_test_data(campain_id)
            return False
        
        print("   ✓ Ordre initial correct (1, 2, 3, 4, 5)")
        
        # 5. Déplacer le test 3 vers le haut (position 2)
        print("\n📝 Étape 4: Déplacement du test 3 vers le haut")
        test_3_id = test_ids[2]  # Index 2 = Test 3
        success = Test.move_up(test_3_id)
        
        if not success:
            print("   ❌ Erreur lors du déplacement vers le haut")
            cleanup_test_data(campain_id)
            return False
        
        tests = Test.get_by_campain(campain_id)
        print("   Nouvel ordre:")
        for idx, test in enumerate(tests):
            order = test.get('order')
            print(f"      {idx + 1}. {test['name']} (order={order})")
        
        # Vérifier que Test 3 est maintenant en position 2
        if tests[1]['name'] != 'Test 3':
            print(f"   ❌ Test 3 devrait être en position 2, mais c'est: {tests[1]['name']}")
            cleanup_test_data(campain_id)
            return False
        
        print("   ✓ Test 3 déplacé avec succès en position 2")
        
        # 6. Déplacer le test 1 vers le bas (position 2)
        print("\n📝 Étape 5: Déplacement du test 1 vers le bas")
        test_1_id = test_ids[0]  # Index 0 = Test 1
        success = Test.move_down(test_1_id)
        
        if not success:
            print("   ❌ Erreur lors du déplacement vers le bas")
            cleanup_test_data(campain_id)
            return False
        
        tests = Test.get_by_campain(campain_id)
        print("   Nouvel ordre:")
        for idx, test in enumerate(tests):
            order = test.get('order')
            print(f"      {idx + 1}. {test['name']} (order={order})")
        
        # Vérifier que Test 1 est maintenant en position 2
        if tests[1]['name'] != 'Test 1':
            print(f"   ❌ Test 1 devrait être en position 2, mais c'est: {tests[1]['name']}")
            cleanup_test_data(campain_id)
            return False
        
        print("   ✓ Test 1 déplacé avec succès en position 2")
        
        # 7. Tester les limites (déplacer le premier vers le haut = impossible)
        print("\n📝 Étape 6: Test des limites")
        first_test_id = tests[0]['_id']
        success = Test.move_up(first_test_id)
        
        if success:
            print("   ❌ Le premier test ne devrait pas pouvoir monter")
            cleanup_test_data(campain_id)
            return False
        
        print("   ✓ Impossible de monter le premier test (comportement attendu)")
        
        # Tester le dernier vers le bas
        last_test_id = tests[-1]['_id']
        success = Test.move_down(last_test_id)
        
        if success:
            print("   ❌ Le dernier test ne devrait pas pouvoir descendre")
            cleanup_test_data(campain_id)
            return False
        
        print("   ✓ Impossible de descendre le dernier test (comportement attendu)")
        
        # 8. Vérifier l'ordre final
        print("\n📝 Étape 7: Vérification de l'ordre final")
        tests = Test.get_by_campain(campain_id)
        print("   Ordre final:")
        for idx, test in enumerate(tests):
            order = test.get('order')
            print(f"      {idx + 1}. {test['name']} (order={order})")
        
        # 9. Nettoyer les données de test
        cleanup_test_data(campain_id)
        
        print("\n" + "=" * 80)
        print("✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Essayer de nettoyer en cas d'erreur
        try:
            if 'campain_id' in locals():
                cleanup_test_data(campain_id)
        except:
            pass
        
        return False

if __name__ == '__main__':
    success = test_order_functionality()
    sys.exit(0 if success else 1)
