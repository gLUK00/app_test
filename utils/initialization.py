import json
import os
import logging
from models.variable import Variable
from utils.db import get_collection

def initialize_variables_from_json(json_path):
    """
    Initialise les variables à partir d'un fichier JSON.
    
    Args:
        json_path (str): Chemin vers le fichier JSON contenant les variables.
    """
    if not os.path.exists(json_path):
        logging.warning(f"Fichier d'initialisation des variables introuvable : {json_path}")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            variables_list = json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Erreur de décodage JSON dans {json_path} : {e}")
        return
    except Exception as e:
        logging.error(f"Erreur lors de la lecture de {json_path} : {e}")
        return

    if not isinstance(variables_list, list):
        logging.error(f"Le format du fichier {json_path} doit être une liste d'objets.")
        return

    collection = get_collection(Variable.collection_name)
    
    count_created = 0
    count_updated = 0

    logging.info(f"Début de l'initialisation des variables depuis {json_path}")

    for var_data in variables_list:
        key = var_data.get('key')
        value = var_data.get('value')
        filiere = var_data.get('filiere')
        description = var_data.get('description', '')

        if not key:
            logging.warning("Variable ignorée car la clé est manquante.")
            continue

        # 1. Gestion de la variable Root
        # Chercher si une variable Root avec cette key existe
        root_var = collection.find_one({'key': key, 'isRoot': True})
        
        if not root_var:
            # Si elle n'existe pas en Root, on la crée
            # Cela couvre le cas "Si elle n'existe pas [du tout]" -> on crée la Root
            try:
                # On vérifie s'il existe une variable avec cette clé (même non root) pour éviter les doublons bizarres
                # Mais la consigne dit "Si elle n'existe pas : Une variable Root sera créée"
                # On force la création de la Root si elle manque
                Variable.create(key=key, value="", filiere="", description=description, is_root=True)
                logging.info(f"Variable Root créée : {key}")
                count_created += 1
                # On la récupère pour confirmer son existence pour la suite
                root_var = collection.find_one({'key': key, 'isRoot': True})
            except Exception as e:
                logging.error(f"Erreur lors de la création de la variable Root {key} : {e}")

        # 2. Gestion de la variable de filière
        if filiere:
            existing_var = collection.find_one({'key': key, 'filiere': filiere})
            
            if existing_var:
                # Si elle existe dans la filiere : Mettre à jour
                try:
                    Variable.update(existing_var['_id'], {
                        'value': value,
                        'filiere': filiere,
                        'description': description
                    })
                    logging.info(f"Variable mise à jour : {key} ({filiere})")
                    count_updated += 1
                except Exception as e:
                    logging.error(f"Erreur lors de la mise à jour de la variable {key} ({filiere}) : {e}")
            else:
                # Si elle n'existe pas dans la filiere mais existe en Root (ce qui est le cas ici car on l'a assurée au point 1)
                # Créer une nouvelle variable dans la filiere
                try:
                    Variable.create(key=key, value=value, filiere=filiere, description=description, is_root=False)
                    logging.info(f"Variable créée : {key} ({filiere})")
                    count_created += 1
                except Exception as e:
                    logging.error(f"Erreur lors de la création de la variable {key} ({filiere}) : {e}")

    logging.info(f"Initialisation des variables terminée. Créées: {count_created}, Mises à jour: {count_updated}")
