"""Module pour l'exécution d'un test individuel en arrière-plan."""
import time
from datetime import datetime
from pathlib import Path
from bson import ObjectId
from models.test import Test
from models.campain import Campain
from models.variable import Variable
from plugins.plugin_manager import PluginManager
from plugins.actions.action_base import ActionBase
from utils.workdir import get_campain_workdir
import traceback
import re

class TestExecutor:
    """Classe pour exécuter un test individuel."""
    
    def __init__(self, socketio):
        """Initialise l'exécuteur de test."""
        self.socketio = socketio
        self.plugin_manager = PluginManager('actions', ActionBase)
        # Charger les plugins d'actions
        self.plugin_manager.discover_plugins()
    
    def execute_test(self, test_id, filiere):
        """
        Exécute un test individuel en arrière-plan.
        
        Args:
            test_id: ID du test à exécuter
            filiere: Filière/environnement sélectionné
        """
        # Lancer l'exécution dans un thread séparé
        import threading
        thread = threading.Thread(
            target=self._run_test,
            args=(test_id, filiere)
        )
        thread.daemon = True
        thread.start()
    
    def _run_test(self, test_id, filiere):
        """Exécute le test."""
        try:
            # Attendre un court instant pour que le client rejoigne la room WebSocket
            time.sleep(0.5)
            
            # Émettre l'événement de démarrage
            self.socketio.emit('test_started', {
                'test_id': test_id,
                'status': 'running'
            }, room=f'test_{test_id}')
            
            print(f"[TestExecutor] Émission de test_started pour test {test_id} dans room test_{test_id}")
            
            # Récupérer le test
            test = Test.find_by_id(test_id)
            if not test:
                self.socketio.emit('test_log', {
                    'test_id': test_id,
                    'log': f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Test introuvable"
                }, room=f'test_{test_id}')
                
                self.socketio.emit('test_completed', {
                    'test_id': test_id,
                    'status': 'failed'
                }, room=f'test_{test_id}')
                return
            
            # Récupérer la campagne
            campain_id = str(test.get('campainId'))
            campain = Campain.find_by_id(campain_id)
            if not campain:
                self.socketio.emit('test_log', {
                    'test_id': test_id,
                    'log': f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Campagne introuvable"
                }, room=f'test_{test_id}')
                
                self.socketio.emit('test_completed', {
                    'test_id': test_id,
                    'status': 'failed'
                }, room=f'test_{test_id}')
                return
            
            # Charger les variables TestGyver
            variables = Variable.get_by_filiere(filiere)
            variables_dict = {var['key']: var['value'] for var in variables if not var.get('isRoot', False)}
            
            # Ajouter les variables de collection
            workdir = get_campain_workdir(campain_id)
            files_dir = str(Path(workdir) / 'files')
            work_dir = str(Path(workdir) / 'work')
            
            variables_dict['test.test_id'] = test_id
            variables_dict['test.campain_id'] = campain_id
            variables_dict['test.files_dir'] = files_dir
            variables_dict['test.work_dir'] = work_dir
            
            # Variables de sortie du test
            test_variables = {}
            if 'variables' in test:
                for var_name in test['variables']:
                    test_variables['app.' + var_name] = None
            
            # Émettre le log de démarrage
            self.socketio.emit('test_log', {
                'test_id': test_id,
                'log': f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Démarrage du test"
            }, room=f'test_{test_id}')
            
            print(f"[TestExecutor] Émission de test_log (Démarrage) pour test {test_id}")
            
            self.socketio.emit('test_log', {
                'test_id': test_id,
                'log': f"[{datetime.now().strftime('%H:%M:%S')}] 📂 Environnement: {filiere}"
            }, room=f'test_{test_id}')
            
            print(f"[TestExecutor] Émission de test_log (Environnement) pour test {test_id}")
            
            # Exécuter chaque action
            actions = test.get('actions', [])
            status = 'passed'
            
            for action_index, action_data in enumerate(actions):
                action_type = action_data.get('type')
                action_value = action_data.get('value', {})
                
                self.socketio.emit('test_log', {
                    'test_id': test_id,
                    'log': "--------------------------------"
                }, room=f'test_{test_id}')
                
                self.socketio.emit('test_log', {
                    'test_id': test_id,
                    'log': f"[{datetime.now().strftime('%H:%M:%S')}] 🔧 Exécution de l'action {action_index + 1}/{len(actions)}: {action_type}"
                }, room=f'test_{test_id}')
                
                # Remplacer les variables dans les valeurs de l'action
                resolved_value = self._resolve_variables(action_value, variables_dict, test_variables)
                
                # Charger le plugin d'action
                action_plugin = self.plugin_manager.get_plugin(action_type)
                if not action_plugin:
                    self.socketio.emit('test_log', {
                        'test_id': test_id,
                        'log': f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Plugin d'action '{action_type}' non trouvé"
                    }, room=f'test_{test_id}')
                    status = 'failed'
                    break
                
                # Exécuter l'action
                try:
                    result = action_plugin.execute(resolved_value,test_variables)
                    
                    if result.get('result'):
                        self.socketio.emit('test_log', {
                            'test_id': test_id,
                            'log': f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Action réussie"
                        }, room=f'test_{test_id}')
                        
                        # Ajouter les traces de l'action si présentes
                        if result.get('traces'):
                            for trace in result['traces']:
                                self.socketio.emit('test_log', {
                                    'test_id': test_id,
                                    'log': f"[{datetime.now().strftime('%H:%M:%S')}] 📋 {trace}"
                                }, room=f'test_{test_id}')

                        # Récupérer les variables de sortie si output_mapping est défini
                        output_mapping = action_value.get('output_mapping', {})
                        if output_mapping:
                            output_values = result.get('output_variables', {})
                            
                            # Pour chaque mapping défini (nom_sortie_plugin -> nom_variable_test)
                            for plugin_var_name, test_var_name in output_mapping.items():
                                if plugin_var_name in output_values:
                                    # Stocker la variable de sortie avec le préfixe app.
                                    full_var_name = f"app.{test_var_name}"
                                    test_variables[full_var_name] = output_values[plugin_var_name]
                                    self.socketio.emit('test_log', {
                                        'test_id': test_id,
                                        'log': f"[{datetime.now().strftime('%H:%M:%S')}] 📝 Variable '{test_var_name}' = {output_values[plugin_var_name]}"
                                    }, room=f'test_{test_id}')
                    else:
                        self.socketio.emit('test_log', {
                            'test_id': test_id,
                            'log': f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Action échouée: {result.get('message', 'Erreur inconnue')}"
                        }, room=f'test_{test_id}')
                        
                        # Ajouter les traces même en cas d'échec
                        if result.get('traces'):
                            for trace in result['traces']:
                                self.socketio.emit('test_log', {
                                    'test_id': test_id,
                                    'log': f"[{datetime.now().strftime('%H:%M:%S')}] 📋 {trace}"
                                }, room=f'test_{test_id}')
                        status = 'failed'
                        break
                
                except Exception as e:
                    error_trace = traceback.format_exc()
                    self.socketio.emit('test_log', {
                        'test_id': test_id,
                        'log': f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erreur lors de l'exécution: {str(e)}"
                    }, room=f'test_{test_id}')
                    
                    self.socketio.emit('test_log', {
                        'test_id': test_id,
                        'log': f"[{datetime.now().strftime('%H:%M:%S')}] 📋 Trace:\n{error_trace}"
                    }, room=f'test_{test_id}')
                    status = 'failed'
                    break
            
            # Émettre le log de fin
            if status == 'passed':
                self.socketio.emit('test_log', {
                    'test_id': test_id,
                    'log': f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Test terminé avec succès"
                }, room=f'test_{test_id}')
            else:
                self.socketio.emit('test_log', {
                    'test_id': test_id,
                    'log': f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Test échoué"
                }, room=f'test_{test_id}')
            
            # Émettre l'événement de fin
            self.socketio.emit('test_completed', {
                'test_id': test_id,
                'status': status
            }, room=f'test_{test_id}')
            
        except Exception as e:
            # En cas d'erreur
            error_msg = f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erreur critique: {str(e)}\n{traceback.format_exc()}"
            
            self.socketio.emit('test_log', {
                'test_id': test_id,
                'log': error_msg
            }, room=f'test_{test_id}')
            
            self.socketio.emit('test_completed', {
                'test_id': test_id,
                'status': 'failed'
            }, room=f'test_{test_id}')
    
    def _resolve_variables(self, value, variables_dict, test_variables):
        """
        Remplace les variables dans une valeur.
        
        Args:
            value: Valeur à traiter (peut être string, dict, list)
            variables_dict: Dictionnaire des variables TestGyver et collection
            test_variables: Dictionnaire des variables du test
        
        Returns:
            Valeur avec les variables remplacées
        """
        if isinstance(value, str):
            # Remplacer les variables TestGyver {{variable_name}}
            def replace_testgyver(match):
                var_name = match.group(1)
                return str(variables_dict.get(var_name, match.group(0)))
            
            # Remplacer les variables de test {{app.variable_name}}
            def replace_test(match):
                var_name = match.group(1)
                full_key = f"app.{var_name}"
                return str(test_variables.get(full_key, match.group(0)))
            
            # Remplacer les variables de collection {{test.variable_name}}
            def replace_collection(match):
                var_name = match.group(1)
                full_key = f"test.{var_name}"
                return str(variables_dict.get(full_key, match.group(0)))
            
            value = re.sub(r'\{\{([^.}]+)\}\}', replace_testgyver, value)
            value = re.sub(r'\{\{app\.([^}]+)\}\}', replace_test, value)
            value = re.sub(r'\{\{test\.([^}]+)\}\}', replace_collection, value)
            
            return value
        
        elif isinstance(value, dict):
            return {k: self._resolve_variables(v, variables_dict, test_variables) for k, v in value.items()}
        
        elif isinstance(value, list):
            return [self._resolve_variables(v, variables_dict, test_variables) for v in value]
        
        else:
            return value
