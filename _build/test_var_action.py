#!/usr/bin/env python3
"""
Script de test pour le plugin VarAction
Teste la conversion de variables en différents types
"""

import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.actions.var_action import VarAction
import json


def test_var_action_metadata():
    """Test des métadonnées du plugin."""
    print("\n=== Test des métadonnées ===")
    action = VarAction()
    metadata = action.get_metadata()
    
    assert metadata['name'] == 'var', "Le nom du plugin doit être 'var'"
    assert metadata['version'] == '1.0.0', "La version doit être '1.0.0'"
    assert action.label == 'Variables (Conversion)', "Le label doit être 'Variables (Conversion)'"
    
    print("✅ Métadonnées correctes")
    print(f"   Nom: {metadata['name']}")
    print(f"   Label: {action.label}")
    print(f"   Version: {metadata['version']}")
    print(f"   Auteur: {metadata['author']}")


def test_input_mask():
    """Test du masque de saisie."""
    print("\n=== Test du masque de saisie ===")
    action = VarAction()
    mask = action.get_input_mask()
    
    assert len(mask) == 2, "Le masque doit contenir 2 champs"
    
    # Vérifier le champ variable_name
    var_field = next((f for f in mask if f['name'] == 'variable_name'), None)
    assert var_field is not None, "Le champ 'variable_name' doit exister"
    assert var_field['type'] == 'select-var-test', "Le type doit être 'select-var-test'"
    assert var_field['required'] is True, "Le champ doit être requis"
    
    # Vérifier le champ target_type
    type_field = next((f for f in mask if f['name'] == 'target_type'), None)
    assert type_field is not None, "Le champ 'target_type' doit exister"
    assert type_field['type'] == 'select', "Le type doit être 'select'"
    assert len(type_field['options']) == 6, "Doit avoir 6 options de types"
    
    print("✅ Masque de saisie correct")
    print(f"   Champ 1: {var_field['name']} (type: {var_field['type']})")
    print(f"   Champ 2: {type_field['name']} avec {len(type_field['options'])} options")


def test_output_variables():
    """Test des variables de sortie."""
    print("\n=== Test des variables de sortie ===")
    action = VarAction()
    output_vars = action.get_output_variables()
    
    assert len(output_vars) == 1, "Doit retourner 1 variable de sortie"
    assert 'converted_value' in output_vars, "La variable 'converted_value' doit exister"
    
    print("✅ Variables de sortie correctes")
    print(f"   Variables: {', '.join(output_vars)}")


def test_validation():
    """Test de la validation de configuration."""
    print("\n=== Test de la validation ===")
    action = VarAction()
    
    # Config valide
    valid_config = {
        'variable_name': 'my_var',
        'target_type': 'int'
    }
    is_valid, message = action.validate_config(valid_config)
    assert is_valid, "La configuration valide doit être acceptée"
    print("✅ Configuration valide acceptée")
    
    # Config sans variable_name
    invalid_config = {
        'target_type': 'int'
    }
    is_valid, message = action.validate_config(invalid_config)
    assert not is_valid, "La configuration sans variable_name doit être rejetée"
    assert 'variable_name' in message, "Le message doit mentionner le champ manquant"
    print("✅ Configuration sans variable_name rejetée")
    
    # Config avec type invalide
    invalid_type = {
        'variable_name': 'my_var',
        'target_type': 'invalid_type'
    }
    is_valid, message = action.validate_config(invalid_type)
    assert not is_valid, "La configuration avec type invalide doit être rejetée"
    assert 'invalide' in message.lower(), "Le message doit indiquer le type invalide"
    print("✅ Configuration avec type invalide rejetée")


def test_conversion_to_int():
    """Test de conversion vers int."""
    print("\n=== Test de conversion vers int ===")
    action = VarAction()
    
    # String vers int
    context = {
        'variable_name': 'my_var',
        'target_type': 'int',
        'variables': {'my_var': '42'}
    }
    code, logs, output = action.execute(context)
    assert code == 0, "La conversion doit réussir"
    assert output['converted_value'] == 42, "La valeur doit être 42"
    print(f"✅ String '42' → int 42")
    
    # Float vers int
    context['variables']['my_var'] = 3.14
    code, logs, output = action.execute(context)
    assert code == 0, "La conversion doit réussir"
    assert output['converted_value'] == 3, "La valeur doit être 3"
    print(f"✅ Float 3.14 → int 3")


def test_conversion_to_float():
    """Test de conversion vers float."""
    print("\n=== Test de conversion vers float ===")
    action = VarAction()
    
    # String vers float
    context = {
        'variable_name': 'my_var',
        'target_type': 'float',
        'variables': {'my_var': '3.14'}
    }
    code, logs, output = action.execute(context)
    assert code == 0, "La conversion doit réussir"
    assert output['converted_value'] == 3.14, "La valeur doit être 3.14"
    print(f"✅ String '3.14' → float 3.14")
    
    # Int vers float
    context['variables']['my_var'] = 42
    code, logs, output = action.execute(context)
    assert code == 0, "La conversion doit réussir"
    assert output['converted_value'] == 42.0, "La valeur doit être 42.0"
    print(f"✅ Int 42 → float 42.0")


def test_conversion_to_bool():
    """Test de conversion vers bool."""
    print("\n=== Test de conversion vers bool ===")
    action = VarAction()
    
    # String 'true' vers bool
    test_cases = [
        ('true', True, "String 'true' → bool True"),
        ('false', False, "String 'false' → bool False"),
        ('1', True, "String '1' → bool True"),
        ('0', False, "String '0' → bool False"),
        ('yes', True, "String 'yes' → bool True"),
        ('no', False, "String 'no' → bool False"),
        (1, True, "Int 1 → bool True"),
        (0, False, "Int 0 → bool False"),
    ]
    
    for value, expected, description in test_cases:
        context = {
            'variable_name': 'my_var',
            'target_type': 'bool',
            'variables': {'my_var': value}
        }
        code, logs, output = action.execute(context)
        assert code == 0, f"La conversion doit réussir pour {value}"
        assert output['converted_value'] == expected, f"La valeur doit être {expected} pour {value}"
        print(f"✅ {description}")


def test_conversion_to_list():
    """Test de conversion vers list."""
    print("\n=== Test de conversion vers list ===")
    action = VarAction()
    
    # String JSON vers list
    context = {
        'variable_name': 'my_var',
        'target_type': 'list',
        'variables': {'my_var': '[1, 2, 3]'}
    }
    code, logs, output = action.execute(context)
    assert code == 0, "La conversion doit réussir"
    assert output['converted_value'] == [1, 2, 3], "La valeur doit être [1, 2, 3]"
    print(f"✅ String '[1, 2, 3]' → list [1, 2, 3]")
    
    # String simple vers list
    context['variables']['my_var'] = 'hello'
    code, logs, output = action.execute(context)
    assert code == 0, "La conversion doit réussir"
    assert output['converted_value'] == ['hello'], "La valeur doit être ['hello']"
    print(f"✅ String 'hello' → list ['hello']")
    
    # Tuple vers list
    context['variables']['my_var'] = (1, 2, 3)
    code, logs, output = action.execute(context)
    assert code == 0, "La conversion doit réussir"
    assert output['converted_value'] == [1, 2, 3], "La valeur doit être [1, 2, 3]"
    print(f"✅ Tuple (1, 2, 3) → list [1, 2, 3]")


def test_conversion_to_dict():
    """Test de conversion vers dict."""
    print("\n=== Test de conversion vers dict ===")
    action = VarAction()
    
    # String JSON vers dict
    context = {
        'variable_name': 'my_var',
        'target_type': 'dict',
        'variables': {'my_var': '{"key": "value", "number": 42}'}
    }
    code, logs, output = action.execute(context)
    assert code == 0, "La conversion doit réussir"
    assert output['converted_value'] == {"key": "value", "number": 42}, "Le dictionnaire doit être correct"
    print(f"✅ String JSON → dict {output['converted_value']}")
    
    # Dict existant
    context['variables']['my_var'] = {"name": "test"}
    code, logs, output = action.execute(context)
    assert code == 0, "La conversion doit réussir"
    assert output['converted_value'] == {"name": "test"}, "Le dictionnaire doit rester inchangé"
    print(f"✅ Dict → dict (inchangé)")


def test_conversion_to_json():
    """Test de conversion vers JSON string."""
    print("\n=== Test de conversion vers JSON ===")
    action = VarAction()
    
    # Dict vers JSON string
    context = {
        'variable_name': 'my_var',
        'target_type': 'json',
        'variables': {'my_var': {"key": "value", "number": 42}}
    }
    code, logs, output = action.execute(context)
    assert code == 0, "La conversion doit réussir"
    parsed = json.loads(output['converted_value'])
    assert parsed == {"key": "value", "number": 42}, "Le JSON doit être correct"
    print(f"✅ Dict → JSON string")
    
    # List vers JSON string
    context['variables']['my_var'] = [1, 2, 3]
    code, logs, output = action.execute(context)
    assert code == 0, "La conversion doit réussir"
    parsed = json.loads(output['converted_value'])
    assert parsed == [1, 2, 3], "Le JSON doit être correct"
    print(f"✅ List → JSON string")


def test_error_cases():
    """Test des cas d'erreur."""
    print("\n=== Test des cas d'erreur ===")
    action = VarAction()
    
    # Variable inexistante
    context = {
        'variable_name': 'inexistant',
        'target_type': 'int',
        'variables': {'my_var': '42'}
    }
    code, logs, output = action.execute(context)
    assert code == 1, "Doit échouer avec une variable inexistante"
    assert 'introuvable' in logs.lower(), "Le message doit indiquer que la variable est introuvable"
    print(f"✅ Variable inexistante → erreur")
    
    # Conversion impossible
    context = {
        'variable_name': 'my_var',
        'target_type': 'int',
        'variables': {'my_var': 'not_a_number'}
    }
    code, logs, output = action.execute(context)
    assert code == 1, "Doit échouer avec une conversion impossible"
    print(f"✅ Conversion impossible → erreur")


def run_all_tests():
    """Exécute tous les tests."""
    print("=" * 60)
    print("TESTS DU PLUGIN VAR ACTION")
    print("=" * 60)
    
    try:
        test_var_action_metadata()
        test_input_mask()
        test_output_variables()
        test_validation()
        test_conversion_to_int()
        test_conversion_to_float()
        test_conversion_to_bool()
        test_conversion_to_list()
        test_conversion_to_dict()
        test_conversion_to_json()
        test_error_cases()
        
        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS SONT PASSÉS")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n❌ ÉCHEC DU TEST : {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE : {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
