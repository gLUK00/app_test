#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour l'API des fonctions JavaScript des plugins.
Teste les routes API GET /api/actions/javascript.
"""

import sys
import os
import json

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


def test_get_all_javascript():
    """Teste la route GET /api/actions/javascript."""
    print("=" * 80)
    print("TEST 1: GET /api/actions/javascript")
    print("=" * 80)
    
    with app.test_client() as client:
        response = client.get('/api/actions/javascript')
        
        assert response.status_code == 200, f"Status code doit être 200, reçu {response.status_code}"
        
        data = response.get_json()
        assert isinstance(data, dict), "La réponse doit être un dictionnaire"
        
        print(f"✅ Réponse reçue avec {len(data)} plugins ayant des fonctions JavaScript")
        
        # Vérifier que VarAction est présent
        assert 'var' in data, "Le plugin 'var' doit être présent"
        
        var_js = data['var']
        assert 'jsShowForm' in var_js, "VarAction doit avoir jsShowForm"
        assert 'jsValidateForm' in var_js, "VarAction doit avoir jsValidateForm"
        
        assert var_js['jsShowForm'] is not None, "jsShowForm ne doit pas être None"
        assert var_js['jsValidateForm'] is not None, "jsValidateForm ne doit pas être None"
        
        print("✅ Plugin VarAction contient jsShowForm et jsValidateForm")
        
        # Vérifier que les autres plugins ne sont pas présents (car ils retournent None)
        for plugin_name, plugin_js in data.items():
            if plugin_name != 'var':
                print(f"⚠️  Plugin inattendu avec JS: {plugin_name}")
        
        return data


def test_get_javascript_by_type():
    """Teste la route GET /api/actions/javascript/<action_type>."""
    print("\n" + "=" * 80)
    print("TEST 2: GET /api/actions/javascript/var")
    print("=" * 80)
    
    with app.test_client() as client:
        response = client.get('/api/actions/javascript/var')
        
        assert response.status_code == 200, f"Status code doit être 200, reçu {response.status_code}"
        
        data = response.get_json()
        assert isinstance(data, dict), "La réponse doit être un dictionnaire"
        
        assert 'type' in data, "La réponse doit contenir le type"
        assert data['type'] == 'var', "Le type doit être 'var'"
        
        assert 'jsShowForm' in data, "La réponse doit contenir jsShowForm"
        assert 'jsValidateForm' in data, "La réponse doit contenir jsValidateForm"
        
        assert isinstance(data['jsShowForm'], str), "jsShowForm doit être une string"
        assert isinstance(data['jsValidateForm'], str), "jsValidateForm doit être une string"
        
        print("✅ Réponse correcte pour le plugin 'var'")
        print(f"   - jsShowForm: {len(data['jsShowForm'])} caractères")
        print(f"   - jsValidateForm: {len(data['jsValidateForm'])} caractères")
        
        return data


def test_get_javascript_invalid_type():
    """Teste la route GET /api/actions/javascript/<action_type> avec un type invalide."""
    print("\n" + "=" * 80)
    print("TEST 3: GET /api/actions/javascript/invalid_type")
    print("=" * 80)
    
    with app.test_client() as client:
        response = client.get('/api/actions/javascript/invalid_type')
        
        assert response.status_code == 400, f"Status code doit être 400, reçu {response.status_code}"
        
        data = response.get_json()
        assert 'message' in data, "La réponse d'erreur doit contenir un message"
        
        print("✅ Erreur 400 retournée pour un type d'action invalide")
        print(f"   Message: {data['message']}")


def test_javascript_content_validity():
    """Teste que le contenu JavaScript est valide."""
    print("\n" + "=" * 80)
    print("TEST 4: Validation du contenu JavaScript")
    print("=" * 80)
    
    with app.test_client() as client:
        response = client.get('/api/actions/javascript/var')
        data = response.get_json()
        
        js_show_form = data['jsShowForm']
        js_validate_form = data['jsValidateForm']
        
        # Vérifier la présence de mots-clés JavaScript
        assert 'function jsShowForm' in js_show_form, "jsShowForm doit contenir la définition de fonction"
        assert 'function jsValidateForm' in js_validate_form, "jsValidateForm doit contenir la définition de fonction"
        
        # Vérifier le contenu spécifique à VarAction
        assert 'variable_name' in js_show_form, "jsShowForm doit référencer variable_name"
        assert 'isValid' in js_validate_form, "jsValidateForm doit retourner isValid"
        assert 'errorMessage' in js_validate_form, "jsValidateForm doit retourner errorMessage"
        
        print("✅ Le contenu JavaScript est valide")
        
        # Afficher un extrait
        print("\nExtrait de jsShowForm:")
        print("-" * 40)
        lines = js_show_form.split('\n')[:5]
        for line in lines:
            print(line)
        
        print("\nExtrait de jsValidateForm:")
        print("-" * 40)
        lines = js_validate_form.split('\n')[:5]
        for line in lines:
            print(line)


def main():
    """Exécute tous les tests."""
    print("\n🧪 TESTS DE L'API DES FONCTIONS JAVASCRIPT")
    print("=" * 80)
    
    try:
        test_get_all_javascript()
        test_get_javascript_by_type()
        test_get_javascript_invalid_type()
        test_javascript_content_validity()
        
        print("\n" + "=" * 80)
        print("✅ TOUS LES TESTS DE L'API SONT PASSÉS AVEC SUCCÈS")
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
