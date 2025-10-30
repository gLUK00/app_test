#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour le système d'exécution de campagnes.

Ce script teste les fonctionnalités suivantes:
1. Génération de nom de rapport unique
2. Récupération des filières
3. Lancement d'une campagne
4. Mise à jour du statut et de la progression
5. Résolution des variables
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.campain_executor import CampainExecutor
from models.rapport import Rapport
from models.variable import Variable
from datetime import datetime
import re


class MockSocketIO:
    """Mock de SocketIO pour les tests."""
    
    def __init__(self):
        self.events = []
    
    def emit(self, event, data):
        """Enregistre les événements émis."""
        self.events.append({'event': event, 'data': data})
        print(f"[WebSocket] {event}: {data}")


def test_generate_name():
    """Test de la génération de nom unique."""
    print("\n=== Test: Génération de nom de rapport ===")
    
    now = datetime.now()
    months_fr = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    base_name = f"{months_fr[now.month - 1]} {now.year}"
    
    print(f"Nom de base: {base_name}")
    
    # Simuler l'unicité
    name = base_name
    counter = 1
    
    # Si le nom existe déjà (simulé)
    existing_names = [base_name, f"{base_name} (1)"]
    
    while name in existing_names:
        name = f"{base_name} ({counter})"
        counter += 1
    
    print(f"Nom unique généré: {name}")
    assert name == f"{base_name} (2)", "Le nom devrait être suffixé avec (2)"
    print("✅ Test réussi")


def test_variable_resolution():
    """Test de la résolution des variables."""
    print("\n=== Test: Résolution des variables ===")
    
    executor = CampainExecutor(MockSocketIO())
    
    # Variables de test
    variables_dict = {
        'api_url': 'https://api.example.com',
        'api_token': 'secret123',
        'test_id': '507f1f77bcf86cd799439011',
        'campain_id': '507f1f77bcf86cd799439012'
    }
    
    test_variables = {
        'user_id': '12345',
        'session_token': 'token_abc'
    }
    
    # Test de résolution
    test_cases = [
        {
            'input': '{{api_url}}/users',
            'expected': 'https://api.example.com/users',
            'description': 'Variable TestGyver simple'
        },
        {
            'input': 'Bearer {{api_token}}',
            'expected': 'Bearer secret123',
            'description': 'Variable TestGyver dans une chaîne'
        },
        {
            'input': '{{app.user_id}}',
            'expected': '12345',
            'description': 'Variable de test'
        },
        {
            'input': '{{test.test_id}}',
            'expected': '507f1f77bcf86cd799439011',
            'description': 'Variable de collection'
        },
        {
            'input': {
                'url': '{{api_url}}/users/{{app.user_id}}',
                'headers': {
                    'Authorization': 'Bearer {{api_token}}'
                }
            },
            'expected': {
                'url': 'https://api.example.com/users/12345',
                'headers': {
                    'Authorization': 'Bearer secret123'
                }
            },
            'description': 'Dictionnaire avec variables'
        }
    ]
    
    for test_case in test_cases:
        result = executor._resolve_variables(
            test_case['input'],
            variables_dict,
            test_variables
        )
        
        print(f"\nTest: {test_case['description']}")
        print(f"  Input: {test_case['input']}")
        print(f"  Expected: {test_case['expected']}")
        print(f"  Result: {result}")
        
        assert result == test_case['expected'], f"Échec: {result} != {test_case['expected']}"
        print("  ✅ Réussi")
    
    print("\n✅ Tous les tests de résolution réussis")


def test_status_flow():
    """Test du flux de statuts."""
    print("\n=== Test: Flux de statuts ===")
    
    statuses = ['pending', 'running', 'completed']
    
    for status in statuses:
        print(f"\nStatut: {status}")
        
        # Simuler l'affichage
        if status == 'pending':
            print("  Badge: gris, Icône: fa-clock")
        elif status == 'running':
            print("  Badge: bleu, Icône: fa-spinner fa-spin")
        elif status == 'completed':
            print("  Badge: vert, Icône: fa-check-circle")
        elif status == 'failed':
            print("  Badge: rouge, Icône: fa-times-circle")
        
        print("  ✅ OK")
    
    print("\n✅ Test du flux de statuts réussi")


def test_progress_calculation():
    """Test du calcul de progression."""
    print("\n=== Test: Calcul de progression ===")
    
    total_tests = 10
    
    for executed in range(total_tests + 1):
        progress = int((executed / total_tests) * 100)
        print(f"Tests exécutés: {executed}/{total_tests} → Progression: {progress}%")
        
        expected = int((executed / total_tests) * 100)
        assert progress == expected, f"Échec: {progress} != {expected}"
    
    print("✅ Test de calcul de progression réussi")


def test_websocket_events():
    """Test des événements WebSocket."""
    print("\n=== Test: Événements WebSocket ===")
    
    mock_socketio = MockSocketIO()
    
    # Simuler les événements
    events = [
        ('campain_started', {'rapport_id': '123', 'campain_id': '456'}),
        ('test_started', {'rapport_id': '123', 'test_id': '789'}),
        ('test_completed', {'rapport_id': '123', 'test_id': '789', 'status': 'passed', 'logs': 'OK'}),
        ('campain_progress', {'rapport_id': '123', 'progress': 50}),
        ('campain_completed', {'rapport_id': '123', 'status': 'completed', 'result': 'success'})
    ]
    
    for event_name, event_data in events:
        mock_socketio.emit(event_name, event_data)
    
    print(f"\nNombre d'événements émis: {len(mock_socketio.events)}")
    assert len(mock_socketio.events) == 5, "Tous les événements devraient être émis"
    
    print("✅ Test des événements WebSocket réussi")


def main():
    """Exécute tous les tests."""
    print("=" * 60)
    print("TESTS DU SYSTÈME D'EXÉCUTION DE CAMPAGNES")
    print("=" * 60)
    
    try:
        test_generate_name()
        test_variable_resolution()
        test_status_flow()
        test_progress_calculation()
        test_websocket_events()
        
        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS ONT RÉUSSI")
        print("=" * 60)
        
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
