"""Action pour effectuer des opérations FTP."""
from ftplib import FTP, error_perm, error_temp
import io
import socket
from plugins.actions.action_base import ActionBase


class FTPAction(ActionBase):
    """Action pour effectuer des opérations FTP sur un serveur distant."""
    
    # Métadonnées du plugin
    plugin_name = "ftp"
    label = "FTP"
    version = "1.0.0"
    author = "TestGyver Team"
    color = "#fd7e14"
    
    def get_metadata(self):
        """Retourne les métadonnées de l'action."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Effectue des opérations FTP sur un serveur distant",
            "color": self.color
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
            },
            {
                "name": "local_path",
                "type": "string",
                "label": "Chemin local",
                "placeholder": "{{test.files_dir}}/mac.jpg",
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

    def get_js_show_form(self):
        """
        Retourne le code JavaScript à exécuter lors de l'affichage du formulaire.
        actionConfig est automatiquement disponible comme paramètre.
        """
        return """
// Récupérer le TestActionsManager

const manager = window.testActionsManager;

// Afficher/masquer les champs selon la méthode FTP sélectionnée
const methodSelect = document.getElementById('method');
if (methodSelect && manager) {
    // Fonction pour gérer l'affichage des champs
    const updateFieldsVisibility = () => {
        const method = methodSelect.value;
        
        // Par défaut, tout masquer sauf les champs communs
        manager.hideFields(['content', 'local_path']);
        
        // Afficher les champs selon la méthode
        if (method === 'GET') {
            manager.showFields(['remote_path', 'local_path']);
            manager.hideFields(['content']);
        } else if (method === 'PUT') {
            manager.showFields(['remote_path', 'content', 'local_path']);
        } else if (method === 'DELETE') {
            manager.showFields(['remote_path']);
            manager.hideFields(['content', 'local_path']);
        } else if (method === 'LIST') {
            manager.showFields(['remote_path']);
            manager.hideFields(['content', 'local_path']);
        }
    };
    
    // Appliquer lors du changement de méthode
    methodSelect.addEventListener('change', updateFieldsVisibility);
    
    // Appliquer immédiatement si une méthode est déjà sélectionnée
    if (actionConfig?.method) {
        updateFieldsVisibility();
    }
}
"""

    def get_js_validate_form(self):
        """
        Retourne le code JavaScript à exécuter lors de la validation du formulaire.
        Cette fonction valide que la variable sélectionnée existe dans les variables du test.
        """
        return """
// Fonction appelée lors de la validation du formulaire
console.log('FtpAction: jsValidateForm appelée', actionConfig, variables);

// Tout est OK
return {
    isValid: true,
    errorMessage: ''
};
"""
    
    def execute(self, action_context, test_variables=None):
        """
        Exécute une opération FTP.
        
        Args:
            action_context: Dictionnaire contenant method, host, port, username, password, remote_path, content
        """
        ftp = None
        
        try:
            method = action_context.get('method', 'GET').upper()
            host = action_context.get('host', '').strip()
            port = int(action_context.get('port', 21))
            username = action_context.get('username', '').strip()
            password = action_context.get('password', '')
            remote_path = action_context.get('remote_path', '').strip()
            content = action_context.get('content', '')
            file_content = action_context.get('file_content', '').strip()
            
            # Vérifier que l'hôte n'est pas vide
            if not host:
                raise ValueError("L'hôte FTP ne peut pas être vide")
            
            # Vérifier la résolution DNS
            try:
                self.add_trace(f"Vérification DNS pour: {host}")
                ip = socket.gethostbyname(host)
                self.add_trace(f"Hôte résolu: {host} -> {ip}")
            except socket.gaierror as e:
                raise OSError(f"Impossible de résoudre l'hôte '{host}'. Vérifiez le nom d'hôte ou utilisez une adresse IP.") from e
            
            # recupere le contenu du fichier si file_content est fourni
            if file_content:
                with open(file_content, 'rb') as f:
                    content = f.read()
            
            self.add_trace(f"Connexion FTP à {host}:{port}")
            self.add_trace(f"Tentative de résolution DNS pour: {host}")
            
            # Connexion au serveur FTP
            ftp = FTP()
            ftp.connect(host, port, timeout=30)
            self.add_trace(f"Connexion TCP établie, authentification en cours...")
            ftp.login(username, password)
            
            self.add_trace(f"Connexion établie - Message de bienvenue: {ftp.getwelcome()}")
            
            # Exécuter l'opération demandée
            if method == 'GET':
                if not remote_path:
                    raise ValueError("Le chemin distant (remote_path) est obligatoire pour l'opération GET")
                
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
                
                return self.get_result(True, output_vars)
            
            elif method == 'PUT':
                if not remote_path:
                    raise ValueError("Le chemin distant (remote_path) est obligatoire pour l'opération PUT")
                
                self.add_trace(f"Upload du fichier vers: {remote_path}")
                
                # Uploader le fichier
                # Si content est une chaîne, l'encoder en bytes, sinon l'utiliser tel quel
                if isinstance(content, str):
                    data = io.BytesIO(content.encode('utf-8'))
                    file_size = len(content.encode('utf-8'))
                else:
                    data = io.BytesIO(content)
                    file_size = len(content)
                
                ftp.storbinary(f'STOR {remote_path}', data)
                
                # Préparer les variables de sortie
                output_vars = {
                    "ftp_file_content": "",
                    "ftp_file_size": file_size,
                    "ftp_file_list": "",
                    "ftp_operation_success": "true"
                }
                
                self.set_code(0)
                self.add_trace(f"Fichier uploadé avec succès ({file_size} octets)")
                
                return self.get_result(True, output_vars)
            
            elif method == 'DELETE':
                if not remote_path:
                    raise ValueError("Le chemin distant (remote_path) est obligatoire pour l'opération DELETE")
                
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
                
                return self.get_result(True, output_vars)
            
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

                return self.get_result(True, output_vars)
            
            else:
                self.set_code(1)
                self.add_trace(f"Méthode FTP non supportée: {method}")
                return self.get_result()
        
        except ValueError as e:
            self.set_code(1)
            self.add_trace(f"Erreur de configuration: {str(e)}")
            return self.get_result(False, None)
        
        except error_perm as e:
            self.set_code(1)
            self.add_trace(f"Erreur de permission FTP: {str(e)}")
            return self.get_result(False, None)
        
        except error_temp as e:
            self.set_code(1)
            self.add_trace(f"Erreur temporaire FTP: {str(e)}")
            return self.get_result( False, None )
        
        except OSError as e:
            self.set_code(1)
            error_msg = f"Erreur réseau: {str(e)}"
            if e.errno == -2 or "Name or service not known" in str(e):
                error_msg += f" - Impossible de résoudre l'hôte '{action_context.get('host')}'. Vérifiez le nom d'hôte ou l'adresse IP."
            self.add_trace(error_msg)
            return self.get_result(False, None)
        
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur inattendue: {str(e)} (type: {type(e).__name__})")
            return self.get_result( False, None )
        
        finally:
            if ftp:
                try:
                    ftp.quit()
                    self.add_trace("Connexion FTP fermée")
                except:
                    pass
