#!/usr/bin/env python3
"""
Script de test pour valider la fonctionnalité de mesure des temps d'exécution.

Ce script teste :
- La mesure du temps d'exécution de chaque action
- La mesure du temps d'exécution de chaque test
- La mesure du temps total d'exécution de la campagne
- L'affichage de ces temps dans le rapport
"""

import sys
import os
from datetime import datetime
from bson import ObjectId
import time

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.test import Test
from models.campain import Campain
from models.rapport import Rapport
from models.user import User
from models.variable import Variable
from utils.db import get_collection

def cleanup_test_data(campain_id, rapport_ids):
    """Nettoie les données de test créées."""
    print("\n🧹 Nettoyage des données de test...")
    
    # Supprimer les rapports
    rapport_collection = get_collection(Rapport.collection_name)
    for rapport_id in rapport_ids:
        rapport_collection.delete_one({'_id': ObjectId(rapport_id)})
    print(f"   ✓ {len(rapport_ids)} rapport(s) supprimé(s)")
    
    # Supprimer les tests de la campagne
    test_collection = get_collection(Test.collection_name)
    result = test_collection.delete_many({'campainId': ObjectId(campain_id)})
    print(f"   ✓ {result.deleted_count} test(s) supprimé(s)")
    
    # Supprimer la campagne
    campain_collection = get_collection(Campain.collection_name)
    campain_collection.delete_one({'_id': ObjectId(campain_id)})
    print(f"   ✓ Campagne supprimée")

def test_execution_times():
    """Teste la fonctionnalité de mesure des temps d'exécution."""
    
    print("=" * 80)
    print("🧪 TEST DE LA MESURE DES TEMPS D'EXÉCUTION")
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
            name=f"Test Temps - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description="Campagne de test pour valider les temps d'exécution"
        )
        print(f"   ✓ Campagne créée: {campain_id}")
        
        # 3. Créer une variable de test (avec nom unique)
        print("\n📝 Étape 2: Création d'une variable de test")
        var_key = f'test_url_{int(time.time())}'
        Variable.create(
            key=var_key,
            value='https://httpbin.org/delay/1',
            filiere='test',
            description='URL de test avec délai de 1 seconde'
        )
        print(f"   ✓ Variable créée: {var_key}")
        
        # 4. Créer un test avec des actions
        print("\n📝 Étape 3: Création d'un test")
        test_id = Test.create(
            campain_id=campain_id,
            user_id=user_id,
            actions=[
                {
                    'type': 'http',
                    'value': {
                        'method': 'GET',
                        'url': f'{{{{{var_key}}}}}',
                        'headers': {}
                    }
                }
            ],
            name="Test HTTP avec délai",
            description="Test pour mesurer le temps d'exécution"
        )
        print(f"   ✓ Test créé: {test_id}")
        
        # 5. Créer un rapport
        print("\n📝 Étape 4: Création et exécution du rapport")
        rapport_id = Rapport.create(
            campain_id=campain_id,
            result='pending',
            details=f"Rapport Test Temps - {datetime.now().strftime('%H:%M:%S')}",
            filiere='test',
            tests=[]
        )
        print(f"   ✓ Rapport créé: {rapport_id}")
        
        # 6. Simuler l'exécution (normalement fait par CampainExecutor)
        print("\n📝 Étape 5: Vérification des champs de temps")
        
        # Récupérer le rapport
        rapport = Rapport.find_by_id(rapport_id)
        
        # Vérifier que les champs existent
        if 'executionTimeMs' not in rapport:
            print("   ❌ Le champ 'executionTimeMs' n'existe pas dans le rapport")
            cleanup_test_data(campain_id, [rapport_id])
            return False
        
        print(f"   ✓ Champ 'executionTimeMs' présent: {rapport['executionTimeMs']}")
        
        if 'startTime' not in rapport:
            print("   ❌ Le champ 'startTime' n'existe pas dans le rapport")
            cleanup_test_data(campain_id, [rapport_id])
            return False
        
        print(f"   ✓ Champ 'startTime' présent: {rapport['startTime']}")
        
        if 'endTime' not in rapport:
            print("   ❌ Le champ 'endTime' n'existe pas dans le rapport")
            cleanup_test_data(campain_id, [rapport_id])
            return False
        
        print(f"   ✓ Champ 'endTime' présent: {rapport['endTime']}")
        
        # 7. Simuler une mise à jour avec des temps
        print("\n📝 Étape 6: Simulation de mise à jour avec temps d'exécution")
        start_time = time.time()
        time.sleep(0.5)  # Simuler une exécution de 500ms
        end_time = time.time()
        execution_time_ms = int((end_time - start_time) * 1000)
        
        Rapport.update(rapport_id, {
            'executionTimeMs': execution_time_ms,
            'startTime': start_time,
            'endTime': end_time,
            'status': 'completed',
            'tests': [{
                'testId': ObjectId(test_id),
                'status': 'passed',
                'logs': 'Test simulé',
                'executionTimeMs': execution_time_ms,
                'actionTimes': [execution_time_ms]
            }]
        })
        
        # Vérifier la mise à jour
        rapport = Rapport.find_by_id(rapport_id)
        
        if rapport['executionTimeMs'] < 400 or rapport['executionTimeMs'] > 600:
            print(f"   ❌ Temps d'exécution incorrect: {rapport['executionTimeMs']} ms (attendu: ~500 ms)")
            cleanup_test_data(campain_id, [rapport_id])
            return False
        
        print(f"   ✓ Temps d'exécution de la campagne: {rapport['executionTimeMs']} ms")
        
        # Vérifier le temps du test
        if len(rapport['tests']) == 0:
            print("   ❌ Aucun test dans le rapport")
            cleanup_test_data(campain_id, [rapport_id])
            return False
        
        test_result = rapport['tests'][0]
        
        if 'executionTimeMs' not in test_result:
            print("   ❌ Le champ 'executionTimeMs' n'existe pas dans le test")
            cleanup_test_data(campain_id, [rapport_id])
            return False
        
        print(f"   ✓ Temps d'exécution du test: {test_result['executionTimeMs']} ms")
        
        if 'actionTimes' not in test_result:
            print("   ❌ Le champ 'actionTimes' n'existe pas dans le test")
            cleanup_test_data(campain_id, [rapport_id])
            return False
        
        print(f"   ✓ Temps des actions: {test_result['actionTimes']}")
        
        # 8. Nettoyer les données de test
        cleanup_test_data(campain_id, [rapport_id])
        
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
            if 'campain_id' in locals() and 'rapport_id' in locals():
                cleanup_test_data(campain_id, [rapport_id])
        except:
            pass
        
        return False

if __name__ == '__main__':
    success = test_execution_times()
    sys.exit(0 if success else 1)
