"""Action pour effectuer des opérations WebDAV."""
import os
from plugins.actions.action_base import ActionBase
from webdav4.client import Client

class WebdavAction(ActionBase):
    """Action pour effectuer des opérations WebDAV sur un serveur distant."""
    
    # Métadonnées du plugin
    plugin_name = "webdav"
    version = "1.0.0"
    author = "TestGyver Team"
    
    def _is_directory(self, client, path):
        """
        Vérifie si un chemin est un répertoire en utilisant la méthode info().
        
        Args:
            client: Instance du client WebDAV
            path: Chemin à vérifier (avec ou sans slash final)
        
        Returns:
            bool: True si c'est un répertoire, False sinon
        """
        try:
            # Normaliser le chemin avec slash final pour les répertoires
            check_path = path.rstrip('/') + '/'
            info = client.info(check_path)
            # Vérifier si c'est une collection (répertoire)
            return info.get('type') == 'directory'
        except Exception:
            # Si info échoue, essayer avec ls
            try:
                check_path = path.rstrip('/') + '/'
                client.ls(check_path, detail=False)
                return True  # Si ls réussit, c'est un répertoire
            except Exception:
                return False  # Si les deux échouent, ce n'est pas un répertoire
    
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
                "options": ["CHECK", "INFO", "LIST", "MKDIR", "CLEAN", "MOVE", "DOWNLOAD", "UPLOAD"],
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
                # Créer récursivement les répertoires si nécessaire
                self._mkdir_recursive(client, src_file)
                self.add_trace(f"Répertoire créé: {src_file}")
                return self.get_result( True, { "webdav_response": True } )
            if action == "CLEAN":
                client.clean(src_file)
                self.add_trace(f"Contenu nettoyé dans: {src_file}")
                return self.get_result( True, { "webdav_response": True } )
            if action == "MOVE":
                client.move(src_file, targ_file)
                self.add_trace(f"Fichier déplacé de {src_file} à {targ_file}")
                return self.get_result( True, { "webdav_response": True } )
            if action == "DOWNLOAD":
                local_path = targ_file
                client.download_file(remote_path=src_file, local_path=local_path)
                self.add_trace(f"Fichier téléchargé de {src_file} à {local_path}")
                return self.get_result( True, { "webdav_response": True } )
            if action == "UPLOAD":
                
                local_path = src_file
                
                # Vérifier si src_file est un fichier ou un répertoire
                if os.path.isfile(local_path):
                    # Upload d'un seul fichier
                    client.upload_file(from_path=local_path, to_path=targ_file)
                    self.add_trace(f"Fichier uploadé de {local_path} à {targ_file}")
                elif os.path.isdir(local_path):
                    # Upload récursif d'un répertoire
                    self._upload_directory_recursive(client, local_path, targ_file)
                    self.add_trace(f"Répertoire uploadé de {local_path} à {targ_file}")
                else:
                    raise ValueError(f"Le chemin local '{local_path}' n'existe pas ou n'est ni un fichier ni un répertoire")
                
                return self.get_result( True, None )

            raise ValueError(f"Action WebDAV inconnue: {action}")
        
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur inattendue: {str(e)}")
            return self.get_result( False, None )
    
    def _upload_directory_recursive(self, client, local_dir, remote_dir):
        """
        Upload récursif d'un répertoire local vers WebDAV.
        
        Args:
            client: Instance du client WebDAV
            local_dir: Chemin local du répertoire à uploader
            remote_dir: Chemin distant WebDAV de destination
        """
        
        # Normaliser les chemins
        local_dir = local_dir.rstrip(os.sep)
        remote_dir = remote_dir.rstrip('/')
        
        # Créer le répertoire distant s'il n'existe pas
        # WebDAV nécessite un slash final pour les collections/répertoires
        remote_dir_with_slash = remote_dir + '/'
        if not self._is_directory(client, remote_dir_with_slash):
            self._mkdir_recursive(client, remote_dir)
        
        # Parcourir tous les fichiers et sous-répertoires
        for item in os.listdir(local_dir):
            local_path = os.path.join(local_dir, item)
            remote_path = f"{remote_dir}/{item}"
            
            if os.path.isfile(local_path):
                # Upload du fichier
                client.upload_file(from_path=local_path, to_path=remote_path)
                self.add_trace(f"Fichier uploadé: {local_path} -> {remote_path}")
            elif os.path.isdir(local_path):
                # Appel récursif pour le sous-répertoire
                self._upload_directory_recursive(client, local_path, remote_path)
    
    def _mkdir_recursive(self, client, path):
        """
        Crée récursivement les répertoires nécessaires.
        
        Args:
            client: Instance du client WebDAV
            path: Chemin complet du répertoire à créer
        """
        # Normaliser le chemin (enlever les slashes multiples et trailing slash)
        path = path.rstrip('/')
        
        # Si le répertoire existe déjà, ne rien faire
        # WebDAV nécessite un slash final pour les collections/répertoires
        try:
            if self._is_directory(client, path):
                self.add_trace(f"Le répertoire {path} existe déjà")
                return
        except Exception:
            # Si la vérification échoue, le répertoire n'existe probablement pas, on continue
            pass
        
        # Diviser le chemin en parties
        parts = [p for p in path.split('/') if p]
        
        # Construire et créer chaque niveau
        current_path = ''
        for part in parts:
            current_path = f"{current_path}/{part}" if current_path else part
            
            # Vérifier si ce niveau existe déjà en utilisant notre méthode
            # WebDAV nécessite un slash final pour les collections/répertoires
            try:
                if self._is_directory(client, current_path):
                    # Le répertoire existe déjà, passer au suivant
                    continue
            except Exception:
                # La vérification a échoué, le répertoire n'existe pas, on va le créer
                pass
            
            # Créer le répertoire
            try:
                client.mkdir(current_path)
                self.add_trace(f"Sous-répertoire créé: {current_path}")
            except Exception as e:
                # Vérifier si l'erreur est due au fait que le répertoire existe déjà
                error_msg = str(e).lower()
                if 'exists' in error_msg or 'already' in error_msg or '405' in error_msg:
                    # Le répertoire existe déjà, continuer
                    self.add_trace(f"Le sous-répertoire {current_path} existe déjà")
                    continue
                # Autre erreur, la propager
                self.add_trace(f"Erreur lors de la création de {current_path}: {str(e)}")
                raise
