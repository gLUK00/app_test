"""Action pour effectuer des requêtes HTTP."""
import requests
from plugins.actions.action_base import ActionBase

class HTTPRequestAction(ActionBase):
    """Action pour effectuer des requêtes HTTP (GET, POST, PUT, DELETE)."""
    
    def get_input_mask(self):
        """Retourne le masque de saisie pour les requêtes HTTP."""
        return [
            {
                "name": "method",
                "type": "select",
                "label": "Méthode HTTP",
                "options": ["GET", "POST", "PUT", "DELETE"],
                "required": True
            },
            {
                "name": "url",
                "type": "string",
                "label": "URL",
                "placeholder": "https://example.com/api/endpoint",
                "required": True
            },
            {
                "name": "headers",
                "type": "textarea",
                "label": "En-têtes HTTP (JSON)",
                "placeholder": '{"Content-Type": "application/json"}',
                "required": False
            },
            {
                "name": "body",
                "type": "textarea",
                "label": "Corps de la requête (pour POST/PUT)",
                "placeholder": '{"key": "value"}',
                "required": False
            }
        ]
    
    def execute(self, action_context):
        """
        Exécute une requête HTTP.
        
        Args:
            action_context: Dictionnaire contenant method, url, headers, body
        """
        try:
            method = action_context.get('method', 'GET').upper()
            url = action_context.get('url')
            headers = action_context.get('headers', {})
            body = action_context.get('body')
            
            self.add_trace(f"Préparation de la requête {method} vers {url}")
            
            # Parser les headers si c'est une string JSON
            if isinstance(headers, str):
                import json
                headers = json.loads(headers) if headers else {}
            
            # Parser le body si c'est une string JSON
            if isinstance(body, str) and body:
                import json
                body = json.loads(body)
            
            # Effectuer la requête
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=body, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=body, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                self.set_code(1)
                self.add_trace(f"Méthode HTTP non supportée: {method}")
                return self.get_result()
            
            self.add_trace(f"Statut de la réponse: {response.status_code}")
            self.add_trace(f"Temps de réponse: {response.elapsed.total_seconds()}s")
            
            if response.status_code >= 200 and response.status_code < 300:
                self.set_code(0)
                self.add_trace("Requête réussie")
                
                result_data = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text[:1000]  # Limiter la taille
                }
                
                return self.get_result(result_data)
            else:
                self.set_code(1)
                self.add_trace(f"Erreur HTTP: {response.status_code}")
                return self.get_result({"status_code": response.status_code, "error": response.text[:500]})
        
        except requests.exceptions.Timeout:
            self.set_code(1)
            self.add_trace("Timeout: la requête a pris trop de temps")
            return self.get_result()
        
        except requests.exceptions.ConnectionError:
            self.set_code(1)
            self.add_trace("Erreur de connexion: impossible de joindre le serveur")
            return self.get_result()
        
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur lors de l'exécution: {str(e)}")
            return self.get_result()
