#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script de test pour le système de gestion des répertoires de travail des campagnes."""
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.workdir import (
    get_workdir,
    ensure_workdir_exists,
    create_campain_workdir,
    delete_campain_workdir,
    get_campain_workdir
)

def test_workdir_management():
    """Test du système de gestion des répertoires de travail."""
    print("\n" + "="*70)
    print("TEST: Système de gestion des répertoires de travail")
    print("="*70 + "\n")
    
    # Test 1: Récupération du chemin workdir
    print("1. Test de récupération du chemin workdir...")
    workdir = get_workdir()
    print(f"   ✓ Workdir configuré: {workdir}")
    
    # Test 2: Initialisation du workdir
    print("\n2. Test d'initialisation du workdir...")
    ensure_workdir_exists()
    workdir_path = Path(workdir)
    assert workdir_path.exists(), "Le workdir devrait exister"
    print(f"   ✓ Workdir initialisé: {workdir_path.absolute()}")
    
    # Test 3: Création d'un répertoire de campagne
    print("\n3. Test de création d'un répertoire de campagne...")
    test_campain_id = "test_campain_123"
    campain_dir = create_campain_workdir(test_campain_id)
    campain_path = Path(campain_dir)
    assert campain_path.exists(), "Le répertoire de campagne devrait exister"
    print(f"   ✓ Répertoire créé: {campain_dir}")
    
    # Test 4: Récupération du chemin d'un répertoire de campagne
    print("\n4. Test de récupération du chemin d'une campagne...")
    retrieved_dir = get_campain_workdir(test_campain_id)
    assert retrieved_dir == campain_dir, "Les chemins devraient correspondre"
    print(f"   ✓ Chemin récupéré: {retrieved_dir}")
    
    # Test 5: Création d'un fichier dans le répertoire de campagne
    print("\n5. Test de création d'un fichier dans le répertoire...")
    test_file = campain_path / "test.txt"
    test_file.write_text("Test content")
    assert test_file.exists(), "Le fichier de test devrait exister"
    print(f"   ✓ Fichier créé: {test_file}")
    
    # Test 6: Suppression du répertoire de campagne
    print("\n6. Test de suppression du répertoire de campagne...")
    success = delete_campain_workdir(test_campain_id)
    assert success, "La suppression devrait réussir"
    assert not campain_path.exists(), "Le répertoire ne devrait plus exister"
    print(f"   ✓ Répertoire supprimé")
    
    # Test 7: Création de plusieurs répertoires orphelins et nettoyage
    print("\n7. Test de nettoyage des répertoires orphelins...")
    orphan_ids = ["orphan_1", "orphan_2", "orphan_3"]
    for orphan_id in orphan_ids:
        orphan_path = Path(workdir) / orphan_id
        orphan_path.mkdir(parents=True, exist_ok=True)
        print(f"   - Répertoire orphelin créé: {orphan_id}")
    
    print("\n   Nettoyage des orphelins...")
    ensure_workdir_exists()
    
    # Vérifier que les orphelins ont été supprimés
    for orphan_id in orphan_ids:
        orphan_path = Path(workdir) / orphan_id
        assert not orphan_path.exists(), f"L'orphelin {orphan_id} devrait être supprimé"
    print(f"   ✓ Tous les orphelins ont été supprimés")
    
    print("\n" + "="*70)
    print("✓ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS")
    print("="*70 + "\n")

if __name__ == '__main__':
    try:
        test_workdir_management()
    except AssertionError as e:
        print(f"\n✗ ÉCHEC DU TEST: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERREUR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
