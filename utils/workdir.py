"""Utilitaire pour la gestion du répertoire de travail des campagnes."""
import os
import shutil
import json
from pathlib import Path
from models.campain import Campain


def get_workdir():
    """Récupère le chemin du répertoire de travail depuis la configuration."""
    config_path = Path(__file__).parent.parent / 'configuration.json'
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config.get('workdir', './workdir')


def ensure_workdir_exists():
    """
    Vérifie que le répertoire workdir existe, sinon le crée.
    Supprime également les répertoires orphelins (campagnes supprimées).
    """
    workdir = get_workdir()
    workdir_path = Path(workdir)
    
    # Créer le workdir s'il n'existe pas
    if not workdir_path.exists():
        workdir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Répertoire de travail créé: {workdir_path.absolute()}")
    else:
        print(f"✓ Répertoire de travail existant: {workdir_path.absolute()}")
    
    # Récupérer tous les IDs de campagnes en base de données
    campains = Campain.get_all()
    valid_campain_ids = {str(c['_id']) for c in campains}
    
    # Créer les répertoires pour les campagnes existantes s'ils n'existent pas
    created_count = 0
    for campain_id in valid_campain_ids:
        campain_dir = workdir_path / campain_id
        if not campain_dir.exists():
            try:
                campain_dir.mkdir(parents=True, exist_ok=True)
                created_count += 1
                print(f"  ✓ Répertoire de campagne créé: {campain_id}")
            except Exception as e:
                print(f"  ✗ Erreur lors de la création du répertoire {campain_id}: {e}")
        
        # Créer les sous-répertoires 'files' et 'work' s'ils n'existent pas
        try:
            files_dir = campain_dir / "files"
            work_dir = campain_dir / "work"
            
            if not files_dir.exists():
                files_dir.mkdir(parents=True, exist_ok=True)
            
            if not work_dir.exists():
                work_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"  ✗ Erreur lors de la création des sous-répertoires pour {campain_id}: {e}")
    
    if created_count > 0:
        print(f"✓ {created_count} répertoire(s) de campagne créé(s)")
    
    # Parcourir les répertoires du workdir
    orphan_count = 0
    if workdir_path.exists() and workdir_path.is_dir():
        for item in workdir_path.iterdir():
            if item.is_dir():
                dir_name = item.name
                # Si le répertoire ne correspond à aucune campagne existante
                if dir_name not in valid_campain_ids:
                    try:
                        shutil.rmtree(item)
                        orphan_count += 1
                        print(f"  ✓ Répertoire orphelin supprimé: {dir_name}")
                    except Exception as e:
                        print(f"  ✗ Erreur lors de la suppression de {dir_name}: {e}")
    
    if orphan_count > 0:
        print(f"✓ {orphan_count} répertoire(s) orphelin(s) supprimé(s)")
    else:
        print("✓ Aucun répertoire orphelin détecté")


def create_campain_workdir(campain_id):
    """
    Crée un répertoire de travail pour une campagne avec ses sous-répertoires.
    
    Args:
        campain_id: ID de la campagne
    
    Returns:
        str: Chemin absolu du répertoire créé
    """
    workdir = get_workdir()
    campain_dir = Path(workdir) / str(campain_id)
    
    try:
        campain_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Répertoire de campagne créé: {campain_dir.absolute()}")
        
        # Créer les sous-répertoires 'files' et 'work'
        files_dir = campain_dir / "files"
        work_dir = campain_dir / "work"
        
        files_dir.mkdir(parents=True, exist_ok=True)
        work_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Sous-répertoires créés: files, work")
        
        return str(campain_dir.absolute())
    except Exception as e:
        print(f"✗ Erreur lors de la création du répertoire de campagne {campain_id}: {e}")
        raise


def delete_campain_workdir(campain_id):
    """
    Supprime le répertoire de travail d'une campagne.
    
    Args:
        campain_id: ID de la campagne
    
    Returns:
        bool: True si suppression réussie, False sinon
    """
    workdir = get_workdir()
    campain_dir = Path(workdir) / str(campain_id)
    
    if campain_dir.exists() and campain_dir.is_dir():
        try:
            shutil.rmtree(campain_dir)
            print(f"✓ Répertoire de campagne supprimé: {campain_dir.absolute()}")
            return True
        except Exception as e:
            print(f"✗ Erreur lors de la suppression du répertoire de campagne {campain_id}: {e}")
            return False
    else:
        print(f"ℹ Répertoire de campagne inexistant: {campain_dir.absolute()}")
        return True


def get_campain_workdir(campain_id):
    """
    Récupère le chemin du répertoire de travail d'une campagne.
    
    Args:
        campain_id: ID de la campagne
    
    Returns:
        str: Chemin absolu du répertoire
    """
    workdir = get_workdir()
    campain_dir = Path(workdir) / str(campain_id)
    return str(campain_dir.absolute())
