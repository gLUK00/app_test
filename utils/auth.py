"""Utilitaires pour la gestion de l'authentification JWT."""
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from utils.db import load_config

def generate_token(user_id, role):
    """Génère un token JWT pour un utilisateur."""
    config = load_config()
    expiration = datetime.utcnow() + timedelta(minutes=config['security']['token_expiration_minutes'])
    
    payload = {
        'user_id': str(user_id),
        'role': role,
        'exp': expiration,
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, config['jwt_secret'], algorithm='HS256')
    return token

def decode_token(token):
    """Décode un token JWT et retourne le payload."""
    config = load_config()
    try:
        payload = jwt.decode(token, config['jwt_secret'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Décorateur pour protéger les routes nécessitant une authentification."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Vérifier le header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Format: "Bearer <token>"
            except IndexError:
                return jsonify({'message': 'Format de token invalide'}), 401
        
        # Vérifier le cookie
        if not token and 'token' in request.cookies:
            token = request.cookies.get('token')
        
        if not token:
            return jsonify({'message': 'Token manquant'}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'message': 'Token invalide ou expiré'}), 401
        
        # Ajouter les informations utilisateur à la requête
        request.user_id = payload['user_id']
        request.user_role = payload['role']
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Décorateur pour protéger les routes nécessitant un rôle administrateur."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, 'user_role') or request.user_role != 'admin':
            return jsonify({'message': 'Accès refusé : droits administrateur requis'}), 403
        return f(*args, **kwargs)
    
    return decorated
