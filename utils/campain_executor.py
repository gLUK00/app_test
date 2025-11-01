"""Module pour l'exécution des campagnes de tests en arrière-plan."""
import threading
from datetime import datetime
from pathlib import Path
from bson import ObjectId
from models.test import Test
from models.rapport import Rapport
from models.variable import Variable
from plugins.plugin_manager import PluginManager
from plugins.actions.action_base import ActionBase
from utils.workdir import get_campain_workdir
import traceback
import re

class CampainExecutor:
    """Classe pour exécuter une campagne de tests."""
    
    def __init__(self, socketio):
        """Initialise l'exécuteur de campagne."""
        self.socketio = socketio
        self.plugin_manager = PluginManager('actions', ActionBase)
        # Charger les plugins d'actions
        self.plugin_manager.discover_plugins()
    
    def execute_campain(self, rapport_id, campain_id, filiere, tests, stop_on_failure):
        """
        Exécute une campagne de tests en arrière-plan.
        
        Args:
            rapport_id: ID du rapport à mettre à jour
            campain_id: ID de la campagne
            filiere: Filière/environnement sélectionné
            tests: Liste des tests à exécuter
            stop_on_failure: Arrêter l'exécution au premier échec
        """
        # Lancer l'exécution dans un thread séparé
        thread = threading.Thread(
            target=self._run_campain,
            args=(rapport_id, campain_id, filiere, tests, stop_on_failure)
        )
        thread.daemon = True
        thread.start()
    
    def _run_campain(self, rapport_id, campain_id, filiere, tests, stop_on_failure):
        """Exécute la campagne de tests."""
        try:
            # Mettre à jour le statut à "running"
            Rapport.update(rapport_id, {
                'status': 'running',
                'progress': 0
            })
            
            # Émettre l'événement de démarrage
            self.socketio.emit('campain_started', {
                'rapport_id': rapport_id,
                'campain_id': campain_id
            }, room=f'rapport_{rapport_id}')
            
            # Récupérer les variables de l'environnement
            variables = Variable.get_by_filiere(filiere)
            variables_dict = {var['key']: var['value'] for var in variables}
            
            # Récupérer les chemins du workdir de la campagne
            campain_workdir = Path(get_campain_workdir(campain_id))
            files_dir = str(campain_workdir / "files")
            work_dir = str(campain_workdir / "work")
            
            # Ajouter les variables de collection
            variables_dict['test.test_id'] = None  # Sera mis à jour pour chaque test
            variables_dict['test.campain_id'] = campain_id
            variables_dict['test.files_dir'] = files_dir
            variables_dict['test.work_dir'] = work_dir
            
            total_tests = len(tests)
            executed_tests = []
            global_success = True
            
            for index, test_id in enumerate(tests):
                # Vérifier si on doit arrêter
                if stop_on_failure and not global_success:
                    # Marquer les tests restants comme "skipped"
                    for remaining_test_id in tests[index:]:
                        executed_tests.append({
                            'testId': ObjectId(remaining_test_id),
                            'status': 'skipped',
                            'logs': 'Test ignoré après un échec précédent'
                        })
                    break
                
                # Mettre à jour la variable test_id
                variables_dict['test.test_id'] = test_id
                
                # Émettre l'événement de démarrage du test
                self.socketio.emit('test_started', {
                    'rapport_id': rapport_id,
                    'test_id': test_id
                }, room=f'rapport_{rapport_id}')
                
                # Récupérer les variables du test
                test = Test.find_by_id(test_id)
                if 'variables' in test:
                    for var_name in test['variables']:
                        variables_dict['app.' + var_name] = None
                
                # Exécuter le test
                test_result = self._execute_test(test_id, variables_dict, filiere)
                executed_tests.append(test_result)
                
                # Vérifier le résultat
                if test_result['status'] != 'passed':
                    global_success = False
                
                # Mettre à jour la progression
                progress = int(((index + 1) / total_tests) * 100)
                Rapport.update(rapport_id, {
                    'progress': progress,
                    'tests': executed_tests
                })
                
                # Émettre l'événement de progression
                self.socketio.emit('test_completed', {
                    'rapport_id': rapport_id,
                    'test_id': test_id,
                    'status': test_result['status'],
                    'logs': test_result['logs']
                }, room=f'rapport_{rapport_id}')
                
                self.socketio.emit('campain_progress', {
                    'rapport_id': rapport_id,
                    'progress': progress
                }, room=f'rapport_{rapport_id}')
            
            # Finaliser le rapport
            final_status = 'completed' if global_success else 'failed'
            final_result = 'success' if global_success else 'failure'
            
            Rapport.update(rapport_id, {
                'status': final_status,
                'result': final_result,
                'progress': 100,
                'tests': executed_tests
            })
            
            # Émettre l'événement de fin
            self.socketio.emit('campain_completed', {
                'rapport_id': rapport_id,
                'status': final_status,
                'result': final_result
            }, room=f'rapport_{rapport_id}')
            
        except Exception as e:
            # En cas d'erreur, mettre à jour le rapport
            error_msg = f"Erreur lors de l'exécution: {str(e)}\n{traceback.format_exc()}"
            
            Rapport.update(rapport_id, {
                'status': 'failed',
                'result': 'failure',
                'details': error_msg
            })
            
            self.socketio.emit('campain_error', {
                'rapport_id': rapport_id,
                'error': error_msg
            }, room=f'rapport_{rapport_id}')
    
    def _execute_test(self, test_id, variables_dict, filiere):
        """
        Exécute un test individuel.
        
        Args:
            test_id: ID du test à exécuter
            variables_dict: Dictionnaire des variables disponibles
            filiere: Filière/environnement
        
        Returns:
            dict: Résultat de l'exécution du test
        """
        logs = []
        status = 'passed'
        
        try:
            # Récupérer le test
            test = Test.find_by_id(test_id)
            if not test:
                return {
                    'testId': ObjectId(test_id),
                    'status': 'failed',
                    'logs': 'Test introuvable'
                }
            
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Démarrage du test")
            
            # Variables de sortie du test
            test_variables = {}
            if 'variables' in test:
                for var_name in test['variables']:
                    test_variables['app.'+var_name] = None
            
            # Exécuter chaque action
            actions = test.get('actions', [])
            for action_index, action_data in enumerate(actions):
                action_type = action_data.get('type')
                action_value = action_data.get('value', {})
                
                logs.append( "--------------------------------" )
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Exécution de l'action {action_index + 1}/{len(actions)}: {action_type}")
                
                # Remplacer les variables dans les valeurs de l'action
                resolved_value = self._resolve_variables(action_value, variables_dict, test_variables)
                
                # Merge les variables de retour de l'action
                
                # Charger le plugin d'action
                action_plugin = self.plugin_manager.get_plugin(action_type)
                if not action_plugin:
                    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Plugin d'action '{action_type}' non trouvé")
                    status = 'failed'
                    break
                
                # Exécuter l'action
                try:
                    result = action_plugin.execute(resolved_value)
                    
                    if result.get('result'):
                        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Action réussie")
                        
                        # Ajouter les traces de l'action si présentes
                        if result.get('traces'):
                            for trace in result['traces']:
                                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📋 {trace}")

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
                                    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📝 Variable '{test_var_name}' = {output_values[plugin_var_name]}")
                    else:
                        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Action échouée: {result.get('message', 'Erreur inconnue')}")
                        # Ajouter les traces même en cas d'échec
                        if result.get('traces'):
                            for trace in result['traces']:
                                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📋 {trace}")
                        status = 'failed'
                        break
                
                except Exception as e:
                    error_trace = traceback.format_exc()
                    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erreur lors de l'exécution: {str(e)}")
                    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📋 Trace:\n{error_trace}")
                    status = 'failed'
                    break
            
            if status == 'passed':
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Test terminé avec succès")
            else:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Test échoué")
        
        except Exception as e:
            error_trace = traceback.format_exc()
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erreur: {str(e)}")
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📋 Trace:\n{error_trace}")
            status = 'failed'
        
        return {
            'testId': ObjectId(test_id),
            'status': status,
            'logs': '\n'.join(logs)
        }
    
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
