#!/usr/bin/env python3
"""Outil de diagnostic pour investiguer un test en base.

Ce script permet :
- d'inspecter les actions associées à un test (type, paramètres bruts, valeurs résolues)
- d'exécuter une action précise pour observer les valeurs réellement envoyées au plugin
- de relancer l'exécution complète du test afin de collecter les traces détaillées

Utilisation rapide :
    python _build/debug_test_failure.py TEST_ID --filiere preprod --action-index 3 --show-logs
"""

from __future__ import annotations

import argparse
import copy
import inspect
import traceback
import sys
from pathlib import Path
from typing import Any, Dict

# Ajouter la racine du projet au PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from models.test import Test  # noqa: E402
from models.variable import Variable  # noqa: E402
from utils.campain_executor import CampainExecutor  # noqa: E402
from utils.workdir import get_campain_workdir  # noqa: E402


class SilentSocketIO:
    """Stub minimal pour les émissions socket utilisées par CampainExecutor."""

    def emit(self, event, data=None, room=None):  # pylint: disable=unused-argument
        # On garde la méthode pour compatibilité mais on ne publie rien.
        return None


def list_filieres() -> None:
    """Affiche la liste des filières disponibles."""
    filieres = Variable.get_all_filieres()
    if not filieres:
        print("Aucune filière détectée (vérifier la collection variables).")
        return
    print("Filières disponibles :")
    for filiere in filieres:
        print(f" - {filiere}")


def build_variables_dict(test_doc: Dict[str, Any], filiere: str | None) -> Dict[str, Any]:
    """Construit le dictionnaire de variables similaire à l'exécution réelle."""
    variables_dict: Dict[str, Any] = {}

    if filiere:
        env_variables = Variable.get_by_filiere(filiere)
        variables_dict.update({var['key']: var['value'] for var in env_variables})
    else:
        print("⚠️  Aucune filière fournie : seules les variables internes seront utilisées.")

    campain_id = test_doc.get('campainId')
    variables_dict.setdefault('test.test_id', test_doc.get('_id'))
    variables_dict.setdefault('test.campain_id', campain_id)

    workdir = Path(get_campain_workdir(campain_id)) if campain_id else ROOT_DIR / 'workdir'
    variables_dict.setdefault('test.files_dir', str(workdir / 'files'))
    variables_dict.setdefault('test.work_dir', str(workdir / 'work'))

    return variables_dict


def describe_action(action: Dict[str, Any], index: int) -> None:
    """Affiche un résumé humainement lisible d'une action."""
    action_type = action.get('type', '<inconnu>')
    value = action.get('value', {})
    print(f"\nAction #{index + 1} — type: {action_type}")
    if not value:
        print("  (pas de paramètres)")
        return
    for key, val in value.items():
        print(f"  - {key}: {val}")


def resolve_action_payload(executor: CampainExecutor, action: Dict[str, Any], variables_dict: Dict[str, Any],
                            test_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Calcule la payload effective envoyée au plugin."""
    test_variables = {f"app.{var_name}": None for var_name in test_doc.get('variables', [])}
    raw_value = action.get('value', {})
    resolved = executor._resolve_variables(copy.deepcopy(raw_value), copy.deepcopy(variables_dict), test_variables)  # pylint: disable=protected-access
    return resolved


def execute_single_action(executor: CampainExecutor, action: Dict[str, Any], resolved_payload: Dict[str, Any]) -> None:
    """Exécute un plugin unique et affiche un maximum d'informations."""
    action_type = action.get('type')
    plugin = executor.plugin_manager.get_plugin(action_type)
    if not plugin:
        print(f"❌ Plugin '{action_type}' introuvable")
        return

    try:
        source_file = inspect.getsourcefile(plugin.__class__) or '<inconnu>'
        execute_callable = plugin.execute
        if hasattr(execute_callable, '__func__'):
            execute_callable = execute_callable.__func__  # type: ignore[attr-defined]
        line_no = inspect.getsourcelines(execute_callable)[1]
        print(f"Plugin: {plugin.__class__.__name__} ({source_file}:{line_no})")
    except (OSError, TypeError):
        print(f"Plugin: {plugin.__class__.__name__} (emplacement non résolu)")

    print("Payload résolue envoyée au plugin:")
    for key, value in resolved_payload.items():
        print(f"  - {key}: {value}")

    print("\n⏩ Exécution en cours...")
    try:
        result = plugin.execute(resolved_payload)
        print("✅ Exécution terminée")
        print("Résultat brut:")
        for key, value in result.items():
            print(f"  - {key}: {value}")
    except Exception as exc:  # pylint: disable=broad-except
        print("❌ Exception levée pendant l'action :")
        print(exc)
        print("Trace complète :")
        print(traceback.format_exc())


def execute_full_test(executor: CampainExecutor, test_id: str, variables_dict: Dict[str, Any], filiere: str,
                      show_logs: bool) -> None:
    """Relance l'exécution complète d'un test et affiche son statut."""
    result = executor._execute_test(test_id, copy.deepcopy(variables_dict), filiere)  # pylint: disable=protected-access
    print("\n=== Résultat de l'exécution complète ===")
    print(f"Statut: {result['status']}")
    print(f"Temps total: {result['executionTimeMs']} ms")
    if show_logs:
        print("\n--- Logs ---")
        print(result['logs'])
    else:
        print("(Utiliser --show-logs pour afficher les logs détaillés)")


def main() -> int:
    parser = argparse.ArgumentParser(description='Diagnostic ciblé d\'un test sauvegardé en base.')
    parser.add_argument('test_id', help="Identifiant du test (ex: 691c48a32abf1a184464bb4a)")
    parser.add_argument('--filiere', help="Nom de la filière/collection de variables à utiliser")
    parser.add_argument('--action-index', type=int,
                        help="Index 1-based de l'action à inspecter/exécuter isolément")
    parser.add_argument('--list-filieres', action='store_true', help="Affiche les filières disponibles et quitte")
    parser.add_argument('--show-logs', action='store_true', help="Affiche les logs complets lors de l'exécution totale")
    parser.add_argument('--no-run', action='store_true', help="N'exécute rien, ne fait qu'inspecter les actions")

    args = parser.parse_args()

    if args.list_filieres:
        list_filieres()
        return 0

    test_doc = Test.find_by_id(args.test_id)
    if not test_doc:
        print(f"Test {args.test_id} introuvable en base.")
        return 1

    print(f"Test: {test_doc.get('name') or '(sans nom)'}")
    print(f"Description: {test_doc.get('description') or '—'}")
    print(f"Campagne: {test_doc.get('campainId')}")
    print(f"Nombre d'actions: {len(test_doc.get('actions', []))}")

    for idx, action in enumerate(test_doc.get('actions', [])):
        describe_action(action, idx)

    executor = CampainExecutor(SilentSocketIO())
    variables_dict = build_variables_dict(test_doc, args.filiere)

    if args.action_index:
        zero_based = args.action_index - 1
        actions = test_doc.get('actions', [])
        if zero_based < 0 or zero_based >= len(actions):
            print(f"Index d'action invalide ({args.action_index}).")
            return 1
        target_action = actions[zero_based]
        resolved_payload = resolve_action_payload(executor, target_action, variables_dict, test_doc)
        execute_single_action(executor, target_action, resolved_payload)
        if args.no_run:
            return 0

    if args.no_run:
        return 0

    if not args.filiere:
        print("❌ Impossible d'exécuter le test sans préciser --filiere")
        return 1

    execute_full_test(executor, args.test_id, variables_dict, args.filiere, args.show_logs)
    return 0


if __name__ == '__main__':
    sys.exit(main())
