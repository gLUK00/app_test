"""Action pour interagir avec un stockage compatible S3."""
import boto3
import json
import os
from botocore.exceptions import ClientError
from plugins.actions.action_base import ActionBase


class S3Action(ActionBase):
    """Action pour effectuer des opérations S3 (List, Upload, Download, Delete)."""
    
    # Métadonnées du plugin
    plugin_name = "s3"
    label = "S3 (Simple Storage Service)"
    version = "1.0.0"
    author = "TestGyver Team"
    
    def get_metadata(self):
        """Retourne les métadonnées de l'action."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Interagit avec un service de stockage compatible S3 (AWS, MinIO, etc.)"
        }
    
    def validate_config(self, config):
        """Valide la configuration de l'action."""
        if 'operation' not in config or not config['operation']:
            return (False, "L'opération est obligatoire")
        
        operation = config['operation']
        if operation in ['upload_file', 'download_file', 'delete_object', 'list_objects']:
            if 'bucket_name' not in config or not config['bucket_name']:
                return (False, "Le nom du bucket est obligatoire pour cette opération")
        
        if operation in ['upload_file', 'download_file', 'delete_object']:
            if 'object_key' not in config or not config['object_key']:
                return (False, "La clé de l'objet (chemin S3) est obligatoire pour cette opération")
                
        if operation == 'upload_file':
            if 'local_path' not in config or not config['local_path']:
                return (False, "Le chemin local du fichier est obligatoire pour l'upload")
                
        if operation == 'download_file':
            if 'local_path' not in config or not config['local_path']:
                return (False, "Le chemin local de destination est obligatoire pour le download")
                
        return (True, "")
    
    def get_input_mask(self):
        """Retourne le masque de saisie pour les opérations S3."""
        return [
            {
                "name": "endpoint_url",
                "type": "string",
                "label": "Endpoint URL (Optionnel)",
                "placeholder": "https://s3.amazonaws.com ou http://minio:9000",
                "required": False,
                "description": "Laisser vide pour AWS S3 par défaut"
            },
            {
                "name": "access_key",
                "type": "string",
                "label": "Access Key ID",
                "placeholder": "AKIAIOSFODNN7EXAMPLE",
                "required": True
            },
            {
                "name": "secret_key",
                "type": "string",
                "label": "Secret Access Key",
                "placeholder": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                "required": True
            },
            {
                "name": "region_name",
                "type": "string",
                "label": "Région (Optionnel)",
                "placeholder": "us-east-1",
                "required": False
            },
            {
                "name": "verify",
                "type": "string",
                "label": "Vérification SSL (verify)",
                "placeholder": "/path/to/cert.pem ou False",
                "required": False,
                "description": "Chemin vers le bundle CA ou 'False' pour désactiver la vérification SSL"
            },
            {
                "name": "operation",
                "type": "select",
                "label": "Opération",
                "options": [
                    {"value": "list_buckets", "label": "Lister les buckets"},
                    {"value": "list_objects", "label": "Lister les objets"},
                    {"value": "upload_file", "label": "Uploader un fichier"},
                    {"value": "download_file", "label": "Télécharger un fichier"},
                    {"value": "delete_object", "label": "Supprimer un objet"}
                ],
                "required": True
            },
            {
                "name": "bucket_name",
                "type": "string",
                "label": "Nom du Bucket",
                "placeholder": "my-bucket",
                "required": False,
                "description": "Requis pour toutes les opérations sauf 'Lister les buckets'"
            },
            {
                "name": "object_key",
                "type": "string",
                "label": "Clé de l'objet (Chemin S3)",
                "placeholder": "folder/file.txt",
                "required": False,
                "description": "Requis pour Upload, Download, Delete"
            },
            {
                "name": "local_path",
                "type": "string",
                "label": "Chemin local du fichier",
                "placeholder": "/tmp/file.txt",
                "required": False,
                "description": "Requis pour Upload (source) et Download (destination)"
            }
        ]
    
    def get_output_variables(self):
        """Retourne la liste des variables de sortie pour S3."""
        return [
            {
                "name": "s3_result",
                "description": "Résultat de l'opération (JSON string)",
                "type": "string"
            },
            {
                "name": "s3_success",
                "description": "Indique si l'opération a réussi (true/false)",
                "type": "boolean"
            }
        ]
    
    def execute(self, action_context, test_variables=None):
        """Exécute l'action S3."""
        self.code = 0
        self.traces = []
        
        # Récupération des paramètres
        endpoint_url = action_context.get('endpoint_url')
        access_key = action_context.get('access_key')
        secret_key = action_context.get('secret_key')
        region_name = action_context.get('region_name')
        verify = action_context.get('verify')
        operation = action_context.get('operation')
        bucket_name = action_context.get('bucket_name')
        object_key = action_context.get('object_key')
        local_path = action_context.get('local_path')
        
        # Configuration du client S3
        s3_config = {
            'service_name': 's3',
            'aws_access_key_id': access_key,
            'aws_secret_access_key': secret_key,
        }
        
        if endpoint_url:
            s3_config['endpoint_url'] = endpoint_url
        if region_name:
            s3_config['region_name'] = region_name
            
        # Gestion du paramètre verify (SSL)
        if verify:
            if verify.lower() == 'false':
                s3_config['verify'] = False
                self.add_trace("Vérification SSL désactivée.")
            elif verify.lower() == 'true':
                s3_config['verify'] = True
            else:
                s3_config['verify'] = verify
                self.add_trace(f"Utilisation du certificat CA : {verify}")
            
        self.add_trace(f"Connexion S3 vers {endpoint_url or 'AWS Default'}...")
        
        try:
            s3_client = boto3.client(**s3_config)
            result_data = {}
            
            if operation == 'list_buckets':
                self.add_trace("Listage des buckets...")
                response = s3_client.list_buckets()
                buckets = [bucket['Name'] for bucket in response['Buckets']]
                self.add_trace(f"Buckets trouvés: {', '.join(buckets)}")
                result_data = {"buckets": buckets}
                
            elif operation == 'list_objects':
                self.add_trace(f"Listage des objets dans le bucket '{bucket_name}'...")
                response = s3_client.list_objects_v2(Bucket=bucket_name)
                if 'Contents' in response:
                    objects = [obj['Key'] for obj in response['Contents']]
                    self.add_trace(f"{len(objects)} objets trouvés.")
                    result_data = {"objects": objects}
                else:
                    self.add_trace("Aucun objet trouvé.")
                    result_data = {"objects": []}
                    
            elif operation == 'upload_file':
                self.add_trace(f"Upload du fichier '{local_path}' vers '{bucket_name}/{object_key}'...")
                if not os.path.exists(local_path):
                    raise FileNotFoundError(f"Le fichier local '{local_path}' n'existe pas.")
                
                s3_client.upload_file(local_path, bucket_name, object_key)
                self.add_trace("Upload réussi.")
                result_data = {"status": "uploaded", "key": object_key}
                
            elif operation == 'download_file':
                self.add_trace(f"Téléchargement de '{bucket_name}/{object_key}' vers '{local_path}'...")
                # Création du répertoire parent si nécessaire
                os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)
                
                s3_client.download_file(bucket_name, object_key, local_path)
                self.add_trace("Téléchargement réussi.")
                result_data = {"status": "downloaded", "local_path": local_path}
                
            elif operation == 'delete_object':
                self.add_trace(f"Suppression de '{bucket_name}/{object_key}'...")
                s3_client.delete_object(Bucket=bucket_name, Key=object_key)
                self.add_trace("Suppression réussie.")
                result_data = {"status": "deleted", "key": object_key}
            
            else:
                self.code = 1
                self.add_trace(f"Opération inconnue: {operation}")
                return self.get_result(output_variables={"s3_success": False})

            return self.get_result(
                result_data=result_data,
                output_variables={
                    "s3_result": json.dumps(result_data),
                    "s3_success": True
                }
            )
            
        except ClientError as e:
            self.code = 1
            error_msg = f"Erreur S3: {e}"
            self.add_trace(error_msg)
            return self.get_result(output_variables={"s3_result": json.dumps({"error": str(e)}), "s3_success": False})
            
        except Exception as e:
            self.code = 1
            error_msg = f"Erreur inattendue: {str(e)}"
            self.add_trace(error_msg)
            return self.get_result(output_variables={"s3_result": json.dumps({"error": str(e)}), "s3_success": False})
