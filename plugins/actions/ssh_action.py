"""Action pour effectuer des commandes SSH."""
import paramiko
from plugins.actions.action_base import ActionBase

class SSHAction(ActionBase):
    """Action pour exécuter des commandes SSH sur un serveur distant."""
    
    def get_input_mask(self):
        """Retourne le masque de saisie pour les commandes SSH."""
        return [
            {
                "name": "host",
                "type": "string",
                "label": "Hôte",
                "placeholder": "192.168.1.100",
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
                "name": "command",
                "type": "textarea",
                "label": "Commande à exécuter",
                "placeholder": "ls -la /home",
                "required": True
            }
        ]
    
    def execute(self, action_context):
        """
        Exécute une commande SSH.
        
        Args:
            action_context: Dictionnaire contenant host, port, username, password, command
        """
        ssh_client = None
        
        try:
            host = action_context.get('host')
            port = int(action_context.get('port', 22))
            username = action_context.get('username')
            password = action_context.get('password')
            command = action_context.get('command')
            
            self.add_trace(f"Connexion SSH à {username}@{host}:{port}")
            
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
            
            self.add_trace("Connexion établie")
            self.add_trace(f"Exécution de la commande: {command}")
            
            # Exécuter la commande
            stdin, stdout, stderr = ssh_client.exec_command(command)
            
            # Lire les résultats
            output = stdout.read().decode('utf-8')
            error_output = stderr.read().decode('utf-8')
            exit_code = stdout.channel.recv_exit_status()
            
            self.add_trace(f"Code de sortie: {exit_code}")
            
            if exit_code == 0:
                self.set_code(0)
                self.add_trace("Commande exécutée avec succès")
                
                result_data = {
                    "exit_code": exit_code,
                    "output": output[:1000],  # Limiter la taille
                    "error": error_output[:500] if error_output else None
                }
                
                return self.get_result(result_data)
            else:
                self.set_code(1)
                self.add_trace(f"Erreur lors de l'exécution: {error_output}")
                
                return self.get_result({
                    "exit_code": exit_code,
                    "output": output[:500],
                    "error": error_output[:500]
                })
        
        except paramiko.AuthenticationException:
            self.set_code(1)
            self.add_trace("Erreur d'authentification: identifiants invalides")
            return self.get_result()
        
        except paramiko.SSHException as e:
            self.set_code(1)
            self.add_trace(f"Erreur SSH: {str(e)}")
            return self.get_result()
        
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur lors de l'exécution: {str(e)}")
            return self.get_result()
        
        finally:
            if ssh_client:
                ssh_client.close()
                self.add_trace("Connexion SSH fermée")
