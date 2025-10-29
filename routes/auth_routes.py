# -*- coding: utf-8 -*-
"""Routes API pour l'authentification."""
from flask import Blueprint, request, jsonify, make_response
from models.user import User
from utils.auth import generate_token, token_required
from utils.validation import validate_required_fields

auth_bp = Blueprint('auth_api', __name__, url_prefix='/api')

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    API d'authentification.
    Retourne un token JWT en cas de succès.
    """
    try:
        data = request.get_json()
        
        # Validation des champs requis
        is_valid, message = validate_required_fields(data, ['email', 'password'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        email = data['email']
        password = data['password']
        
        # Vérifier les identifiants
        if not User.verify_password(email, password):
            return jsonify({'message': 'Email ou mot de passe incorrect'}), 401
        
        # Récupérer l'utilisateur
        user = User.find_by_email(email)
        
        # Générer le token
        token = generate_token(user['_id'], user['role'])
        
        response = make_response(jsonify({
            'message': 'Authentification réussie',
            'token': token,
            'user': {
                'id': user['_id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role']
            }
        }))
        
        # Définir le cookie
        response.set_cookie('token', token, httponly=True, secure=False, samesite='Lax')
        
        return response, 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """API de déconnexion."""
    response = make_response(jsonify({'message': 'Déconnexion réussie'}))
    response.set_cookie('token', '', expires=0)
    return response, 200

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """Récupère les informations de l'utilisateur connecté."""
    try:
        user = User.find_by_id(request.user_id)
        
        if not user:
            return jsonify({'message': 'Utilisateur non trouvé'}), 404
        
        return jsonify({
            'id': user['_id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role']
        }), 200
    
    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500
