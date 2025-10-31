#!/usr/bin/env python3
"""Script de test pour vérifier le remplacement des variables dans les chaînes complexes."""

import re

def resolve_variables_test(value, variables_dict, test_variables):
    """
    Fonction de test identique à celle du CampainExecutor.
    """
    if isinstance(value, str):
        # Remplacer les variables TestGyver {{variable_name}}
        def replace_testgyver(match):
            var_name = match.group(1)
            return str(variables_dict.get(var_name, match.group(0)))
        
        # Remplacer les variables de test {{app.variable_name}}
        def replace_test(match):
            var_name = match.group(1)
            return str(test_variables.get(var_name, match.group(0)))
        
        # Remplacer les variables de collection {{test.variable_name}}
        def replace_collection(match):
            var_name = match.group(1)
            full_key = f"test.{match.group(1)}"
            return str(variables_dict.get(full_key, match.group(0)))
        
        value = re.sub(r'\{\{([^.}]+)\}\}', replace_testgyver, value)
        value = re.sub(r'\{\{app\.([^}]+)\}\}', replace_test, value)
        value = re.sub(r'\{\{test\.([^}]+)\}\}', replace_collection, value)
        
        return value
    
    return value

# Préparer les données de test
print("=" * 70)
print("Test de remplacement des variables dans des chaînes complexes")
print("=" * 70)

# Variables de test
variables_dict = {
    'url_base': 'https://exemple.com',
    'port': '8080',
    'test.test_id': '34843848343',
    'test.campain_id': 'camp_12345'
}

test_variables = {
    'user_token': 'abc123xyz',
    'session_id': 'sess_999'
}

# Cas de test
test_cases = [
    # Cas 1: Variable seule
    {
        'input': '{{test.test_id}}',
        'expected': '34843848343',
        'description': 'Variable de collection seule'
    },
    # Cas 2: Variable avec suffixe
    {
        'input': '{{test.test_id}}/image',
        'expected': '34843848343/image',
        'description': 'Variable de collection avec suffixe'
    },
    # Cas 3: Variable entourée de texte
    {
        'input': 'dossier_A/{{test.test_id}}/dossier_B/dossier_C',
        'expected': 'dossier_A/34843848343/dossier_B/dossier_C',
        'description': 'Variable de collection entourée de texte'
    },
    # Cas 4: Plusieurs variables
    {
        'input': '{{url_base}}:{{port}}/api/test/{{test.test_id}}',
        'expected': 'https://exemple.com:8080/api/test/34843848343',
        'description': 'Plusieurs variables de types différents'
    },
    # Cas 5: Variables TestGyver et app
    {
        'input': '{{url_base}}/user/{{app.user_token}}/session',
        'expected': 'https://exemple.com/user/abc123xyz/session',
        'description': 'Variables TestGyver et app mélangées'
    },
    # Cas 6: Toutes les variables ensemble
    {
        'input': '{{url_base}}/test/{{test.test_id}}/user/{{app.user_token}}/data',
        'expected': 'https://exemple.com/test/34843848343/user/abc123xyz/data',
        'description': 'Tous les types de variables'
    },
    # Cas 7: Variable au début
    {
        'input': '{{test.campain_id}}/reports/latest.pdf',
        'expected': 'camp_12345/reports/latest.pdf',
        'description': 'Variable au début de la chaîne'
    },
    # Cas 8: Variable au milieu
    {
        'input': 'uploads/{{test.test_id}}/files/document.txt',
        'expected': 'uploads/34843848343/files/document.txt',
        'description': 'Variable au milieu de la chaîne'
    },
    # Cas 9: Variable non trouvée (doit rester inchangée)
    {
        'input': '{{test.unknown_var}}/path',
        'expected': '{{test.unknown_var}}/path',
        'description': 'Variable inexistante (doit rester inchangée)'
    },
    # Cas 10: URL complète
    {
        'input': '{{url_base}}:{{port}}/api/v1/campain/{{test.campain_id}}/test/{{test.test_id}}/execute',
        'expected': 'https://exemple.com:8080/api/v1/campain/camp_12345/test/34843848343/execute',
        'description': 'URL complète avec multiples variables'
    }
]

# Exécuter les tests
print("\nExécution des tests:\n")
all_passed = True

for i, test_case in enumerate(test_cases, 1):
    input_value = test_case['input']
    expected = test_case['expected']
    description = test_case['description']
    
    result = resolve_variables_test(input_value, variables_dict, test_variables)
    
    passed = result == expected
    all_passed = all_passed and passed
    
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"Test #{i}: {status}")
    print(f"  Description: {description}")
    print(f"  Entrée:      {input_value}")
    print(f"  Résultat:    {result}")
    print(f"  Attendu:     {expected}")
    
    if not passed:
        print(f"  ⚠️  DIFFÉRENCE DÉTECTÉE!")
    print()

print("=" * 70)
if all_passed:
    print("✅ TOUS LES TESTS ONT RÉUSSI!")
else:
    print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
print("=" * 70)
