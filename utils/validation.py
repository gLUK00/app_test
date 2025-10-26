"""Utilitaires pour la validation des données."""
import re
from utils.db import load_config

def validate_email(email):
    """Valide le format d'une adresse email."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Valide qu'un mot de passe respecte les exigences de sécurité."""
    config = load_config()
    min_length = config['security']['password_min_length']
    
    if len(password) < min_length:
        return False, f"Le mot de passe doit contenir au moins {min_length} caractères"
    
    return True, "Mot de passe valide"

def validate_required_fields(data, required_fields):
    """Vérifie que tous les champs requis sont présents dans les données."""
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        return False, f"Champs manquants : {', '.join(missing_fields)}"
    
    return True, "Tous les champs requis sont présents"

def sanitize_string(value):
    """Nettoie une chaîne de caractères pour éviter les injections."""
    if not isinstance(value, str):
        return value
    
    # Supprimer les caractères potentiellement dangereux
    dangerous_chars = ['<', '>', '"', "'", '`', '$', '{', '}']
    for char in dangerous_chars:
        value = value.replace(char, '')
    
    return value.strip()
