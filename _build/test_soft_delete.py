#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour la fonctionnalité de suppression logique (soft delete).
Ce script teste les modèles Test, Campain et Rapport avec la suppression logique activée.
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.test import Test
from models.campain import Campain
from models.rapport import Rapport
from models.user import User
from utils.db import is_soft_delete_enabled

def test_soft_delete_config():
    """Teste que la configuration soft_delete est activée."""
    print("\n📋 Test 1: Vérification de la configuration soft_delete")
    
    is_enabled = is_soft_delete_enabled()
    print(f"  ℹ️  Suppression logique activée: {is_enabled}")
    
    if is_enabled:
        print("  ✅ La suppression logique est activée")
        return True
    else:
        print("  ⚠️  La suppression logique est désactivée")
        return False

def test_campain_soft_delete():
    """Teste la suppression logique d'une campagne."""
    print("\n📋 Test 2: Suppression logique d'une campagne")
    
    try:
        # Créer un utilisateur de test
        users = User.get_all()
        if not users:
            print("  ⚠️  Aucun utilisateur disponible pour le test")
            return False
        
        user_id = users[0]['_id']
        
        # Créer une campagne de test
        campain_id = Campain.create(
            user_created=user_id,
            name=f"Test Soft Delete {datetime.now().strftime('%Y%m%d%H%M%S')}",
            description="Campagne de test pour la suppression logique"
        )
        print(f"  ✅ Campagne créée: {campain_id}")
        
        # Vérifier que la campagne est active
        campain = Campain.find_by_id(campain_id)
        if not campain:
            print("  ❌ Campagne non trouvée après création")
            return False
        
        # Supprimer la campagne
        deleted = Campain.delete(campain_id)
        print(f"  ✅ Campagne supprimée (soft delete): {deleted}")
        
        # Vérifier que la campagne n'apparaît plus dans get_all
        all_campains = Campain.get_all()
        campain_in_list = any(c['_id'] == campain_id for c in all_campains)
        
        if campain_in_list:
            print("  ❌ La campagne supprimée apparaît encore dans get_all()")
            return False
        else:
            print("  ✅ La campagne supprimée n'apparaît plus dans get_all()")
        
        # Vérifier que la campagne est dans les éléments supprimés
        deleted_campains = Campain.get_deleted()
        campain_in_deleted = any(c['_id'] == campain_id for c in deleted_campains)
        
        if campain_in_deleted:
            print("  ✅ La campagne apparaît dans get_deleted()")
        else:
            print("  ❌ La campagne n'apparaît pas dans get_deleted()")
            return False
        
        # Restaurer la campagne
        restored = Campain.restore(campain_id)
        print(f"  ✅ Campagne restaurée: {restored}")
        
        # Vérifier que la campagne est de nouveau active
        all_campains = Campain.get_all()
        campain_in_list = any(c['_id'] == campain_id for c in all_campains)
        
        if campain_in_list:
            print("  ✅ La campagne restaurée apparaît dans get_all()")
        else:
            print("  ❌ La campagne restaurée n'apparaît pas dans get_all()")
            return False
        
        # Supprimer définitivement
        Campain.delete(campain_id)  # Soft delete d'abord
        permanent_deleted = Campain.permanent_delete(campain_id)
        print(f"  ✅ Campagne supprimée définitivement: {permanent_deleted}")
        
        # Vérifier que la campagne a été supprimée définitivement
        deleted_campains = Campain.get_deleted()
        campain_in_deleted = any(c['_id'] == campain_id for c in deleted_campains)
        
        if not campain_in_deleted:
            print("  ✅ La campagne ne figure plus dans get_deleted() après suppression définitive")
        else:
            print("  ❌ La campagne est toujours dans get_deleted() après suppression définitive")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_test_soft_delete():
    """Teste la suppression logique d'un test."""
    print("\n📋 Test 3: Suppression logique d'un test")
    
    try:
        # Créer un utilisateur et une campagne de test
        users = User.get_all()
        if not users:
            print("  ⚠️  Aucun utilisateur disponible pour le test")
            return False
        
        user_id = users[0]['_id']
        
        campain_id = Campain.create(
            user_created=user_id,
            name=f"Campagne Test {datetime.now().strftime('%Y%m%d%H%M%S')}",
            description="Campagne pour tester la suppression de tests"
        )
        print(f"  ✅ Campagne créée: {campain_id}")
        
        # Créer un test
        test_id = Test.create(
            campain_id=campain_id,
            user_id=user_id,
            actions=[],
            name="Test de suppression logique",
            description="Test pour vérifier la suppression logique"
        )
        print(f"  ✅ Test créé: {test_id}")
        
        # Supprimer le test
        deleted = Test.delete(test_id)
        print(f"  ✅ Test supprimé (soft delete): {deleted}")
        
        # Vérifier que le test n'apparaît plus dans get_all
        all_tests = Test.get_all()
        test_in_list = any(t['_id'] == test_id for t in all_tests)
        
        if not test_in_list:
            print("  ✅ Le test supprimé n'apparaît plus dans get_all()")
        else:
            print("  ❌ Le test supprimé apparaît encore dans get_all()")
            return False
        
        # Vérifier que le test est dans les éléments supprimés
        deleted_tests = Test.get_deleted()
        test_in_deleted = any(t['_id'] == test_id for t in deleted_tests)
        
        if test_in_deleted:
            print("  ✅ Le test apparaît dans get_deleted()")
        else:
            print("  ❌ Le test n'apparaît pas dans get_deleted()")
            return False
        
        # Restaurer le test
        restored = Test.restore(test_id)
        print(f"  ✅ Test restauré: {restored}")
        
        # Nettoyer
        Test.permanent_delete(test_id)
        Campain.permanent_delete(campain_id)
        print("  ✅ Nettoyage effectué")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rapport_soft_delete():
    """Teste la suppression logique d'un rapport."""
    print("\n📋 Test 4: Suppression logique d'un rapport")
    
    try:
        # Créer un utilisateur et une campagne de test
        users = User.get_all()
        if not users:
            print("  ⚠️  Aucun utilisateur disponible pour le test")
            return False
        
        user_id = users[0]['_id']
        
        campain_id = Campain.create(
            user_created=user_id,
            name=f"Campagne Rapport {datetime.now().strftime('%Y%m%d%H%M%S')}",
            description="Campagne pour tester la suppression de rapports"
        )
        print(f"  ✅ Campagne créée: {campain_id}")
        
        # Créer un rapport
        rapport_id = Rapport.create(
            campain_id=campain_id,
            result="success",
            details="Rapport de test",
            filiere="test",
            tests=[]
        )
        print(f"  ✅ Rapport créé: {rapport_id}")
        
        # Supprimer le rapport
        deleted = Rapport.delete(rapport_id)
        print(f"  ✅ Rapport supprimé (soft delete): {deleted}")
        
        # Vérifier que le rapport n'apparaît plus dans get_all
        all_rapports = Rapport.get_all()
        rapport_in_list = any(r['_id'] == rapport_id for r in all_rapports)
        
        if not rapport_in_list:
            print("  ✅ Le rapport supprimé n'apparaît plus dans get_all()")
        else:
            print("  ❌ Le rapport supprimé apparaît encore dans get_all()")
            return False
        
        # Vérifier que le rapport est dans les éléments supprimés
        deleted_rapports = Rapport.get_deleted()
        rapport_in_deleted = any(r['_id'] == rapport_id for r in deleted_rapports)
        
        if rapport_in_deleted:
            print("  ✅ Le rapport apparaît dans get_deleted()")
        else:
            print("  ❌ Le rapport n'apparaît pas dans get_deleted()")
            return False
        
        # Restaurer le rapport
        restored = Rapport.restore(rapport_id)
        print(f"  ✅ Rapport restauré: {restored}")
        
        # Nettoyer
        Rapport.permanent_delete(rapport_id)
        Campain.permanent_delete(campain_id)
        print("  ✅ Nettoyage effectué")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n" + "="*80)
    print("TESTS UNITAIRES - SUPPRESSION LOGIQUE (SOFT DELETE)")
    print("="*80)
    
    results = []
    
    # Test 1: Configuration
    results.append(("Configuration soft_delete", test_soft_delete_config()))
    
    # Test 2: Campagnes
    results.append(("Suppression logique campagnes", test_campain_soft_delete()))
    
    # Test 3: Tests
    results.append(("Suppression logique tests", test_test_soft_delete()))
    
    # Test 4: Rapports
    results.append(("Suppression logique rapports", test_rapport_soft_delete()))
    
    # Résumé
    print("\n" + "="*80)
    print("RÉSUMÉ DES TESTS")
    print("="*80)
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed
    
    for name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{status}: {name}")
    
    print("\n" + "-"*80)
    print(f"Total: {total} tests | Réussis: {passed} | Échecs: {failed}")
    print("="*80 + "\n")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("✅ Tous les tests sont passés avec succès!\n")
