"""Action pour effectuer des requêtes HTTP."""
import requests
from plugins.actions.action_base import ActionBase


class HTTPRequestAction(ActionBase):
    """Action pour effectuer des requêtes HTTP (GET, POST, PUT, DELETE)."""
    
    # Métadonnées du plugin
    plugin_name = "http"
    label = "HTTP Request"
    version = "1.0.0"
    author = "TestGyver Team"
    
    def get_metadata(self):
        """Retourne les métadonnées de l'action."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Effectue des requêtes HTTP (GET, POST, PUT, DELETE)"
        }
    
    def validate_config(self, config):
        """Valide la configuration de l'action."""
        if 'url' not in config or not config['url']:
            return (False, "L'URL est obligatoire")
        if 'method' not in config or not config['method']:
            return (False, "La méthode HTTP est obligatoire")
        if config['method'].upper() not in ['GET', 'POST', 'PUT', 'DELETE']:
            return (False, f"Méthode HTTP non supportée: {config['method']}")
        return (True, "")
    
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
            },
            {
                "name": "return_status_code",
                "type": "select",
                "label": "Code de statut HTTP attendu",
                "options": [200, 201, 400, 404, 500],
                "required": False
            },{
                "name": "timeout",
                "type": "number",
                "label": "Timeout (secondes)",
                "placeholder": 30,
                "required": False
            }
        ]
    
    def get_output_variables(self):
        """Retourne la liste des variables de sortie pour les requêtes HTTP."""
        return [
            {
                "name": "http_status_code",
                "description": "Code de statut HTTP de la réponse (ex: 200, 404, 500)",
                "type": "number"
            },
            {
                "name": "http_response_body",
                "description": "Corps de la réponse HTTP",
                "type": "string"
            },
            {
                "name": "http_response_time",
                "description": "Temps de réponse en secondes",
                "type": "number"
            },
            {
                "name": "http_response_headers",
                "description": "En-têtes de la réponse HTTP (JSON)",
                "type": "string"
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
            return_status_code = action_context.get('return_status_code', None)
            timeout = action_context.get('timeout', 30)
            
            self.add_trace(f"Préparation de la requête {method} vers {url}")
            
            # Parser les headers si c'est une string JSON
            if isinstance(headers, str):
                import json
                headers = json.loads(headers) if headers else {}
            
            # Parser le body si c'est une string JSON
            if isinstance(body, str) and body:
                import json
                body = json.loads(body)
            
            """
            oDataConvert2pdf = { 'in': sTmpFileIn, 'out': sTmpFileOut, 'type': sType, 'session': coreRequest.getSessionId() }
            res = requests.post( coreConfig.services[ "endpoint" ][ "convert2pdf-convert-v0" ], data=oDataConvert2pdf, verify=False )
            if res.status_code != 200:
            """
            
            # Effectuer la requête
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout, verify=False)
            elif method == 'POST':
                response = requests.post(url, headers=headers, data=body, timeout=timeout, verify=False)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, data=body, timeout=timeout, verify=False)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout, verify=False)
            else:
                self.set_code(1)
                self.add_trace(f"Méthode HTTP non supportée: {method}")
                return self.get_result()
            
            self.add_trace(f"Statut de la réponse: {response.status_code}")
            self.add_trace(f"Temps de réponse: {response.elapsed.total_seconds()}s")
            
            # Préparer les variables de sortie
            output_vars = {
                "http_status_code": response.status_code,
                "http_response_body": response.text,
                "http_response_time": response.elapsed.total_seconds(),
                "http_response_headers": dict(response.headers)
            }
            
            # si il y a un code de statut attendu, vérifier
            if return_status_code and str( response.status_code ) != return_status_code:
                self.set_code(1)
                self.add_trace(f"Code de statut inattendu: attendu {return_status_code}, reçu {response.status_code}")
                return self.get_result( False, output_vars )

            if return_status_code or ( response.status_code >= 200 and response.status_code < 300 ):
                self.set_code(0)
                self.add_trace("Requête réussie")
                
                return self.get_result(True, output_vars)

            self.set_code(1)
            self.add_trace(f"Erreur HTTP: {response.status_code}")
            return self.get_result( False, None )
        
        except requests.exceptions.Timeout:
            self.set_code(1)
            self.add_trace("Timeout: la requête a pris trop de temps")
            return self.get_result( False, None )

        except requests.exceptions.ConnectionError:
            self.set_code(1)
            self.add_trace("Erreur de connexion: impossible de joindre le serveur")
            return self.get_result( False, None )
        
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur lors de l'exécution: {str(e)}")
            return self.get_result( False, None )
