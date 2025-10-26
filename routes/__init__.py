"""Package routes pour TestGyver."""
from .auth_routes import auth_bp
from .users_routes import users_bp
from .campains_routes import campains_bp
from .variables_routes import variables_bp
from .tests_routes import tests_bp
from .rapports_routes import rapports_bp
from .web_routes import web_bp

__all__ = [
    'auth_bp',
    'users_bp',
    'campains_bp',
    'variables_bp',
    'tests_bp',
    'rapports_bp',
    'web_bp'
]
