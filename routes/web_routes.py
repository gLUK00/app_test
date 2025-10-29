"""Routes web pour les pages de l'application."""
from flask import Blueprint, render_template, redirect, url_for, request
from utils.auth import token_required, admin_required, decode_token

web_bp = Blueprint('web', __name__)

def get_current_user():
    """Récupère l'utilisateur courant depuis le token."""
    token = request.cookies.get('token')
    if token:
        payload = decode_token(token)
        # Vérifier si le payload contient une erreur
        if payload and 'error' not in payload:
            return {
                'id': payload.get('user_id'),
                'role': payload.get('role')
            }
    return None

@web_bp.route('/')
def index():
    """Page d'authentification."""
    user = get_current_user()
    if user:
        return redirect(url_for('web.dashboard'))
    return render_template('login.html')

@web_bp.route('/dashboard')
@token_required
def dashboard():
    """Tableau de bord principal après authentification."""
    user = get_current_user()
    return render_template('dashboard.html', user=user)

@web_bp.route('/campains/add')
@token_required
def add_campain():
    """Page d'ajout d'une nouvelle campagne."""
    user = get_current_user()
    return render_template('campain_add.html', user=user)

@web_bp.route('/campains/<campain_id>')
@token_required
def campain_details(campain_id):
    """Page de détails d'une campagne spécifique."""
    user = get_current_user()
    return render_template('campain_details.html', user=user, campain_id=campain_id)

@web_bp.route('/campains/<campain_id>/add/test')
@token_required
def add_test(campain_id):
    """Page d'ajout d'un test à une campagne."""
    user = get_current_user()
    return render_template('test_add.html', user=user, campain_id=campain_id)

@web_bp.route('/campains/<campain_id>/edit/test/<test_id>')
@token_required
def edit_test(campain_id, test_id):
    """Page d'édition d'un test."""
    user = get_current_user()
    return render_template('test_edit.html', user=user, campain_id=campain_id, test_id=test_id)

@web_bp.route('/admin/users')
@token_required
@admin_required
def admin_users():
    """Gestion des utilisateurs (admin uniquement)."""
    user = get_current_user()
    return render_template('admin/users.html', user=user)

@web_bp.route('/admin/users/add')
@token_required
@admin_required
def admin_users_add():
    """Ajout d'un nouvel utilisateur."""
    user = get_current_user()
    return render_template('admin/user_add.html', user=user)

@web_bp.route('/admin/users/edit/<user_id>')
@token_required
@admin_required
def admin_users_edit(user_id):
    """Édition d'un utilisateur existant."""
    user = get_current_user()
    return render_template('admin/user_edit.html', user=user, user_id=user_id)

@web_bp.route('/admin/variables')
@token_required
@admin_required
def admin_variables():
    """Gestion des variables (admin uniquement)."""
    user = get_current_user()
    return render_template('admin/variables.html', user=user)

@web_bp.route('/admin/variables/add')
@token_required
@admin_required
def admin_variables_add():
    """Ajout d'une nouvelle variable."""
    user = get_current_user()
    return render_template('admin/variable_add.html', user=user)

@web_bp.route('/admin/variables/edit/<variable_id>')
@token_required
@admin_required
def admin_variables_edit(variable_id):
    """Édition d'une variable existante."""
    user = get_current_user()
    return render_template('admin/variable_edit.html', user=user, variable_id=variable_id)
