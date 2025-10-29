"""Package reports pour TestGyver."""
from plugins.plugin_manager import PluginManager
from .report_base import ReportBase

# Initialiser le gestionnaire de plugins pour les rapports
report_manager = PluginManager('reports', ReportBase)

# Découvrir et charger automatiquement tous les plugins de rapports
report_manager.discover_plugins()

# Registre de tous les rapports disponibles
REPORT_REGISTRY = report_manager.get_all_plugins()


def get_report(report_type):
    """
    Retourne une instance du plugin de rapport correspondant au type.
    
    Args:
        report_type: Type du rapport ('pdf', 'html', 'excel', etc.)
    
    Returns:
        Instance du rapport ou None si le type n'existe pas
    """
    return report_manager.get_plugin(report_type)


def get_all_reports():
    """
    Retourne la liste de tous les rapports disponibles.
    
    Returns:
        dict: Dictionnaire {type: {"metadata": {...}, "class": ...}}
    """
    reports = {}
    for report_type, report_class in REPORT_REGISTRY.items():
        instance = report_class()
        reports[report_type] = {
            "metadata": instance.get_metadata(),
            "class": report_class.__name__,
            "output_format": instance.get_output_format(),
            "configuration_schema": instance.get_configuration_schema()
        }
    return reports


def reload_reports():
    """
    Recharge tous les plugins de rapports.
    
    Returns:
        dict: Dictionnaire des rapports rechargés
    """
    global REPORT_REGISTRY
    report_manager.reload_plugins()
    REPORT_REGISTRY = report_manager.get_all_plugins()
    return REPORT_REGISTRY


def register_report(report_name, report_class):
    """
    Enregistre manuellement un nouveau plugin de rapport.
    
    Args:
        report_name (str): Nom du rapport
        report_class: Classe du rapport
    
    Returns:
        bool: True si enregistré avec succès
    """
    success = report_manager.register_plugin(report_name, report_class)
    if success:
        global REPORT_REGISTRY
        REPORT_REGISTRY = report_manager.get_all_plugins()
    return success


def list_reports():
    """
    Liste tous les rapports disponibles avec leurs informations.
    
    Returns:
        list: Liste des informations de rapports
    """
    return report_manager.list_plugins()


__all__ = [
    'ReportBase',
    'get_report',
    'get_all_reports',
    'reload_reports',
    'register_report',
    'list_reports',
    'REPORT_REGISTRY',
    'report_manager'
]
