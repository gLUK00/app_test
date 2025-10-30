"""Action pour effectuer des opérations WebDAV."""
import requests
from requests.auth import HTTPBasicAuth
from plugins.actions.action_base import ActionBase
from webdav4.client import Client

class WebdavAction(ActionBase):
    """Action pour effectuer des opérations WebDAV sur un serveur distant."""
    
    # Métadonnées du plugin
    plugin_name = "webdav"
    version = "1.0.0"
    author = "TestGyver Team"
    
    def get_metadata(self):
        """Retourne les métadonnées de l'action."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Effectue des opérations WebDAV sur un serveur distant"
        }
    
    def validate_config(self, config):
        """Valide la configuration de l'action."""
        required_fields = ['method', 'url', 'username', 'password']
        for field in required_fields:
            if field not in config or not config[field]:
                return (False, f"Le champ '{field}' est obligatoire")
        return (True, "")
    
    def get_input_mask(self):
        """Retourne le masque de saisie pour les opérations WebDAV."""
        return [
            {
                "name": "url",
                "type": "string",
                "label": "URL WebDAV",
                "placeholder": "http(s)://serveur/webdav/chemin",
                "required": True
            },
            {
                "name": "username",
                "type": "string",
                "label": "Utilisateur",
                "placeholder": "Nom d'utilisateur WebDAV",
                "required": False
            },
            {
                "name": "password",
                "type": "string",
                "label": "Mot de passe",
                "placeholder": "Mot de passe WebDAV",
                "required": False
            },
            {
                "name": "action",
                "type": "select",
                "label": "Action WebDAV",
                "options": ["CHECK", "INFO", "LIST", "MKDIR", "CLEAN", "COPY", "MOVE", "DOWNLOAD", "UPLOAD"],
                "required": True
            },
            {
                "name": "srcFile",
                "type": "string",
                "label": "Fichier source/chemin",
                "placeholder": "pour check, info, list, clean, copy, move, download, upload",
                "required": False
            },
            {
                "name": "targFile",
                "type": "string",
                "label": "Fichier cible/chemin",
                "placeholder": "pour copy, move, download, upload",
                "required": False
            }
        ]
    
    def get_output_variables(self):
        """Retourne la liste des variables de sortie pour les opérations WebDAV."""
        return [
            {
                "name": "webdav_response",
                "description": "Retour de la réponse de l'action du WebDAV"
            }
        ]
    
    def execute(self, action_context):
        """
        Exécute une opération WebDAV.
        
        Args:
            action_context: Dictionnaire contenant method, url, username, password, headers, body
        """
        try:
            url = action_context.get('url')
            username = action_context.get('username', '')
            password = action_context.get('password', '')
            action = action_context.get('action').upper()
            src_file = action_context.get('srcFile', '')
            targ_file = action_context.get('targFile', '')
            
            self.add_trace(f"Préparation de l'opération WebDAV {action} vers {url}")
            
            auth = ()
            if username and password:
                self.add_trace(f"Authentification avec l'utilisateur: {username}")
                auth = (username, password)
            client = Client(url, auth=auth)
            
            if action == "CHECK":
                exists = client.exists(src_file)
                status_text = 'existe' if exists else "n'existe pas"
                self.add_trace(f"Vérification de l'existence de {src_file}: {status_text}")
                return self.get_result( True, { "webdav_response": exists })
            if action == "INFO":
                info = client.info(src_file)
                self.add_trace(f"Informations sur {src_file}: {info}")
                return self.get_result( True, { "webdav_response": info })
            if action == "LIST":
                listing = client.ls(src_file)
                self.add_trace(f"Liste des fichiers dans {src_file}: {listing}")
                return self.get_result( True, { "webdav_response": listing })
            if action == "MKDIR":
                client.mkdir(src_file)
                self.add_trace(f"Répertoire créé: {src_file}")
                return self.get_result( True, None )
            if action == "CLEAN":
                client.clean(src_file)
                self.add_trace(f"Contenu nettoyé dans: {src_file}")
                return self.get_result( True, None )
            if action == "COPY":
                client.copy(src_file, targ_file)
                self.add_trace(f"Fichier copié de {src_file} à {targ_file}")
                return self.get_result( True, None )
            if action == "MOVE":
                client.move(src_file, targ_file)
                self.add_trace(f"Fichier déplacé de {src_file} à {targ_file}")
                return self.get_result( True, None )
            if action == "DOWNLOAD":
                local_path = targ_file
                client.download_sync(remote_path=src_file, local_path=local_path)
                self.add_trace(f"Fichier téléchargé de {src_file} à {local_path}")
                return self.get_result( True, None )
            if action == "UPLOAD":
                local_path = src_file
                client.upload_sync(remote_path=targ_file, local_path=local_path)
                self.add_trace(f"Fichier téléchargé de {local_path} à {targ_file}")
                return self.get_result( True, None )

            raise ValueError(f"Action WebDAV inconnue: {action}")
        
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur inattendue: {str(e)}")
            return self.get_result( False, None )
