"""Routes API pour la gestion des utilisateurs."""

from flask import Blueprint, request, jsonify
from models.user import User
from utils.auth import token_required, admin_required
from utils.pagination import get_pagination_params, paginate_results
from utils.validation import validate_required_fields

users_bp = Blueprint("users_api", __name__, url_prefix="/api/users")


@users_bp.route("", methods=["GET"])
@token_required
@admin_required
def get_users():
    """Récupère la liste des utilisateurs (admin uniquement)."""
    try:
        users = User.get_all()
        page, page_size = get_pagination_params(request)
        result = paginate_results(users, page, page_size)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"message": f"Erreur serveur: {str(e)}"}), 500


@users_bp.route("", methods=["POST"])
@token_required
@admin_required
def create_user():
    """Crée un nouvel utilisateur (admin uniquement)."""
    try:
        data = request.get_json()

        # Validation
        is_valid, message = validate_required_fields(
            data, ["name", "email", "password"]
        )
        if not is_valid:
            return jsonify({"message": message}), 400

        role = data.get("role", "user")

        user_id = User.create(
            name=data["name"], email=data["email"], password=data["password"], role=role
        )

        return (
            jsonify({"message": "Utilisateur créé avec succès", "user_id": user_id}),
            201,
        )

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

    except Exception as e:
        return jsonify({"message": f"Erreur serveur: {str(e)}"}), 500


@users_bp.route("/<user_id>", methods=["GET"])
@token_required
@admin_required
def get_user(user_id):
    """Récupère les détails d'un utilisateur spécifique."""
    try:
        user = User.find_by_id(user_id)

        if not user:
            return jsonify({"message": "Utilisateur non trouvé"}), 404

        return jsonify(user), 200

    except Exception as e:
        return jsonify({"message": f"Erreur serveur: {str(e)}"}), 500


@users_bp.route("/<user_id>", methods=["PUT"])
@token_required
@admin_required
def update_user(user_id):
    """Met à jour un utilisateur existant (admin uniquement)."""
    try:
        data = request.get_json()

        User.update(user_id, data)

        return jsonify({"message": "Utilisateur mis à jour avec succès"}), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

    except Exception as e:
        return jsonify({"message": f"Erreur serveur: {str(e)}"}), 500


@users_bp.route("/<user_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_user(user_id):
    """Supprime un utilisateur (admin uniquement)."""
    try:
        success = User.delete(user_id)

        if not success:
            return jsonify({"message": "Utilisateur non trouvé"}), 404

        return jsonify({"message": "Utilisateur supprimé avec succès"}), 200

    except Exception as e:
        return jsonify({"message": f"Erreur serveur: {str(e)}"}), 500
