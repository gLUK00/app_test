"""Module pour l'exécution des tests de performance en arrière-plan."""
import threading
import time
import copy
import re
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from models.test import Test
from models.rapport import Rapport
from models.variable import Variable
from plugins.plugin_manager import PluginManager
from plugins.actions.action_base import ActionBase
from utils.workdir import get_campain_workdir


class PerformanceExecutor:
    """Exécuteur de tests de performance avec support du parallélisme."""

    def __init__(self, socketio):
        self.socketio = socketio
        self.plugin_manager = PluginManager('actions', ActionBase)
        self.plugin_manager.discover_plugins()

    # ------------------------------------------------------------------
    # Helpers SocketIO
    # ------------------------------------------------------------------

    def _emit(self, event, data, rapport_id):
        """Émet un événement vers la room du rapport de performance."""
        room = f'perf_{rapport_id}'
        try:
            self.socketio.emit(event, data, room=room)
        except Exception as exc:
            print(f"⚠️  Impossible d'émettre '{event}' vers {room}: {exc}")

    # ------------------------------------------------------------------
    # Lancement en arrière-plan
    # ------------------------------------------------------------------

    def execute_performance(self, rapport_id, campain_id, filiere, perf_config):
        """Lance l'exécution du test de performance dans un thread dédié."""
        thread = threading.Thread(
            target=self._run_performance,
            kwargs={
                'rapport_id': rapport_id,
                'campain_id': campain_id,
                'filiere': filiere,
                'perf_config': perf_config,
            }
        )
        thread.daemon = True
        thread.start()
        print(f"✅ Test de performance lancé pour rapport {rapport_id}")

    # ------------------------------------------------------------------
    # Exécution principale
    # ------------------------------------------------------------------

    def _run_performance(self, rapport_id, campain_id, filiere, perf_config):
        """Exécute le test de performance (dans un thread)."""
        start_time = time.time()

        try:
            time.sleep(0.2)  # Laisse le client rejoindre la room WebSocket

            Rapport.update(rapport_id, {
                'status': 'running',
                'progress': 0,
                'startTime': start_time
            })

            self._emit('perf_started', {
                'rapport_id': rapport_id,
                'campain_id': campain_id
            }, rapport_id)

            # Variables de base
            variables = Variable.get_by_filiere(filiere)
            variables_base = {var['key']: var['value'] for var in variables}

            campain_workdir = Path(get_campain_workdir(campain_id))
            variables_base['test.campain_id'] = campain_id
            variables_base['test.files_dir'] = str(campain_workdir / 'files')
            variables_base['test.work_dir'] = str(campain_workdir / 'work')

            tests_config = perf_config.get('tests', [])
            tests_parallel = perf_config.get('tests_parallel', False)
            tests_parallel_count = max(1, int(perf_config.get('tests_parallel_count', 2)))
            timeout_override = perf_config.get('timeout_override')

            total_instances = sum(int(tc.get('instances', 1)) for tc in tests_config)

            # Initialisation des résultats
            perf_results = {
                'total_instances': total_instances,
                'executed_instances': 0,
                'passed_instances': 0,
                'failed_instances': 0,
                'exec_time_avg_ms': 0,
                'exec_time_min_ms': None,
                'exec_time_max_ms': 0,
                'exec_time_total_ms': 0,
                'tests': []
            }

            for tc in tests_config:
                test_id = tc.get('test_id')
                test_doc = Test.find_by_id(test_id)
                n = int(tc.get('instances', 1))
                perf_results['tests'].append({
                    'test_id': test_id,
                    'name': (test_doc.get('name', test_id) if test_doc else test_id),
                    'total_instances': n,
                    'executed_instances': 0,
                    'passed_instances': 0,
                    'failed_instances': 0,
                    'exec_time_avg_ms': 0,
                    'exec_time_min_ms': None,
                    'exec_time_max_ms': 0,
                    'exec_time_total_ms': 0,
                    '_instance_times': []  # temporaire pour calculs
                })

            Rapport.update_perf_results(rapport_id, perf_results)

            lock = threading.Lock()

            # ----------------------------------------------------------
            # Callback mis à jour après chaque instance
            # ----------------------------------------------------------
            def on_instance_done(result, test_result_entry):
                exec_time = result.get('executionTimeMs', 0)
                passed = result.get('status') == 'passed'

                with lock:
                    # Stats du test
                    test_result_entry['executed_instances'] += 1
                    if passed:
                        test_result_entry['passed_instances'] += 1
                    else:
                        test_result_entry['failed_instances'] += 1

                    test_result_entry['_instance_times'].append(exec_time)
                    test_result_entry['exec_time_total_ms'] += exec_time
                    times = test_result_entry['_instance_times']
                    test_result_entry['exec_time_avg_ms'] = int(sum(times) / len(times))
                    if test_result_entry['exec_time_min_ms'] is None or exec_time < test_result_entry['exec_time_min_ms']:
                        test_result_entry['exec_time_min_ms'] = exec_time
                    if exec_time > test_result_entry['exec_time_max_ms']:
                        test_result_entry['exec_time_max_ms'] = exec_time

                    # Stats globales
                    perf_results['executed_instances'] += 1
                    if passed:
                        perf_results['passed_instances'] += 1
                    else:
                        perf_results['failed_instances'] += 1

                    perf_results['exec_time_total_ms'] += exec_time
                    if perf_results['exec_time_min_ms'] is None or exec_time < perf_results['exec_time_min_ms']:
                        perf_results['exec_time_min_ms'] = exec_time
                    if exec_time > perf_results['exec_time_max_ms']:
                        perf_results['exec_time_max_ms'] = exec_time
                    if perf_results['executed_instances'] > 0:
                        perf_results['exec_time_avg_ms'] = int(
                            perf_results['exec_time_total_ms'] / perf_results['executed_instances']
                        )

                    progress = int(
                        (perf_results['executed_instances'] / total_instances) * 100
                    ) if total_instances > 0 else 0

                    # Persistance
                    Rapport.update_perf_results(rapport_id, perf_results)
                    Rapport.update(rapport_id, {'progress': progress})

                    # Événement temps réel
                    self._emit('perf_stats_updated', {
                        'rapport_id': rapport_id,
                        'progress': progress,
                        'global': _serialize_global(perf_results),
                        'tests': [_serialize_test(tr) for tr in perf_results['tests']]
                    }, rapport_id)

            # ----------------------------------------------------------
            # Exécution des instances d'un test
            # ----------------------------------------------------------
            def execute_test_instances(tc, test_result_entry):
                n = int(tc.get('instances', 1))
                parallel = tc.get('parallel', False) and n > 1
                parallel_count = max(1, int(tc.get('parallel_count', 2)))
                stop_on_failure = tc.get('stop_on_instance_failure', False)
                test_id = tc.get('test_id')

                if parallel:
                    with ThreadPoolExecutor(max_workers=parallel_count) as pool:
                        futures = []
                        for i in range(n):
                            vars_copy = copy.deepcopy(variables_base)
                            vars_copy['test.test_id'] = test_id
                            futures.append(
                                pool.submit(
                                    self._execute_test_instance,
                                    test_id, vars_copy, i + 1, timeout_override
                                )
                            )
                        for future in as_completed(futures):
                            on_instance_done(future.result(), test_result_entry)
                else:
                    for i in range(n):
                        if stop_on_failure and test_result_entry['failed_instances'] > 0:
                            # Compter les instances non exécutées comme "skipped"
                            remaining = n - i
                            with lock:
                                perf_results['executed_instances'] += remaining
                                progress = int(
                                    (perf_results['executed_instances'] / total_instances) * 100
                                ) if total_instances > 0 else 0
                                Rapport.update(rapport_id, {'progress': progress})
                                self._emit('perf_stats_updated', {
                                    'rapport_id': rapport_id,
                                    'progress': progress,
                                    'global': _serialize_global(perf_results),
                                    'tests': [_serialize_test(tr) for tr in perf_results['tests']]
                                }, rapport_id)
                            break

                        vars_copy = copy.deepcopy(variables_base)
                        vars_copy['test.test_id'] = test_id
                        result = self._execute_test_instance(test_id, vars_copy, i + 1, timeout_override)
                        on_instance_done(result, test_result_entry)

            # ----------------------------------------------------------
            # Lancement des tests (parallèle ou séquentiel)
            # ----------------------------------------------------------
            if tests_parallel:
                with ThreadPoolExecutor(max_workers=tests_parallel_count) as pool:
                    futures = [
                        pool.submit(execute_test_instances, tc, perf_results['tests'][i])
                        for i, tc in enumerate(tests_config)
                    ]
                    for future in as_completed(futures):
                        future.result()  # propage les exceptions
            else:
                for i, tc in enumerate(tests_config):
                    execute_test_instances(tc, perf_results['tests'][i])

            # ----------------------------------------------------------
            # Finalisation
            # ----------------------------------------------------------
            end_time = time.time()
            exec_time_ms = int((end_time - start_time) * 1000)

            # Nettoyage des données temporaires
            for tr in perf_results['tests']:
                tr.pop('_instance_times', None)
                if tr['exec_time_min_ms'] is None:
                    tr['exec_time_min_ms'] = 0

            if perf_results['exec_time_min_ms'] is None:
                perf_results['exec_time_min_ms'] = 0

            all_passed = perf_results['failed_instances'] == 0
            final_status = 'completed' if all_passed else 'failed'
            final_result = 'success' if all_passed else 'failure'

            Rapport.update(rapport_id, {
                'status': final_status,
                'result': final_result,
                'progress': 100,
                'executionTimeMs': exec_time_ms,
                'endTime': end_time
            })
            Rapport.update_perf_results(rapport_id, perf_results)

            self._emit('perf_completed', {
                'rapport_id': rapport_id,
                'campain_id': campain_id,
                'status': final_status,
                'result': final_result,
                'global': _serialize_global(perf_results),
                'tests': [_serialize_test(tr) for tr in perf_results['tests']]
            }, rapport_id)

        except Exception as exc:
            error_msg = f"Erreur: {str(exc)}\n{traceback.format_exc()}"
            print(f"\n❌ ERREUR test de performance ({rapport_id}): {exc}")
            Rapport.update(rapport_id, {
                'status': 'failed',
                'result': 'failure',
                'details': error_msg
            })
            self._emit('perf_error', {
                'rapport_id': rapport_id,
                'error': str(exc)
            }, rapport_id)

    # ------------------------------------------------------------------
    # Exécution d'une instance de test
    # ------------------------------------------------------------------

    def _execute_test_instance(self, test_id, variables_dict, instance_num, timeout_override=None):
        """Exécute une instance unique d'un test. Thread-safe (contexte isolé)."""
        start_time = time.time()
        status = 'passed'

        try:
            test = Test.find_by_id(test_id)
            if not test:
                return {
                    'status': 'failed',
                    'executionTimeMs': 0,
                    'instance_num': instance_num
                }

            # Contexte de variables isolé par instance
            test_variables = {}
            for var_name in test.get('variables', []):
                test_variables[f'app.{var_name}'] = None

            for action_data in test.get('actions', []):
                action_type = action_data.get('type')
                action_value = action_data.get('value', {})

                resolved_value = self._resolve_variables(action_value, variables_dict, test_variables)
                resolved_value['_campain_id'] = variables_dict.get('test.campain_id')
                # Injecter le timeout override global si activé
                if timeout_override is not None:
                    resolved_value['_timeout_override'] = timeout_override

                action_plugin = self.plugin_manager.get_plugin(action_type)
                if not action_plugin:
                    status = 'failed'
                    break

                try:
                    result = action_plugin.execute(resolved_value, test_variables)
                    if result.get('result'):
                        output_mapping = action_value.get('output_mapping', {})
                        if output_mapping:
                            output_values = result.get('output_variables', {})
                            for plugin_var_name, test_var_name in output_mapping.items():
                                if plugin_var_name in output_values:
                                    test_variables[f'app.{test_var_name}'] = output_values[plugin_var_name]
                    else:
                        status = 'failed'
                        break
                except Exception:
                    status = 'failed'
                    break

        except Exception:
            status = 'failed'

        end_time = time.time()
        return {
            'status': status,
            'executionTimeMs': int((end_time - start_time) * 1000),
            'instance_num': instance_num
        }

    # ------------------------------------------------------------------
    # Résolution des variables
    # ------------------------------------------------------------------

    def _resolve_variables(self, value, variables_dict, test_variables):
        """Résout les variables dans une valeur (string, dict, list)."""
        if isinstance(value, str):
            def replace_testgyver(match):
                return str(variables_dict.get(match.group(1), match.group(0)))

            def replace_test(match):
                full_key = f"app.{match.group(1)}"
                return str(test_variables[full_key]) if full_key in test_variables else match.group(0)

            def replace_collection(match):
                full_key = f"test.{match.group(1)}"
                return str(variables_dict[full_key]) if full_key in variables_dict else match.group(0)

            value = re.sub(r'\{\{([^.}]+)\}\}', replace_testgyver, value)
            value = re.sub(r'\{\{app\.([^}]+)\}\}', replace_test, value)
            value = re.sub(r'\{\{test\.([^}]+)\}\}', replace_collection, value)
            return value

        if isinstance(value, dict):
            return {k: self._resolve_variables(v, variables_dict, test_variables) for k, v in value.items()}

        if isinstance(value, list):
            return [self._resolve_variables(item, variables_dict, test_variables) for item in value]

        return value


# ------------------------------------------------------------------
# Fonctions utilitaires de sérialisation (hors classe)
# ------------------------------------------------------------------

def _serialize_global(pr):
    return {
        'total_instances': pr['total_instances'],
        'executed_instances': pr['executed_instances'],
        'passed_instances': pr['passed_instances'],
        'failed_instances': pr['failed_instances'],
        'exec_time_avg_ms': pr['exec_time_avg_ms'],
        'exec_time_min_ms': pr['exec_time_min_ms'] or 0,
        'exec_time_max_ms': pr['exec_time_max_ms'],
        'exec_time_total_ms': pr['exec_time_total_ms']
    }


def _serialize_test(tr):
    return {
        'test_id': tr['test_id'],
        'name': tr['name'],
        'total_instances': tr['total_instances'],
        'executed_instances': tr['executed_instances'],
        'passed_instances': tr['passed_instances'],
        'failed_instances': tr['failed_instances'],
        'exec_time_avg_ms': tr['exec_time_avg_ms'],
        'exec_time_min_ms': tr.get('exec_time_min_ms') or 0,
        'exec_time_max_ms': tr['exec_time_max_ms'],
        'exec_time_total_ms': tr['exec_time_total_ms']
    }
