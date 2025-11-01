"""Action pour effectuer des opérations FTP."""
from ftplib import FTP, error_perm, error_temp
import io
from plugins.actions.action_base import ActionBase


class FTPAction(ActionBase):
    """Action pour effectuer des opérations FTP sur un serveur distant."""
    
    # Métadonnées du plugin
    plugin_name = "ftp"
    label = "FTP"
    version = "1.0.0"
    author = "TestGyver Team"
    
    def get_metadata(self):
        """Retourne les métadonnées de l'action."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Effectue des opérations FTP sur un serveur distant"
        }
    
    def validate_config(self, config):
        """Valide la configuration de l'action."""
        required_fields = ['method', 'host', 'username', 'password']
        for field in required_fields:
            if field not in config or not config[field]:
                return (False, f"Le champ '{field}' est obligatoire")
        return (True, "")
    
    def get_input_mask(self):
        """Retourne le masque de saisie pour les opérations FTP."""
        return [
            {
                "name": "method",
                "type": "select",
                "label": "Méthode FTP",
                "options": ["GET", "PUT", "DELETE", "LIST"],
                "required": True
            },
            {
                "name": "host",
                "type": "string",
                "label": "Hôte FTP",
                "placeholder": "ftp.example.com",
                "required": True
            },
            {
                "name": "port",
                "type": "number",
                "label": "Port",
                "placeholder": "21",
                "required": False
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
                "name": "remote_path",
                "type": "string",
                "label": "Chemin distant",
                "placeholder": "/path/to/file.txt",
                "required": True
            },
            {
                "name": "content",
                "type": "textarea",
                "label": "Contenu du fichier (pour PUT)",
                "placeholder": "Contenu à uploader",
                "required": False
            }
        ]
    
    def get_output_variables(self):
        """Retourne la liste des variables de sortie pour les opérations FTP."""
        return [
            {
                "name": "ftp_file_content",
                "description": "Contenu du fichier téléchargé (pour GET)",
                "type": "string"
            },
            {
                "name": "ftp_file_size",
                "description": "Taille du fichier en octets",
                "type": "number"
            },
            {
                "name": "ftp_file_list",
                "description": "Liste des fichiers (pour LIST)",
                "type": "string"
            },
            {
                "name": "ftp_operation_success",
                "description": "Indique si l'opération a réussi (true/false)",
                "type": "string"
            }
        ]
    
    def execute(self, action_context):
        """
        Exécute une opération FTP.
        
        Args:
            action_context: Dictionnaire contenant method, host, port, username, password, remote_path, content
        """
        ftp = None
        
        try:
            method = action_context.get('method', 'GET').upper()
            host = action_context.get('host')
            port = int(action_context.get('port', 21))
            username = action_context.get('username')
            password = action_context.get('password')
            remote_path = action_context.get('remote_path')
            content = action_context.get('content', '')
            
            self.add_trace(f"Connexion FTP à {host}:{port}")
            
            # Connexion au serveur FTP
            ftp = FTP()
            ftp.connect(host, port, timeout=30)
            ftp.login(username, password)
            
            self.add_trace(f"Connexion établie - Message de bienvenue: {ftp.getwelcome()}")
            
            # Exécuter l'opération demandée
            if method == 'GET':
                self.add_trace(f"Téléchargement du fichier: {remote_path}")
                
                # Télécharger le fichier
                data = io.BytesIO()
                ftp.retrbinary(f'RETR {remote_path}', data.write)
                
                file_content = data.getvalue().decode('utf-8', errors='replace')
                file_size = len(data.getvalue())
                
                # Préparer les variables de sortie
                output_vars = {
                    "ftp_file_content": file_content,
                    "ftp_file_size": file_size,
                    "ftp_file_list": "",
                    "ftp_operation_success": "true"
                }
                
                self.set_code(0)
                self.add_trace(f"Fichier téléchargé avec succès ({file_size} octets)")
                
                return self.get_result({
                    "content": file_content[:1000],  # Limiter la taille
                    "size": file_size
                }, output_vars)
            
            elif method == 'PUT':
                self.add_trace(f"Upload du fichier vers: {remote_path}")
                
                # Uploader le fichier
                data = io.BytesIO(content.encode('utf-8'))
                ftp.storbinary(f'STOR {remote_path}', data)
                
                file_size = len(content)
                
                # Préparer les variables de sortie
                output_vars = {
                    "ftp_file_content": "",
                    "ftp_file_size": file_size,
                    "ftp_file_list": "",
                    "ftp_operation_success": "true"
                }
                
                self.set_code(0)
                self.add_trace(f"Fichier uploadé avec succès ({file_size} octets)")
                
                return self.get_result({
                    "uploaded": True,
                    "size": file_size
                }, output_vars)
            
            elif method == 'DELETE':
                self.add_trace(f"Suppression du fichier: {remote_path}")
                
                # Supprimer le fichier
                ftp.delete(remote_path)
                
                # Préparer les variables de sortie
                output_vars = {
                    "ftp_file_content": "",
                    "ftp_file_size": 0,
                    "ftp_file_list": "",
                    "ftp_operation_success": "true"
                }
                
                self.set_code(0)
                self.add_trace("Fichier supprimé avec succès")
                
                return self.get_result({"deleted": True}, output_vars)
            
            elif method == 'LIST':
                self.add_trace(f"Liste des fichiers dans: {remote_path}")
                
                # Lister les fichiers
                files = []
                ftp.retrlines(f'LIST {remote_path}', files.append)
                
                file_list_str = "\n".join(files)
                
                # Préparer les variables de sortie
                output_vars = {
                    "ftp_file_content": "",
                    "ftp_file_size": 0,
                    "ftp_file_list": file_list_str,
                    "ftp_operation_success": "true"
                }
                
                self.set_code(0)
                self.add_trace(f"Liste récupérée ({len(files)} entrées)")
                
                return self.get_result({
                    "files": files[:50],  # Limiter à 50 entrées
                    "count": len(files)
                }, output_vars)
            
            else:
                self.set_code(1)
                self.add_trace(f"Méthode FTP non supportée: {method}")
                return self.get_result()
        
        except error_perm as e:
            self.set_code(1)
            self.add_trace(f"Erreur de permission FTP: {str(e)}")
            return self.get_result()
        
        except error_temp as e:
            self.set_code(1)
            self.add_trace(f"Erreur temporaire FTP: {str(e)}")
            return self.get_result()
        
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur inattendue: {str(e)}")
            return self.get_result()
        
        finally:
            if ftp:
                try:
                    ftp.quit()
                    self.add_trace("Connexion FTP fermée")
                except:
                    pass
