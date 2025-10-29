#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script de test pour vérifier le fonctionnement des masques de saisie dynamiques."""

from app import create_app
import json

def test_actions_masks():
    """Teste l'endpoint qui retourne les masques de saisie."""
    app = create_app()
    
    with app.test_client() as client:
        # Test GET /api/actions/masks
        print("Test 1: Récupération de tous les masques de saisie")
        response = client.get('/api/actions/masks')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"Types d'actions disponibles: {list(data.keys())}")
            
            # Vérifier chaque type
            for action_type, mask in data.items():
                print(f"\n{action_type.upper()}:")
                for field in mask:
                    required = "obligatoire" if field.get('required') else "optionnel"
                    print(f"  - {field['name']} ({field['type']}, {required}): {field['label']}")
        else:
            print(f"Erreur: {response.data}")
        
        # Test GET /api/actions/masks/http
        print("\n" + "="*60)
        print("Test 2: Récupération du masque HTTP uniquement")
        response = client.get('/api/actions/masks/http')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"Type: {data['type']}")
            print(f"Nombre de champs: {len(data['mask'])}")
        else:
            print(f"Erreur: {response.data}")
        
        # Test avec un type invalide
        print("\n" + "="*60)
        print("Test 3: Test avec un type invalide")
        response = client.get('/api/actions/masks/invalid')
        print(f"Status: {response.status_code}")
        print(f"Réponse: {response.data.decode('utf-8')}")

if __name__ == '__main__':
    test_actions_masks()
