#!/bin/bash

# Arrêter le script en cas d'erreur
set -e

# Se placer à la racine du projet (parent du dossier _build où se trouve ce script)
cd "$(dirname "$0")/.."

echo "=== Démarrage de la gestion des traductions ==="

# Vérifier si babel.cfg existe
if [ ! -f "babel.cfg" ]; then
    echo "Erreur: babel.cfg non trouvé à la racine du projet."
    exit 1
fi

echo "1. Extraction des messages..."
pybabel extract -F babel.cfg -o messages.pot .

# Liste des langues à gérer (l'anglais est la langue source)
LANGUAGES="en fr es zh de ja"

echo "2. Gestion des catalogues (init/update)..."
for lang in $LANGUAGES; do
    if [ -d "translations/$lang" ]; then
        echo "   -> Mise à jour du catalogue pour : $lang"
        pybabel update -i messages.pot -d translations -l $lang
    else
        echo "   -> Initialisation du catalogue pour : $lang"
        pybabel init -i messages.pot -d translations -l $lang
    fi
done

echo "3. Compilation des traductions..."
pybabel compile -d translations

echo "=== Opérations terminées avec succès ==="
