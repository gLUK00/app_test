"""Utilitaires pour la pagination des résultats."""
from utils.db import load_config

def paginate_results(query_results, page=1, page_size=None):
    """
    Pagine les résultats d'une requête.
    
    Args:
        query_results: Liste des résultats à paginer
        page: Numéro de la page (commence à 1)
        page_size: Nombre d'éléments par page
    
    Returns:
        dict: Dictionnaire contenant les résultats paginés et les métadonnées
    """
    config = load_config()
    
    if page_size is None:
        page_size = config['pagination']['page_size']
    
    # Limiter la taille de page au maximum configuré
    max_page_size = config['pagination']['max_page_size']
    if page_size > max_page_size:
        page_size = max_page_size
    
    # Convertir en liste si nécessaire
    results = list(query_results)
    total_items = len(results)
    total_pages = (total_items + page_size - 1) // page_size  # Division arrondie au supérieur
    
    # Vérifier que la page demandée est valide
    if page < 1:
        page = 1
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # Calculer les indices de début et fin
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    
    # Extraire les résultats pour la page demandée
    page_results = results[start_index:end_index]
    
    return {
        'data': page_results,
        'pagination': {
            'current_page': page,
            'page_size': page_size,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }

def get_pagination_params(request):
    """Extrait les paramètres de pagination de la requête."""
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    
    try:
        page_size = int(request.args.get('page_size', None))
    except (ValueError, TypeError):
        page_size = None
    
    return page, page_size
