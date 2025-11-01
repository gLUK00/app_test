"""Action pour effectuer des opérations d'entrée/sortie sur le système de fichiers."""
import os
import shutil
from pathlib import Path
from plugins.actions.action_base import ActionBase


class IoAction(ActionBase):
    """Action pour effectuer des opérations d'I/O sur le système de fichiers."""
    
    # Métadonnées du plugin
    plugin_name = "io"
    label = "I/O (Fichiers)"
    version = "1.0.0"
    author = "TestGyver Team"
    
    def get_metadata(self):
        """Retourne les métadonnées de l'action."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Effectue des opérations d'entrée/sortie sur le système de fichiers"
        }
    
    def validate_config(self, config):
        """Valide la configuration de l'action."""
        required_fields = ['operation', 'path']
        for field in required_fields:
            if field not in config or not config[field]:
                return (False, f"Le champ '{field}' est obligatoire")
        
        # Vérifier que l'opération est valide
        valid_operations = ['create_dir', 'delete_dir', 'delete_file', 'write_variable', 'read_variable', 'list_files']
        if config['operation'] not in valid_operations:
            return (False, f"Opération invalide. Valeurs acceptées : {', '.join(valid_operations)}")
        
        # Vérifier que variable_value est fourni pour write_variable et read_variable
        if config['operation'] in ['write_variable', 'read_variable']:
            if 'variable_value' not in config or not config['variable_value']:
                return (False, "Le champ 'variable_value' est obligatoire pour cette opération")

        return (True, "")
    
    def get_input_mask(self):
        """Retourne le masque de saisie pour les opérations I/O."""
        return [
            {
                "name": "operation",
                "type": "select",
                "label": "Opération",
                "options": ["create_dir", "delete_dir", "delete_file", "write_variable", "read_variable", "list_files"],
                "required": True
            },
            {
                "name": "path",
                "type": "string",
                "label": "Chemin",
                "placeholder": "Chemin du répertoire ou du fichier",
                "required": True
            },
            {
                "name": "variable_value",
                "type": "textarea",
                "label": "Contenu du fichier",
                "placeholder": "Contenu à écrire (pour write_variable)",
                "required": False
            },
            {
                "name": "file_extension",
                "type": "string",
                "label": "Extension de fichier",
                "placeholder": "Ex: .txt, .json (pour list_files)",
                "required": False
            }
        ]
    
    def get_output_variables(self):
        """Retourne la liste des variables de sortie pour les opérations I/O."""
        return [
            {
                "name": "file_list",
                "description": "Liste des fichiers trouvés (pour list_files)"
            },
            {
                "name": "file_content",
                "description": "Contenu du fichier lu (pour read_variable)"
            }
        ]
    
    def execute(self, action_context):
        """
        Exécute une opération I/O.
        
        Args:
            action_context: Dictionnaire contenant operation, path, file_extension
        """
        try:
            operation = action_context.get('operation')
            path = action_context.get('path')
            variable_value = action_context.get('variable_value', '')
            file_extension = action_context.get('file_extension', '')
            
            self.add_trace(f"Préparation de l'opération I/O {operation} sur {path}")
            
            if operation == "create_dir":
                return self._create_directory(path)
            
            elif operation == "delete_dir":
                return self._delete_directory(path)
            
            elif operation == "delete_file":
                return self._delete_file(path)
            
            elif operation == "write_variable":
                return self._write_variable(path, variable_value)
            
            elif operation == "read_variable":
                return self._read_variable(path)
            
            elif operation == "list_files":
                return self._list_files(path, file_extension)
            
            else:
                raise ValueError(f"Opération I/O inconnue: {operation}")
        
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur inattendue: {str(e)}")
            return self.get_result(False, None)
    
    def _create_directory(self, path):
        """Crée un répertoire."""
        try:
            os.makedirs(path, exist_ok=True)
            self.add_trace(f"Répertoire créé: {path}")
            return self.get_result(True, None)
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur lors de la création du répertoire: {str(e)}")
            return self.get_result(False, None)
    
    def _delete_directory(self, path):
        """Supprime un répertoire et tout son contenu."""
        try:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    self.add_trace(f"Répertoire supprimé: {path}")
                else:
                    self.add_trace(f"Le chemin n'est pas un répertoire: {path}")
                    self.set_code(1)
                    return self.get_result(False, None)
            else:
                self.add_trace(f"Le répertoire n'existe pas: {path}")
            
            return self.get_result(True, None)
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur lors de la suppression du répertoire: {str(e)}")
            return self.get_result(False, None)
    
    def _delete_file(self, path):
        """Supprime un fichier."""
        try:
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                    self.add_trace(f"Fichier supprimé: {path}")
                else:
                    self.add_trace(f"Le chemin n'est pas un fichier: {path}")
                    self.set_code(1)
                    return self.get_result(False, None)
            else:
                self.add_trace(f"Le fichier n'existe pas: {path}")
            
            return self.get_result(True, None)
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur lors de la suppression du fichier: {str(e)}")
            return self.get_result(False, None)
    
    def _write_variable(self, path, content):
        """Écrit une variable dans un fichier."""
        try:
            # Créer le répertoire parent si nécessaire
            parent_dir = os.path.dirname(path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            
            # Écrire le contenu dans le fichier
            with open(path, 'w', encoding='utf-8') as f:
                f.write(str(content))
            
            self.add_trace(f"Variable écrite dans le fichier: {path}")
            return self.get_result(True, None)
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur lors de l'écriture du fichier: {str(e)}")
            return self.get_result(False, None)
    
    def _read_variable(self, path):
        """Lit le contenu d'un fichier."""
        try:
            if not os.path.exists(path):
                self.add_trace(f"Le fichier n'existe pas: {path}")
                self.set_code(1)
                return self.get_result(False, None)
            
            if not os.path.isfile(path):
                self.add_trace(f"Le chemin n'est pas un fichier: {path}")
                self.set_code(1)
                return self.get_result(False, None)
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.add_trace(f"Contenu lu depuis le fichier: {path}")
            return self.get_result(True, {"file_content": content})
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur lors de la lecture du fichier: {str(e)}")
            return self.get_result(False, None)
    
    def _list_files(self, path, file_extension=''):
        """Liste les fichiers dans un répertoire avec filtrage optionnel par extension."""
        try:
            if not os.path.exists(path):
                self.add_trace(f"Le répertoire n'existe pas: {path}")
                self.set_code(1)
                return self.get_result(False, None)
            
            if not os.path.isdir(path):
                self.add_trace(f"Le chemin n'est pas un répertoire: {path}")
                self.set_code(1)
                return self.get_result(False, None)
            
            # Lister les fichiers
            files = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    # Filtrer par extension si spécifié
                    if file_extension:
                        # Normaliser l'extension (ajouter le point si nécessaire)
                        ext = file_extension if file_extension.startswith('.') else f'.{file_extension}'
                        if item.endswith(ext):
                            files.append(item)
                    else:
                        files.append(item)
            
            self.add_trace(f"Fichiers listés dans {path}: {len(files)} fichier(s) trouvé(s)")
            if file_extension:
                self.add_trace(f"Filtré par extension: {file_extension}")
            
            return self.get_result(True, {"file_list": files})
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur lors du listing des fichiers: {str(e)}")
            return self.get_result(False, None)
