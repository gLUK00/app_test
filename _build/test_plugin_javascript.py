#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour les fonctions JavaScript des plugins d'actions.
Vérifie que les plugins peuvent définir et exposer des fonctions JavaScript.
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.actions import get_action, get_all_actions


def test_action_base_js_methods():
    """Teste que la classe de base ActionBase expose les méthodes JavaScript."""
    print("=" * 80)
    print("TEST 1: Vérification des méthodes JavaScript dans ActionBase")
    print("=" * 80)
    
    # Récupérer une action quelconque
    action = get_action('var')
    
    assert hasattr(action, 'get_js_show_form'), "La méthode get_js_show_form doit exister"
    assert hasattr(action, 'get_js_validate_form'), "La méthode get_js_validate_form doit exister"
    
    print("✅ Les méthodes get_js_show_form et get_js_validate_form existent dans ActionBase")


def test_var_action_js_functions():
    """Teste que VarAction définit bien les fonctions JavaScript."""
    print("\n" + "=" * 80)
    print("TEST 2: Vérification des fonctions JavaScript dans VarAction")
    print("=" * 80)
    
    action = get_action('var')
    
    js_show_form = action.get_js_show_form()
    js_validate_form = action.get_js_validate_form()
    
    assert js_show_form is not None, "VarAction doit définir jsShowForm"
    assert js_validate_form is not None, "VarAction doit définir jsValidateForm"
    
    assert isinstance(js_show_form, str), "jsShowForm doit être une string"
    assert isinstance(js_validate_form, str), "jsValidateForm doit être une string"
    
    assert 'function jsShowForm' in js_show_form, "jsShowForm doit contenir la définition de la fonction"
    assert 'function jsValidateForm' in js_validate_form, "jsValidateForm doit contenir la définition de la fonction"
    
    print("✅ VarAction définit correctement jsShowForm et jsValidateForm")
    print(f"   - jsShowForm: {len(js_show_form)} caractères")
    print(f"   - jsValidateForm: {len(js_validate_form)} caractères")


def test_default_js_functions():
    """Teste que les plugins sans fonctions JavaScript retournent None."""
    print("\n" + "=" * 80)
    print("TEST 3: Vérification du comportement par défaut (None)")
    print("=" * 80)
    
    # Tester avec IoAction qui ne définit pas de fonctions JavaScript
    action = get_action('io')
    
    if action:
        js_show_form = action.get_js_show_form()
        js_validate_form = action.get_js_validate_form()
        
        assert js_show_form is None, "Par défaut, get_js_show_form doit retourner None"
        assert js_validate_form is None, "Par défaut, get_js_validate_form doit retourner None"
        
        print("✅ Les plugins sans fonctions JavaScript retournent None par défaut")
    else:
        print("⚠️  Plugin IoAction non trouvé, test ignoré")


def test_all_actions_js_compatibility():
    """Teste que tous les plugins d'actions sont compatibles avec les fonctions JavaScript."""
    print("\n" + "=" * 80)
    print("TEST 4: Compatibilité de tous les plugins d'actions")
    print("=" * 80)
    
    actions = get_all_actions()
    print(f"Nombre total de plugins d'actions: {len(actions)}")
    
    for action_type, action_info in actions.items():
        action = get_action(action_type)
        
        try:
            js_show_form = action.get_js_show_form()
            js_validate_form = action.get_js_validate_form()
            
            # Vérifier que les valeurs retournées sont soit None, soit des strings
            if js_show_form is not None:
                assert isinstance(js_show_form, str), f"{action_type}: jsShowForm doit être une string ou None"
            
            if js_validate_form is not None:
                assert isinstance(js_validate_form, str), f"{action_type}: jsValidateForm doit être une string ou None"
            
            has_js = js_show_form is not None or js_validate_form is not None
            status = "📜 JS" if has_js else "⚪ Standard"
            print(f"   {status} {action_type}")
            
        except Exception as e:
            print(f"   ❌ ERREUR avec {action_type}: {str(e)}")
            raise
    
    print("✅ Tous les plugins d'actions sont compatibles avec les fonctions JavaScript")


def test_js_function_content():
    """Teste le contenu des fonctions JavaScript de VarAction."""
    print("\n" + "=" * 80)
    print("TEST 5: Contenu des fonctions JavaScript de VarAction")
    print("=" * 80)
    
    action = get_action('var')
    
    js_show_form = action.get_js_show_form()
    js_validate_form = action.get_js_validate_form()
    
    # Vérifier que jsShowForm contient les éléments attendus
    assert 'variable_name' in js_show_form, "jsShowForm doit référencer le champ variable_name"
    assert 'addEventListener' in js_show_form, "jsShowForm doit ajouter des écouteurs d'événements"
    assert 'is-valid' in js_show_form or 'is-invalid' in js_show_form, "jsShowForm doit utiliser les classes Bootstrap"
    
    print("✅ jsShowForm contient les éléments attendus")
    
    # Vérifier que jsValidateForm contient les éléments attendus
    assert 'isValid' in js_validate_form, "jsValidateForm doit retourner isValid"
    assert 'errorMessage' in js_validate_form, "jsValidateForm doit retourner errorMessage"
    assert 'variables' in js_validate_form, "jsValidateForm doit utiliser le paramètre variables"
    
    print("✅ jsValidateForm contient les éléments attendus")
    
    # Afficher un extrait des fonctions
    print("\nExtrait de jsShowForm:")
    print("-" * 40)
    print(js_show_form[:200] + "...")
    
    print("\nExtrait de jsValidateForm:")
    print("-" * 40)
    print(js_validate_form[:200] + "...")


def main():
    """Exécute tous les tests."""
    print("\n🧪 TESTS DES FONCTIONS JAVASCRIPT DES PLUGINS D'ACTIONS")
    print("=" * 80)
    
    try:
        test_action_base_js_methods()
        test_var_action_js_functions()
        test_default_js_functions()
        test_all_actions_js_compatibility()
        test_js_function_content()
        
        print("\n" + "=" * 80)
        print("✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS")
        print("=" * 80)
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ ÉCHEC DU TEST: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
