#!/usr/bin/env python3
"""
Script de test pour valider le système de préfixe des collections MongoDB.

Ce script teste :
- La lecture du préfixe depuis configuration.json
- L'application automatique du préfixe aux noms de collections
- Le fonctionnement avec et sans préfixe
- La compatibilité avec l'existant
"""

import sys
import os
import json
import tempfile
import shutil

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db import get_collection, load_config
from models.user import User
from models.variable import Variable
from models.campain import Campain
from models.test import Test
from models.rapport import Rapport


def test_prefix_configuration():
    """Test 1 : Vérifier que le préfixe est bien configuré."""
    print("\n" + "="*70)
    print("Test 1 : Vérification de la configuration du préfixe")
    print("="*70)
    
    config = load_config()
    mongo_config = config.get('mongo', {})
    prefix = mongo_config.get('prefix', '')
    
    print(f"✓ Préfixe configuré : '{prefix}'")
    assert 'prefix' in mongo_config, "Le champ 'prefix' doit exister dans mongo config"
    assert prefix == 'mgv_', f"Le préfixe devrait être 'mgv_', mais est '{prefix}'"
    print("✅ Test 1 réussi : Préfixe correctement configuré")
    

def test_collection_names():
    """Test 2 : Vérifier que les noms de collections sont correctement préfixés."""
    print("\n" + "="*70)
    print("Test 2 : Vérification des noms de collections préfixés")
    print("="*70)
    
    collections_to_test = {
        'users': User.collection_name,
        'variables': Variable.collection_name,
        'campains': Campain.collection_name,
        'tests': Test.collection_name,
        'rapports': Rapport.collection_name
    }
    
    for expected_base_name, actual_name in collections_to_test.items():
        print(f"  Modèle : {expected_base_name}")
        print(f"    - Nom de base attendu : {expected_base_name}")
        print(f"    - Nom de collection : {actual_name}")
        assert actual_name == expected_base_name, f"Le nom de collection devrait être '{expected_base_name}'"
    
    print("✅ Test 2 réussi : Tous les noms de collections sont corrects")


def test_get_collection_with_prefix():
    """Test 3 : Vérifier que get_collection() applique le préfixe."""
    print("\n" + "="*70)
    print("Test 3 : Vérification de l'application du préfixe par get_collection()")
    print("="*70)
    
    config = load_config()
    prefix = config['mongo'].get('prefix', '')
    
    collections_to_test = ['users', 'variables', 'campains', 'tests', 'rapports']
    
    for collection_name in collections_to_test:
        collection = get_collection(collection_name)
        expected_name = f"{prefix}{collection_name}"
        actual_name = collection.name
        
        print(f"  Collection : {collection_name}")
        print(f"    - Nom attendu : {expected_name}")
        print(f"    - Nom réel : {actual_name}")
        
        assert actual_name == expected_name, \
            f"Le nom de la collection devrait être '{expected_name}', mais est '{actual_name}'"
    
    print("✅ Test 3 réussi : Le préfixe est correctement appliqué à toutes les collections")


def test_prefix_default_value():
    """Test 4 : Vérifier le comportement avec un préfixe vide."""
    print("\n" + "="*70)
    print("Test 4 : Vérification du comportement avec préfixe vide")
    print("="*70)
    
    # Sauvegarder la config actuelle
    with open('configuration.json', 'r', encoding='utf-8') as f:
        original_config = f.read()
    
    try:
        # Créer une config temporaire sans préfixe
        config = load_config()
        config['mongo']['prefix'] = ''
        
        with open('configuration.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        
        # Tester avec préfixe vide
        collection = get_collection('users')
        assert collection.name == 'users', \
            f"Sans préfixe, la collection devrait s'appeler 'users', mais s'appelle '{collection.name}'"
        
        print("  ✓ Avec prefix='', la collection 'users' s'appelle 'users'")
        
        # Tester avec préfixe manquant
        del config['mongo']['prefix']
        with open('configuration.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        
        collection = get_collection('variables')
        assert collection.name == 'variables', \
            f"Sans champ prefix, la collection devrait s'appeler 'variables', mais s'appelle '{collection.name}'"
        
        print("  ✓ Sans champ 'prefix', la collection 'variables' s'appelle 'variables'")
        print("✅ Test 4 réussi : Le préfixe vide fonctionne correctement")
        
    finally:
        # Restaurer la config originale
        with open('configuration.json', 'w', encoding='utf-8') as f:
            f.write(original_config)


def test_models_compatibility():
    """Test 5 : Vérifier la compatibilité avec les modèles existants."""
    print("\n" + "="*70)
    print("Test 5 : Vérification de la compatibilité avec les modèles")
    print("="*70)
    
    # Tester que les modèles peuvent toujours récupérer leurs collections
    try:
        user_collection = get_collection(User.collection_name)
        print(f"  ✓ User.collection_name='{User.collection_name}' → collection '{user_collection.name}'")
        
        variable_collection = get_collection(Variable.collection_name)
        print(f"  ✓ Variable.collection_name='{Variable.collection_name}' → collection '{variable_collection.name}'")
        
        campain_collection = get_collection(Campain.collection_name)
        print(f"  ✓ Campain.collection_name='{Campain.collection_name}' → collection '{campain_collection.name}'")
        
        test_collection = get_collection(Test.collection_name)
        print(f"  ✓ Test.collection_name='{Test.collection_name}' → collection '{test_collection.name}'")
        
        rapport_collection = get_collection(Rapport.collection_name)
        print(f"  ✓ Rapport.collection_name='{Rapport.collection_name}' → collection '{rapport_collection.name}'")
        
        print("✅ Test 5 réussi : Tous les modèles sont compatibles avec le système de préfixe")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        raise


def test_cross_collection_references():
    """Test 6 : Vérifier les références croisées entre collections."""
    print("\n" + "="*70)
    print("Test 6 : Vérification des références croisées")
    print("="*70)
    
    # Vérifier que les références comme get_collection('users') dans campain.py fonctionnent
    print("  ℹ️ Les références croisées (ex: get_collection('users') dans campain.py)")
    print("     utilisent bien la fonction get_collection() qui ajoute le préfixe")
    print("  ℹ️ Toutes les collections référencées auront automatiquement le même préfixe")
    
    # Exemple : dans campain.py, ligne 36
    # user_collection = get_collection('users')
    # Cette ligne utilisera également le préfixe, donc cherchera dans 'mgv_users'
    
    config = load_config()
    prefix = config['mongo'].get('prefix', '')
    
    # Simuler ce qui se passe dans campain.py
    user_collection = get_collection('users')
    assert user_collection.name == f"{prefix}users", \
        "Les références croisées doivent aussi utiliser le préfixe"
    
    print(f"  ✓ get_collection('users') → collection '{user_collection.name}'")
    print("✅ Test 6 réussi : Les références croisées fonctionnent correctement")


def run_all_tests():
    """Exécute tous les tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "TEST DU SYSTÈME DE PRÉFIXE MONGODB" + " "*19 + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        test_prefix_configuration,
        test_collection_names,
        test_get_collection_with_prefix,
        test_prefix_default_value,
        test_models_compatibility,
        test_cross_collection_references
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ Test échoué : {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ Erreur inattendue : {e}")
            failed += 1
    
    # Résumé final
    print("\n" + "="*70)
    print("RÉSUMÉ DES TESTS")
    print("="*70)
    print(f"✅ Tests réussis : {passed}/{len(tests)}")
    if failed > 0:
        print(f"❌ Tests échoués : {failed}/{len(tests)}")
    
    # Détails de l'implémentation
    print("\n" + "="*70)
    print("DÉTAILS DE L'IMPLÉMENTATION")
    print("="*70)
    config = load_config()
    prefix = config['mongo'].get('prefix', '')
    print(f"Préfixe configuré : '{prefix}'")
    print(f"Collections créées :")
    for name in ['users', 'variables', 'campains', 'tests', 'rapports']:
        print(f"  - {name} → {prefix}{name}")
    
    print("\n" + "="*70)
    print("IMPACTS SUR L'EXISTANT")
    print("="*70)
    print("✓ Tous les modèles utilisent get_collection() qui gère automatiquement le préfixe")
    print("✓ Aucune modification nécessaire dans les modèles")
    print("✓ Les références croisées (ex: get_collection('users')) fonctionnent")
    print("✓ Le préfixe peut être vide '' pour désactiver cette fonctionnalité")
    print("✓ Si le champ 'prefix' n'existe pas, le comportement par défaut est '' (vide)")
    
    print("\n" + "="*70)
    if failed == 0:
        print("🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS ! 🎉")
    else:
        print(f"⚠️  {failed} TEST(S) ONT ÉCHOUÉ")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
