"""Package perf_reports pour TestGyver."""
from plugins.plugin_manager import PluginManager
from .perf_report_base import PerfReportBase

# Initialiser le gestionnaire de plugins pour les rapports de performance
perf_report_manager = PluginManager('perf_reports', PerfReportBase)

# Découvrir et charger automatiquement tous les plugins
perf_report_manager.discover_plugins()

# Registre de tous les rapports disponibles
PERF_REPORT_REGISTRY = perf_report_manager.get_all_plugins()


def get_perf_report(report_type):
    """
    Retourne une instance du plugin correspondant au type.

    Args:
        report_type (str): Type du rapport ('html', 'csv', 'json', etc.)

    Returns:
        Instance du plugin ou None si le type n'existe pas
    """
    return perf_report_manager.get_plugin(report_type)


def get_all_perf_reports():
    """
    Retourne la liste de tous les rapports de performance disponibles.

    Returns:
        dict: { type: {"metadata": {...}, "class": ..., "configuration_schema": [...]} }
    """
    reports = {}
    for report_type, report_class in PERF_REPORT_REGISTRY.items():
        instance = report_class()
        reports[report_type] = {
            "metadata": instance.get_metadata(),
            "class": report_class.__name__,
            "output_format": instance.get_output_format(),
            "configuration_schema": instance.get_configuration_schema()
        }
    return reports


def reload_perf_reports():
    """
    Recharge tous les plugins de rapports de performance.

    Returns:
        dict: Dictionnaire des rapports rechargés
    """
    global PERF_REPORT_REGISTRY
    perf_report_manager.reload_plugins()
    PERF_REPORT_REGISTRY = perf_report_manager.get_all_plugins()
    return PERF_REPORT_REGISTRY


def register_perf_report(report_name, report_class):
    """
    Enregistre manuellement un nouveau plugin de rapport de performance.

    Args:
        report_name (str): Nom du rapport
        report_class: Classe du rapport

    Returns:
        bool: True si enregistré avec succès
    """
    success = perf_report_manager.register_plugin(report_name, report_class)
    if success:
        global PERF_REPORT_REGISTRY
        PERF_REPORT_REGISTRY = perf_report_manager.get_all_plugins()
    return success


def list_perf_reports():
    """
    Liste tous les rapports de performance disponibles avec leurs informations.

    Returns:
        list: Liste des informations de rapports
    """
    return perf_report_manager.list_plugins()


__all__ = [
    'PerfReportBase',
    'get_perf_report',
    'get_all_perf_reports',
    'reload_perf_reports',
    'register_perf_report',
    'list_perf_reports',
    'PERF_REPORT_REGISTRY',
    'perf_report_manager'
]
