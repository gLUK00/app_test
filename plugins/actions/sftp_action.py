"""Action pour effectuer des opérations SFTP."""
import paramiko
import io
from plugins.actions.action_base import ActionBase


class SFTPAction(ActionBase):
    """Action pour effectuer des opérations SFTP sur un serveur distant."""
    
    # Métadonnées du plugin
    plugin_name = "sftp"
    version = "1.0.0"
    author = "TestGyver Team"
    
    def get_metadata(self):
        """Retourne les métadonnées de l'action."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Effectue des opérations SFTP sur un serveur distant"
        }
    
    def validate_config(self, config):
        """Valide la configuration de l'action."""
        required_fields = ['method', 'host', 'username', 'password']
        for field in required_fields:
            if field not in config or not config[field]:
                return (False, f"Le champ '{field}' est obligatoire")
        return (True, "")
    
    def get_input_mask(self):
        """Retourne le masque de saisie pour les opérations SFTP."""
        return [
            {
                "name": "method",
                "type": "select",
                "label": "Méthode SFTP",
                "options": ["GET", "PUT", "DELETE", "LIST"],
                "required": True
            },
            {
                "name": "host",
                "type": "string",
                "label": "Hôte SFTP",
                "placeholder": "sftp.example.com",
                "required": True
            },
            {
                "name": "port",
                "type": "number",
                "label": "Port",
                "placeholder": "22",
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
        """Retourne la liste des variables de sortie pour les opérations SFTP."""
        return [
            {
                "name": "sftp_file_content",
                "description": "Contenu du fichier téléchargé (pour GET)",
                "type": "string"
            },
            {
                "name": "sftp_file_size",
                "description": "Taille du fichier en octets",
                "type": "number"
            },
            {
                "name": "sftp_file_list",
                "description": "Liste des fichiers (pour LIST)",
                "type": "string"
            },
            {
                "name": "sftp_operation_success",
                "description": "Indique si l'opération a réussi (true/false)",
                "type": "string"
            }
        ]
    
    def execute(self, action_context):
        """
        Exécute une opération SFTP.
        
        Args:
            action_context: Dictionnaire contenant method, host, port, username, password, remote_path, content
        """
        ssh_client = None
        sftp = None
        
        try:
            method = action_context.get('method', 'GET').upper()
            host = action_context.get('host')
            port = int(action_context.get('port', 22))
            username = action_context.get('username')
            password = action_context.get('password')
            remote_path = action_context.get('remote_path')
            content = action_context.get('content', '')
            
            self.add_trace(f"Connexion SFTP à {username}@{host}:{port}")
            
            # Créer le client SSH
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Se connecter
            ssh_client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=30
            )
            
            # Ouvrir la session SFTP
            sftp = ssh_client.open_sftp()
            
            self.add_trace("Connexion SFTP établie")
            
            # Exécuter l'opération demandée
            if method == 'GET':
                self.add_trace(f"Téléchargement du fichier: {remote_path}")
                
                # Télécharger le fichier
                with sftp.file(remote_path, 'r') as remote_file:
                    file_content = remote_file.read().decode('utf-8', errors='replace')
                
                file_stats = sftp.stat(remote_path)
                
                self.set_code(0)
                self.add_trace(f"Fichier téléchargé avec succès ({file_stats.st_size} octets)")
                
                return self.get_result({
                    "content": file_content[:1000],  # Limiter la taille
                    "size": file_stats.st_size
                })
            
            elif method == 'PUT':
                self.add_trace(f"Upload du fichier vers: {remote_path}")
                
                # Uploader le fichier
                with sftp.file(remote_path, 'w') as remote_file:
                    remote_file.write(content.encode('utf-8'))
                
                self.set_code(0)
                self.add_trace(f"Fichier uploadé avec succès ({len(content)} octets)")
                
                return self.get_result({
                    "uploaded": True,
                    "size": len(content)
                })
            
            elif method == 'DELETE':
                self.add_trace(f"Suppression du fichier: {remote_path}")
                
                # Supprimer le fichier
                sftp.remove(remote_path)
                
                self.set_code(0)
                self.add_trace("Fichier supprimé avec succès")
                
                return self.get_result({"deleted": True})
            
            elif method == 'LIST':
                self.add_trace(f"Liste des fichiers dans: {remote_path}")
                
                # Lister les fichiers
                files = sftp.listdir(remote_path)
                
                # Obtenir des détails pour chaque fichier
                file_details = []
                for filename in files[:50]:  # Limiter à 50 fichiers
                    try:
                        full_path = f"{remote_path.rstrip('/')}/{filename}"
                        stats = sftp.stat(full_path)
                        file_details.append({
                            "name": filename,
                            "size": stats.st_size,
                            "is_dir": paramiko.sftp_attr.S_ISDIR(stats.st_mode)
                        })
                    except:
                        file_details.append({"name": filename})
                
                self.set_code(0)
                self.add_trace(f"Liste récupérée ({len(files)} entrées)")
                
                return self.get_result({
                    "files": file_details,
                    "count": len(files)
                })
            
            else:
                self.set_code(1)
                self.add_trace(f"Méthode SFTP non supportée: {method}")
                return self.get_result()
        
        except paramiko.AuthenticationException:
            self.set_code(1)
            self.add_trace("Erreur d'authentification SFTP")
            return self.get_result()
        
        except paramiko.SSHException as e:
            self.set_code(1)
            self.add_trace(f"Erreur SSH: {str(e)}")
            return self.get_result()
        
        except IOError as e:
            self.set_code(1)
            self.add_trace(f"Erreur d'entrée/sortie: {str(e)}")
            return self.get_result()
        
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur inattendue: {str(e)}")
            return self.get_result()
        
        finally:
            if sftp:
                try:
                    sftp.close()
                    self.add_trace("Session SFTP fermée")
                except:
                    pass
            
            if ssh_client:
                try:
                    ssh_client.close()
                except:
                    pass
