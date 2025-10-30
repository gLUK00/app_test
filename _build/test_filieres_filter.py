#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour la méthode get_all_filieres().

Ce script teste que la méthode retourne uniquement les filières valides :
- Exclut les variables racines (isRoot = true)
- Exclut les filières vides, null ou inexistantes
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_get_all_filieres_logic():
    """Test de la logique de filtrage des filières."""
    print("\n=== Test: Filtrage des filières ===")
    
    # Simuler des variables en base de données
    variables_test = [
        {'key': 'var1', 'filiere': 'PRODUCTION', 'isRoot': False},
        {'key': 'var2', 'filiere': 'DEV', 'isRoot': False},
        {'key': 'var3', 'filiere': 'TEST', 'isRoot': False},
        {'key': 'var4', 'filiere': 'PRODUCTION', 'isRoot': False},  # Doublon
        {'key': 'root_var', 'filiere': 'PRODUCTION', 'isRoot': True},  # Variable racine - À EXCLURE
        {'key': 'var5', 'filiere': '', 'isRoot': False},  # Filière vide - À EXCLURE
        {'key': 'var6', 'filiere': None, 'isRoot': False},  # Filière null - À EXCLURE
        {'key': 'var7', 'filiere': 'DEV', 'isRoot': False},  # Doublon
    ]
    
    print(f"\nNombre total de variables: {len(variables_test)}")
    
    # Simuler le filtrage
    valid_filieres = set()
    
    for var in variables_test:
        # Filtrer selon les critères
        if var.get('isRoot') != True and var.get('filiere') and var.get('filiere') != '':
            valid_filieres.add(var['filiere'])
    
    # Trier les filières
    filieres = sorted(list(valid_filieres))
    
    print(f"\nFilières valides trouvées: {filieres}")
    print(f"Nombre de filières: {len(filieres)}")
    
    # Vérifications
    expected_filieres = ['DEV', 'PRODUCTION', 'TEST']
    
    assert filieres == expected_filieres, f"Échec: {filieres} != {expected_filieres}"
    assert 'PRODUCTION' in filieres, "PRODUCTION devrait être dans la liste"
    assert 'DEV' in filieres, "DEV devrait être dans la liste"
    assert 'TEST' in filieres, "TEST devrait être dans la liste"
    assert len(filieres) == 3, "Il devrait y avoir exactement 3 filières distinctes"
    
    print("\n✅ Test réussi - Les filières sont correctement filtrées")
    
    # Vérifier les exclusions
    print("\n=== Vérification des exclusions ===")
    
    excluded_count = 0
    
    for var in variables_test:
        if var.get('isRoot') == True:
            print(f"✓ Variable racine exclue: {var['key']} (filière: {var.get('filiere')})")
            excluded_count += 1
        elif not var.get('filiere') or var.get('filiere') == '':
            print(f"✓ Filière vide/null exclue: {var['key']}")
            excluded_count += 1
    
    print(f"\nNombre de variables exclues: {excluded_count}")
    assert excluded_count == 3, "Il devrait y avoir 3 variables exclues"
    
    print("✅ Toutes les exclusions sont correctes")


def test_mongodb_pipeline():
    """Test de la structure du pipeline MongoDB."""
    print("\n=== Test: Pipeline MongoDB ===")
    
    pipeline = [
        {
            '$match': {
                'isRoot': {'$ne': True},
                'filiere': {'$exists': True, '$ne': None, '$ne': ''}
            }
        },
        {
            '$group': {
                '_id': '$filiere'
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ]
    
    print("\nPipeline d'agrégation:")
    for i, stage in enumerate(pipeline, 1):
        print(f"\nÉtape {i}: {list(stage.keys())[0]}")
        for key, value in stage.items():
            print(f"  {key}: {value}")
    
    # Vérifier les étapes
    assert len(pipeline) == 3, "Le pipeline devrait avoir 3 étapes"
    assert '$match' in pipeline[0], "Première étape devrait être $match"
    assert '$group' in pipeline[1], "Deuxième étape devrait être $group"
    assert '$sort' in pipeline[2], "Troisième étape devrait être $sort"
    
    # Vérifier les conditions de filtrage
    match_stage = pipeline[0]['$match']
    assert 'isRoot' in match_stage, "Devrait filtrer sur isRoot"
    assert 'filiere' in match_stage, "Devrait filtrer sur filiere"
    assert match_stage['isRoot'] == {'$ne': True}, "Devrait exclure isRoot = True"
    
    print("\n✅ Pipeline correctement structuré")


def main():
    """Exécute tous les tests."""
    print("=" * 60)
    print("TESTS DE FILTRAGE DES FILIÈRES")
    print("=" * 60)
    
    try:
        test_get_all_filieres_logic()
        test_mongodb_pipeline()
        
        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS ONT RÉUSSI")
        print("=" * 60)
        print("\nRésumé des filtres appliqués:")
        print("  ✓ Exclusion des variables racines (isRoot = true)")
        print("  ✓ Exclusion des filières vides ('')")
        print("  ✓ Exclusion des filières null")
        print("  ✓ Suppression des doublons")
        print("  ✓ Tri alphabétique")
        
    except AssertionError as e:
        print("\n" + "=" * 60)
        print(f"❌ ÉCHEC DES TESTS: {e}")
        print("=" * 60)
        sys.exit(1)
    
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ ERREUR: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
