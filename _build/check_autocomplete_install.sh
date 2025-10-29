#!/bin/bash

# Script de vérification de l'installation de l'autocomplétion des variables

echo "🔍 Vérification de l'installation de l'autocomplétion des variables..."
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteur
total=0
success=0

# Fonction de vérification
check_file() {
    total=$((total + 1))
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        success=$((success + 1))
    else
        echo -e "${RED}✗${NC} $2 - Fichier non trouvé: $1"
    fi
}

check_content() {
    total=$((total + 1))
    if grep -q "$2" "$1" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $3"
        success=$((success + 1))
    else
        echo -e "${RED}✗${NC} $3 - Contenu non trouvé dans: $1"
    fi
}

echo "📁 Fichiers créés:"
check_file "static/js/variable-autocomplete.js" "Plugin JavaScript"
check_file "static/test-autocomplete.html" "Page de test"
check_file "docs/VARIABLE_AUTOCOMPLETE.md" "Documentation complète"
check_file "docs/VARIABLE_AUTOCOMPLETE_QUICKSTART.md" "Guide rapide"
check_file "docs/IMPLEMENTATION_AUTOCOMPLETE.md" "Résumé d'implémentation"

echo ""
echo "🔧 Fichiers modifiés:"
check_file "static/css/custom.css" "CSS (fichier existe)"
check_file "templates/base.html" "Template base (fichier existe)"
check_file "templates/test_add.html" "Template ajout (fichier existe)"
check_file "templates/test_edit.html" "Template édition (fichier existe)"
check_file "routes/variables_routes.py" "Routes API (fichier existe)"

echo ""
echo "📝 Contenu vérifié:"
check_content "static/css/custom.css" "variable-autocomplete-suggestions" "Styles CSS d'autocomplétion"
check_content "templates/base.html" "variable-autocomplete.js" "Script inclus dans base.html"
check_content "templates/test_add.html" "VariableAutocomplete" "Initialisation dans test_add.html"
check_content "templates/test_edit.html" "VariableAutocomplete" "Initialisation dans test_edit.html"
check_content "routes/variables_routes.py" "isRoot" "Support du filtre isRoot dans l'API"

echo ""
echo "📊 Résultat:"
echo -e "   ${GREEN}${success}${NC} / ${total} vérifications réussies"

if [ $success -eq $total ]; then
    echo -e "${GREEN}✨ Installation complète !${NC}"
    echo ""
    echo "🚀 Prochaines étapes:"
    echo "   1. Redémarrer l'application Flask"
    echo "   2. Créer des variables racines dans l'admin"
    echo "   3. Tester sur la page d'ajout de test"
    echo "   4. Ou ouvrir static/test-autocomplete.html dans un navigateur"
    exit 0
else
    echo -e "${YELLOW}⚠️  Installation incomplète${NC}"
    echo ""
    echo "Des fichiers manquent ou ont un contenu incomplet."
    exit 1
fi
