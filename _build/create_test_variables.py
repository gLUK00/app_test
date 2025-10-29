#!/usr/bin/env python3
"""
Script pour créer des variables racines de test
"""
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.variable import Variable

def create_test_variables():
    """Crée des variables racines de test."""
    
    print("🔧 Création des variables racines de test...")
    print()
    
    # Variables de test à créer
    test_variables = [
        {
            'key': 'username',
            'description': 'Nom d\'utilisateur',
            'is_root': True
        },
        {
            'key': 'password',
            'description': 'Mot de passe',
            'is_root': True
        },
        {
            'key': 'host',
            'description': 'Nom d\'hôte ou adresse IP',
            'is_root': True
        },
        {
            'key': 'hostname',
            'description': 'Nom d\'hôte du serveur',
            'is_root': True
        },
        {
            'key': 'api_token',
            'description': 'Token d\'authentification API',
            'is_root': True
        },
        {
            'key': 'api_key',
            'description': 'Clé d\'API',
            'is_root': True
        },
        {
            'key': 'endpoint',
            'description': 'Point de terminaison de l\'API',
            'is_root': True
        },
        {
            'key': 'port',
            'description': 'Numéro de port',
            'is_root': True
        },
        {
            'key': 'database',
            'description': 'Nom de la base de données',
            'is_root': True
        },
        {
            'key': 'email',
            'description': 'Adresse email',
            'is_root': True
        },
        {
            'key': 'base_url',
            'description': 'URL de base de l\'application',
            'is_root': True
        },
        {
            'key': 'timeout',
            'description': 'Délai d\'attente en secondes',
            'is_root': True
        }
    ]
    
    created = 0
    skipped = 0
    
    for var_data in test_variables:
        try:
            # Vérifier si la variable existe déjà
            existing = Variable.find_by_key_and_root(var_data['key'], is_root=True)
            
            if existing:
                print(f"⏭️  Variable '{var_data['key']}' existe déjà")
                skipped += 1
            else:
                # Créer la variable
                Variable.create(
                    key=var_data['key'],
                    value='',  # Valeur vide pour les variables racines
                    filiere='',  # Pas de filière pour les variables racines
                    description=var_data['description'],
                    is_root=True
                )
                print(f"✅ Variable racine '{var_data['key']}' créée")
                created += 1
                
        except Exception as e:
            print(f"❌ Erreur lors de la création de '{var_data['key']}': {str(e)}")
    
    print()
    print("📊 Résumé:")
    print(f"   ✅ {created} variable(s) créée(s)")
    print(f"   ⏭️  {skipped} variable(s) déjà existante(s)")
    print()
    
    # Afficher toutes les variables racines
    all_root_vars = Variable.get_all()
    root_vars = [v for v in all_root_vars if v.get('isRoot') is True]
    
    print(f"🏷️  Total de variables racines en base: {len(root_vars)}")
    if root_vars:
        print()
        print("Liste des variables racines:")
        for var in root_vars:
            print(f"   • {var['key']}: {var.get('description', 'Pas de description')}")
    
    print()
    print("✨ Terminé!")

if __name__ == '__main__':
    try:
        create_test_variables()
    except Exception as e:
        print(f"❌ Erreur fatale: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
