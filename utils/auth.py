"""Utilitaires pour la gestion de l'authentification JWT."""
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, redirect, url_for, flash
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
        return {'error': 'expired', 'message': 'Votre session a expiré. Veuillez vous reconnecter.'}
    except jwt.InvalidTokenError:
        return {'error': 'invalid', 'message': 'Token invalide. Veuillez vous reconnecter.'}

def token_required(f):
    """Décorateur pour protéger les routes nécessitant une authentification."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        is_api_request = request.path.startswith('/api/')
        
        # Vérifier le header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Format: "Bearer <token>"
            except IndexError:
                if is_api_request:
                    return jsonify({'message': 'Format de token invalide'}), 401
                flash('Format de token invalide', 'error')
                return redirect(url_for('web.index'))
        
        # Vérifier le cookie
        if not token and 'token' in request.cookies:
            token = request.cookies.get('token')
        
        if not token:
            if is_api_request:
                return jsonify({'message': 'Token manquant'}), 401
            flash('Vous devez vous connecter pour accéder à cette page', 'warning')
            return redirect(url_for('web.index'))
        
        payload = decode_token(token)
        
        # Vérifier si le token contient une erreur
        if not payload or 'error' in payload:
            error_message = payload.get('message', 'Token invalide ou expiré') if payload else 'Token invalide ou expiré'
            if is_api_request:
                return jsonify({'message': error_message}), 401
            flash(error_message, 'error')
            response = redirect(url_for('web.index'))
            # Supprimer le cookie invalide
            response.set_cookie('token', '', expires=0)
            return response
        
        # Ajouter les informations utilisateur à la requête
        request.user_id = payload['user_id']
        request.user_role = payload['role']
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Décorateur pour protéger les routes nécessitant un rôle administrateur."""
    @wraps(f)
    def decorated(*args, **kwargs):
        is_api_request = request.path.startswith('/api/')
        
        if not hasattr(request, 'user_role') or request.user_role != 'admin':
            if is_api_request:
                return jsonify({'message': 'Accès refusé : droits administrateur requis'}), 403
            flash('Accès refusé : vous devez être administrateur pour accéder à cette page', 'error')
            return redirect(url_for('web.dashboard'))
        return f(*args, **kwargs)
    
    return decorated
