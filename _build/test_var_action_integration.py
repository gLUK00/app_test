#!/usr/bin/env python3
"""
Test d'intégration du plugin VarAction avec le système de variables
Simule une exécution complète avec résolution de variables
"""

import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.actions.var_action import VarAction


def test_integration_with_variable_resolution():
    """Test d'intégration avec résolution de variables."""
    print("\n" + "=" * 70)
    print("TEST D'INTÉGRATION VARACTION AVEC RÉSOLUTION DE VARIABLES")
    print("=" * 70)
    
    action = VarAction()
    
    # Simuler un contexte d'exécution avec plusieurs variables
    test_variables = {
        'http_status': '200',
        'user_age': '25',
        'is_active': 'true',
        'user_data': '{"id": 123, "name": "John Doe", "email": "john@example.com"}',
        'tags': '["admin", "user", "editor"]',
        'price': '19.99'
    }
    
    print("\n📦 Variables du test disponibles:")
    for key, value in test_variables.items():
        print(f"   {key}: {value} (type: {type(value).__name__})")
    
    # Test 1: Conversion d'un status HTTP
    print("\n" + "-" * 70)
    print("Test 1: Conversion du status HTTP (string → int)")
    print("-" * 70)
    
    context = {
        'variable_name': 'http_status',
        'target_type': 'int',
        'variables': test_variables.copy()
    }
    
    code, logs, output = action.execute(context)
    print(logs)
    
    if code == 0 and output.get('converted_value') == 200:
        print("✅ Test 1 RÉUSSI : '200' converti en 200 (int)")
        test_variables['http_status_int'] = output['converted_value']
    else:
        print("❌ Test 1 ÉCHOUÉ")
        return False
    
    # Test 2: Conversion d'un flag booléen
    print("\n" + "-" * 70)
    print("Test 2: Conversion du flag is_active (string → bool)")
    print("-" * 70)
    
    context = {
        'variable_name': 'is_active',
        'target_type': 'bool',
        'variables': test_variables.copy()
    }
    
    code, logs, output = action.execute(context)
    print(logs)
    
    if code == 0 and output.get('converted_value') is True:
        print("✅ Test 2 RÉUSSI : 'true' converti en True (bool)")
        test_variables['is_active_bool'] = output['converted_value']
    else:
        print("❌ Test 2 ÉCHOUÉ")
        return False
    
    # Test 3: Parsing d'un JSON en dictionnaire
    print("\n" + "-" * 70)
    print("Test 3: Parsing du user_data (string JSON → dict)")
    print("-" * 70)
    
    context = {
        'variable_name': 'user_data',
        'target_type': 'dict',
        'variables': test_variables.copy()
    }
    
    code, logs, output = action.execute(context)
    print(logs)
    
    expected_dict = {"id": 123, "name": "John Doe", "email": "john@example.com"}
    if code == 0 and output.get('converted_value') == expected_dict:
        print("✅ Test 3 RÉUSSI : JSON converti en dict")
        test_variables['user_dict'] = output['converted_value']
    else:
        print("❌ Test 3 ÉCHOUÉ")
        return False
    
    # Test 4: Conversion d'un JSON array en liste
    print("\n" + "-" * 70)
    print("Test 4: Conversion des tags (string JSON → list)")
    print("-" * 70)
    
    context = {
        'variable_name': 'tags',
        'target_type': 'list',
        'variables': test_variables.copy()
    }
    
    code, logs, output = action.execute(context)
    print(logs)
    
    expected_list = ["admin", "user", "editor"]
    if code == 0 and output.get('converted_value') == expected_list:
        print("✅ Test 4 RÉUSSI : JSON array converti en list")
        test_variables['tags_list'] = output['converted_value']
    else:
        print("❌ Test 4 ÉCHOUÉ")
        return False
    
    # Test 5: Conversion d'un prix en float
    print("\n" + "-" * 70)
    print("Test 5: Conversion du prix (string → float)")
    print("-" * 70)
    
    context = {
        'variable_name': 'price',
        'target_type': 'float',
        'variables': test_variables.copy()
    }
    
    code, logs, output = action.execute(context)
    print(logs)
    
    if code == 0 and output.get('converted_value') == 19.99:
        print("✅ Test 5 RÉUSSI : '19.99' converti en 19.99 (float)")
        test_variables['price_float'] = output['converted_value']
    else:
        print("❌ Test 5 ÉCHOUÉ")
        return False
    
    # Test 6: Conversion d'un dict en JSON string
    print("\n" + "-" * 70)
    print("Test 6: Sérialisation du user_dict (dict → JSON string)")
    print("-" * 70)
    
    context = {
        'variable_name': 'user_dict',
        'target_type': 'json',
        'variables': test_variables.copy()
    }
    
    code, logs, output = action.execute(context)
    print(logs)
    
    if code == 0 and isinstance(output.get('converted_value'), str):
        import json
        parsed = json.loads(output['converted_value'])
        if parsed == expected_dict:
            print("✅ Test 6 RÉUSSI : dict converti en JSON string valide")
            test_variables['user_json'] = output['converted_value']
        else:
            print("❌ Test 6 ÉCHOUÉ : JSON invalide")
            return False
    else:
        print("❌ Test 6 ÉCHOUÉ")
        return False
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES VARIABLES APRÈS TOUTES LES CONVERSIONS")
    print("=" * 70)
    
    for key, value in test_variables.items():
        print(f"   {key}: {value} (type: {type(value).__name__})")
    
    print("\n" + "=" * 70)
    print("✅ TOUS LES TESTS D'INTÉGRATION SONT PASSÉS")
    print("=" * 70)
    
    return True


def test_real_world_scenario():
    """Test d'un scénario réel d'utilisation."""
    print("\n" + "=" * 70)
    print("SCÉNARIO RÉEL : VALIDATION D'UNE RÉPONSE API")
    print("=" * 70)
    
    action = VarAction()
    
    # Simuler une réponse API
    api_response = {
        'status': '200',
        'body': '{"success": true, "data": {"user_id": "12345", "balance": "150.75"}, "errors": []}'
    }
    
    print("\n📥 Réponse API simulée:")
    print(f"   Status: {api_response['status']}")
    print(f"   Body: {api_response['body']}")
    
    # Étape 1: Convertir le status en int
    print("\n🔄 Étape 1: Conversion du status")
    context = {
        'variable_name': 'api_status',
        'target_type': 'int',
        'variables': {'api_status': api_response['status']}
    }
    code, logs, output = action.execute(context)
    print(logs)
    
    if code != 0:
        print("❌ Échec de la conversion du status")
        return False
    
    status_int = output['converted_value']
    print(f"✅ Status converti: {status_int} (type: {type(status_int).__name__})")
    
    # Étape 2: Parser le body JSON
    print("\n🔄 Étape 2: Parsing du body JSON")
    context = {
        'variable_name': 'api_body',
        'target_type': 'dict',
        'variables': {'api_body': api_response['body']}
    }
    code, logs, output = action.execute(context)
    print(logs)
    
    if code != 0:
        print("❌ Échec du parsing du body")
        return False
    
    body_dict = output['converted_value']
    print(f"✅ Body parsé: {body_dict}")
    
    # Étape 3: Extraire et convertir l'user_id
    print("\n🔄 Étape 3: Conversion de l'user_id")
    # Simuler l'extraction (dans un vrai cas, ce serait fait par une autre action)
    user_id_str = body_dict['data']['user_id']
    
    context = {
        'variable_name': 'user_id_str',
        'target_type': 'int',
        'variables': {'user_id_str': user_id_str}
    }
    code, logs, output = action.execute(context)
    print(logs)
    
    if code != 0:
        print("❌ Échec de la conversion de l'user_id")
        return False
    
    user_id = output['converted_value']
    print(f"✅ User ID converti: {user_id} (type: {type(user_id).__name__})")
    
    # Étape 4: Convertir le balance en float
    print("\n🔄 Étape 4: Conversion du balance")
    balance_str = body_dict['data']['balance']
    
    context = {
        'variable_name': 'balance_str',
        'target_type': 'float',
        'variables': {'balance_str': balance_str}
    }
    code, logs, output = action.execute(context)
    print(logs)
    
    if code != 0:
        print("❌ Échec de la conversion du balance")
        return False
    
    balance = output['converted_value']
    print(f"✅ Balance converti: {balance} (type: {type(balance).__name__})")
    
    # Validation finale
    print("\n" + "=" * 70)
    print("📋 RÉSULTATS FINAUX")
    print("=" * 70)
    print(f"   Status HTTP: {status_int} (int)")
    print(f"   User ID: {user_id} (int)")
    print(f"   Balance: {balance} (float)")
    print(f"   Données parsées: {body_dict}")
    
    # Vérifications
    checks = [
        (status_int == 200, "Status HTTP est 200"),
        (isinstance(user_id, int), "User ID est un entier"),
        (isinstance(balance, float), "Balance est un float"),
        (balance > 0, "Balance est positif"),
    ]
    
    all_passed = all(check[0] for check in checks)
    
    print("\n🔍 Vérifications:")
    for passed, description in checks:
        print(f"   {'✅' if passed else '❌'} {description}")
    
    if all_passed:
        print("\n" + "=" * 70)
        print("✅ SCÉNARIO RÉEL RÉUSSI")
        print("=" * 70)
    else:
        print("\n❌ SCÉNARIO RÉEL ÉCHOUÉ")
    
    return all_passed


def run_all_tests():
    """Exécute tous les tests."""
    print("\n" + "#" * 70)
    print("# TESTS D'INTÉGRATION DU PLUGIN VARACTION")
    print("#" * 70)
    
    try:
        # Test d'intégration avec variables
        if not test_integration_with_variable_resolution():
            return False
        
        # Test de scénario réel
        if not test_real_world_scenario():
            return False
        
        print("\n" + "#" * 70)
        print("# ✅ TOUS LES TESTS D'INTÉGRATION SONT PASSÉS")
        print("#" * 70)
        return True
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE : {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
