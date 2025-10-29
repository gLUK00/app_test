#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour valider la gestion des tokens JWT invalides ou expirés.
"""
import jwt
from datetime import datetime, timedelta
from utils.auth import decode_token, generate_token
from utils.db import load_config

def test_valid_token():
    """Test avec un token valide."""
    print("Test 1: Token valide")
    token = generate_token("user_123", "user")
    payload = decode_token(token)
    
    if payload and 'error' not in payload:
        print("✅ Token valide décodé avec succès")
        print(f"   User ID: {payload.get('user_id')}")
        print(f"   Role: {payload.get('role')}")
    else:
        print("❌ Erreur lors du décodage du token valide")
    print()

def test_expired_token():
    """Test avec un token expiré."""
    print("Test 2: Token expiré")
    config = load_config()
    
    # Créer un token expiré (expiré il y a 1 heure)
    expiration = datetime.utcnow() - timedelta(hours=1)
    payload = {
        'user_id': 'user_123',
        'role': 'user',
        'exp': expiration,
        'iat': datetime.utcnow() - timedelta(hours=2)
    }
    
    expired_token = jwt.encode(payload, config['jwt_secret'], algorithm='HS256')
    result = decode_token(expired_token)
    
    if result and result.get('error') == 'expired':
        print("✅ Token expiré détecté correctement")
        print(f"   Message: {result.get('message')}")
    else:
        print("❌ Le token expiré n'a pas été détecté")
    print()

def test_invalid_token():
    """Test avec un token invalide."""
    print("Test 3: Token invalide")
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    result = decode_token(invalid_token)
    
    if result and result.get('error') == 'invalid':
        print("✅ Token invalide détecté correctement")
        print(f"   Message: {result.get('message')}")
    else:
        print("❌ Le token invalide n'a pas été détecté")
    print()

def test_malformed_token():
    """Test avec un token malformé."""
    print("Test 4: Token malformé")
    malformed_token = "ceci.nest.pas.un.token.valide"
    result = decode_token(malformed_token)
    
    if result and result.get('error') == 'invalid':
        print("✅ Token malformé détecté correctement")
        print(f"   Message: {result.get('message')}")
    else:
        print("❌ Le token malformé n'a pas été détecté")
    print()

def main():
    """Fonction principale pour exécuter tous les tests."""
    print("="*60)
    print("Test de validation des tokens JWT")
    print("="*60)
    print()
    
    try:
        test_valid_token()
        test_expired_token()
        test_invalid_token()
        test_malformed_token()
        
        print("="*60)
        print("Tous les tests sont terminés !")
        print("="*60)
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution des tests: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
