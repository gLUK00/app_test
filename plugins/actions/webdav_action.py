"""Action pour effectuer des opérations WebDAV."""
import requests
from requests.auth import HTTPBasicAuth
from plugins.actions.action_base import ActionBase

class WebdavAction(ActionBase):
    """Action pour effectuer des opérations WebDAV sur un serveur distant."""
    
    def get_input_mask(self):
        """Retourne le masque de saisie pour les opérations WebDAV."""
        return [
            {
                "name": "method",
                "type": "select",
                "label": "Méthode WebDAV",
                "options": ["GET", "PUT", "DELETE", "MKCOL"],
                "required": True
            },
            {
                "name": "url",
                "type": "string",
                "label": "URL",
                "placeholder": "https://webdav.example.com/path/to/resource",
                "required": True
            },
            {
                "name": "username",
                "type": "string",
                "label": "Nom d'utilisateur",
                "placeholder": "user",
                "required": True
            },
            {
                "name": "password",
                "type": "string",
                "label": "Mot de passe",
                "placeholder": "••••••••",
                "required": True
            },
            {
                "name": "headers",
                "type": "textarea",
                "label": "En-têtes HTTP (JSON)",
                "placeholder": '{"Content-Type": "text/xml"}',
                "required": False
            },
            {
                "name": "body",
                "type": "textarea",
                "label": "Corps de la requête (pour PUT)",
                "placeholder": "Contenu du fichier ou données XML",
                "required": False
            }
        ]
    
    def execute(self, action_context):
        """
        Exécute une opération WebDAV.
        
        Args:
            action_context: Dictionnaire contenant method, url, username, password, headers, body
        """
        try:
            method = action_context.get('method', 'GET').upper()
            url = action_context.get('url')
            username = action_context.get('username')
            password = action_context.get('password')
            headers = action_context.get('headers', {})
            body = action_context.get('body')
            
            self.add_trace(f"Préparation de l'opération WebDAV {method} vers {url}")
            
            # Parser les headers si c'est une string JSON
            if isinstance(headers, str):
                import json
                headers = json.loads(headers) if headers else {}
            
            # Authentification de base
            auth = HTTPBasicAuth(username, password)
            
            self.add_trace(f"Authentification avec l'utilisateur: {username}")
            
            # Effectuer la requête WebDAV
            if method == 'GET':
                response = requests.get(url, auth=auth, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, auth=auth, headers=headers, data=body, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, auth=auth, headers=headers, timeout=30)
            elif method == 'MKCOL':
                # MKCOL est utilisé pour créer une collection (répertoire)
                response = requests.request('MKCOL', url, auth=auth, headers=headers, timeout=30)
            else:
                self.set_code(1)
                self.add_trace(f"Méthode WebDAV non supportée: {method}")
                return self.get_result()
            
            self.add_trace(f"Statut de la réponse: {response.status_code}")
            
            if response.status_code >= 200 and response.status_code < 300:
                self.set_code(0)
                self.add_trace("Opération WebDAV réussie")
                
                result_data = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text[:1000] if method == 'GET' else None
                }
                
                return self.get_result(result_data)
            else:
                self.set_code(1)
                self.add_trace(f"Erreur WebDAV: {response.status_code}")
                return self.get_result({"status_code": response.status_code, "error": response.text[:500]})
        
        except requests.exceptions.Timeout:
            self.set_code(1)
            self.add_trace("Timeout lors de la connexion au serveur WebDAV")
            return self.get_result()
        
        except requests.exceptions.ConnectionError:
            self.set_code(1)
            self.add_trace("Erreur de connexion au serveur WebDAV")
            return self.get_result()
        
        except requests.exceptions.RequestException as e:
            self.set_code(1)
            self.add_trace(f"Erreur lors de la requête WebDAV: {str(e)}")
            return self.get_result()
        
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur inattendue: {str(e)}")
            return self.get_result()
