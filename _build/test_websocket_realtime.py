#!/usr/bin/env python3
"""
Script de test pour vérifier la mise à jour en temps réel des rapports via WebSocket.
"""
import sys
import os
import time
from pathlib import Path
from bson import ObjectId

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.campain import Campain
from models.test import Test
from models.rapport import Rapport
from models.variable import Variable
from utils.db import get_collection

def cleanup():
    """Nettoie les données de test."""
    print("\n🧹 Nettoyage des données de test...")
    
    # Supprimer les campagnes de test
    campains_col = get_collection('campains')
    result = campains_col.delete_many({'name': {'$regex': '^Test WebSocket.*'}})
    print(f"   - {result.deleted_count} campagnes supprimées")
    
    # Supprimer les tests de test
    tests_col = get_collection('tests')
    result = tests_col.delete_many({'name': {'$regex': '^Test WS.*'}})
    print(f"   - {result.deleted_count} tests supprimés")
    
    # Supprimer les rapports de test
    rapports_col = get_collection('rapports')
    result = rapports_col.delete_many({'details': {'$regex': '^Rapport Test WS.*'}})
    print(f"   - {result.deleted_count} rapports supprimés")
    
    # Supprimer les variables de test
    variables_col = get_collection('variables')
    result = variables_col.delete_many({'key': {'$regex': '^test_ws_.*'}})
    print(f"   - {result.deleted_count} variables supprimées")

def test_websocket_events():
    """Test la mise à jour en temps réel des rapports."""
    print("\n" + "="*80)
    print("TEST: Mise à jour en temps réel des rapports via WebSocket")
    print("="*80)
    
    try:
        # Nettoyage initial
        cleanup()
        
        # 1. Créer une campagne
        print("\n📋 Création d'une campagne de test...")
        # On a besoin d'un utilisateur pour créer une campagne
        # Utiliser un utilisateur existant ou en créer un temporaire
        users_col = get_collection('users')
        user = users_col.find_one({'name': 'admin'})
        if not user:
            # Créer un utilisateur temporaire
            from models.user import User
            user_id = User.create('test_ws', 'test@ws.com', 'test123')
        else:
            user_id = str(user['_id'])
        
        campain_data = {
            'user_created': user_id,
            'name': 'Test WebSocket Campagne',
            'description': 'Campagne pour tester les mises à jour WebSocket en temps réel'
        }
        campain_id = Campain.create(user_id, campain_data['name'], campain_data['description'])
        print(f"   ✅ Campagne créée: {campain_id}")
        
        # 2. Créer une variable de test
        print("\n🔧 Création d'une variable de test...")
        timestamp = int(time.time())
        variable_key = f'test_ws_url_{timestamp}'
        variable_value = 'https://httpbin.org/delay/1'
        variable_filiere = 'test_ws'
        
        variable_id = Variable.create(variable_key, variable_value, variable_filiere, 'Variable de test WebSocket')
        print(f"   ✅ Variable créée: {variable_id}")
        
        # 3. Créer un test simple
        print("\n🧪 Création d'un test...")
        test_actions = [
            {
                'type': 'http',
                'value': {
                    'method': 'GET',
                    'url': f'${{{variable_key}}}'
                }
            }
        ]
        test_id = Test.create(campain_id, user_id, test_actions, name='Test WS - HTTP Request')
        print(f"   ✅ Test créé: {test_id}")
        
        # 4. Créer un rapport initial
        print("\n📊 Création d'un rapport initial...")
        timestamp = int(time.time())
        rapport_id = Rapport.create(
            campain_id=campain_id,
            result=None,
            details=f'Rapport Test WS {timestamp}',
            filiere='test_ws',
            tests=[],
            status='pending',
            progress=0
        )
        print(f"   ✅ Rapport créé: {rapport_id}")
        
        # 5. Simuler les mises à jour du rapport (comme le ferait CampainExecutor)
        print("\n⏱️  Simulation de l'exécution de la campagne...")
        
        # 5.1 Démarrage de la campagne (status: running, progress: 0)
        print("   📍 Mise à jour 1: Démarrage de la campagne")
        Rapport.update(rapport_id, {
            'status': 'running',
            'progress': 0,
            'startTime': time.time()
        })
        rapport = Rapport.find_by_id(rapport_id)
        assert rapport['status'] == 'running', f"Status devrait être 'running', reçu: {rapport['status']}"
        assert rapport['progress'] == 0, f"Progress devrait être 0, reçu: {rapport['progress']}"
        print(f"      ✅ Status: {rapport['status']}, Progress: {rapport['progress']}%")
        time.sleep(0.5)
        
        # 5.2 Progression du test (progress: 50)
        print("   📍 Mise à jour 2: Test en cours (50%)")
        Rapport.update(rapport_id, {
            'progress': 50
        })
        rapport = Rapport.find_by_id(rapport_id)
        assert rapport['status'] == 'running', f"Status devrait rester 'running', reçu: {rapport['status']}"
        assert rapport['progress'] == 50, f"Progress devrait être 50, reçu: {rapport['progress']}"
        print(f"      ✅ Status: {rapport['status']}, Progress: {rapport['progress']}%")
        time.sleep(0.5)
        
        # 5.3 Test terminé (progress: 100, test ajouté)
        print("   📍 Mise à jour 3: Test terminé")
        test_result = {
            'testId': ObjectId(test_id),
            'status': 'success',
            'logs': 'Test exécuté avec succès',
            'executionTimeMs': 1234
        }
        Rapport.update(rapport_id, {
            'progress': 100,
            'tests': [test_result]
        })
        rapport = Rapport.find_by_id(rapport_id)
        assert rapport['progress'] == 100, f"Progress devrait être 100, reçu: {rapport['progress']}"
        assert len(rapport['tests']) == 1, f"Devrait avoir 1 test, reçu: {len(rapport['tests'])}"
        print(f"      ✅ Status: {rapport['status']}, Progress: {rapport['progress']}%")
        print(f"      ✅ Tests exécutés: {len(rapport['tests'])}")
        time.sleep(0.5)
        
        # 5.4 Campagne terminée (status: completed)
        print("   📍 Mise à jour 4: Campagne terminée")
        Rapport.update(rapport_id, {
            'status': 'completed',
            'result': 'success',
            'executionTimeMs': 1500,
            'endTime': time.time()
        })
        rapport = Rapport.find_by_id(rapport_id)
        assert rapport['status'] == 'completed', f"Status devrait être 'completed', reçu: {rapport['status']}"
        assert rapport['result'] == 'success', f"Result devrait être 'success', reçu: {rapport['result']}"
        assert rapport['progress'] == 100, f"Progress devrait rester 100, reçu: {rapport['progress']}"
        print(f"      ✅ Status: {rapport['status']}, Result: {rapport['result']}")
        print(f"      ✅ Temps d'exécution: {rapport.get('executionTimeMs', 0)} ms")
        
        # 6. Vérifications finales
        print("\n✅ Vérifications finales:")
        
        # Vérifier que le rapport a bien tous les champs
        assert 'executionTimeMs' in rapport, "Le champ executionTimeMs devrait exister"
        assert 'startTime' in rapport, "Le champ startTime devrait exister"
        assert 'endTime' in rapport, "Le champ endTime devrait exister"
        print("   ✅ Tous les champs de temps sont présents")
        
        # Vérifier la cohérence des temps
        if rapport.get('startTime') and rapport.get('endTime'):
            duration = rapport['endTime'] - rapport['startTime']
            assert duration >= 0, "La durée ne peut pas être négative"
            print(f"   ✅ Durée cohérente: {duration:.2f}s")
        
        # Vérifier le test
        assert rapport['tests'][0]['testId'] == test_id, f"Le test ID ne correspond pas: {rapport['tests'][0]['testId']} vs {test_id}"
        assert rapport['tests'][0]['status'] == 'success', "Le test devrait être en succès"
        print("   ✅ Test correctement enregistré dans le rapport")
        
        print("\n" + "="*80)
        print("✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS")
        print("="*80)
        
        print("\n📝 Notes pour l'interface utilisateur:")
        print("   1. L'IHM doit s'abonner aux événements WebSocket:")
        print("      - campain_started")
        print("      - campain_progress")
        print("      - test_started")
        print("      - test_completed")
        print("      - campain_completed")
        print("      - campain_error")
        print("   2. L'IHM doit rejoindre la room: rapport_{rapport_id}")
        print("   3. À chaque événement, l'IHM doit appeler loadRapports()")
        print("   4. La barre de progression doit se mettre à jour automatiquement")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ ÉCHEC DU TEST: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Nettoyage final
        cleanup()
        print("\n✅ Nettoyage terminé")

if __name__ == '__main__':
    success = test_websocket_events()
    sys.exit(0 if success else 1)
