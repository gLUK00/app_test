import json
import os
import sys
import argparse

# Add project root to path to import modules
sys.path.append(os.getcwd())

from models.variable import Variable

def export_variables(output_file, filiere=None, obfuscate=False):
    print(f"Exporting variables...")
    if filiere:
        print(f"Filtering by environment: {filiere}")
        try:
            variables = Variable.get_by_filiere(filiere)
        except Exception as e:
            print(f"Error retrieving variables: {e}")
            return
    else:
        print("Exporting all variables")
        try:
            variables = Variable.get_all()
        except Exception as e:
            print(f"Error retrieving variables: {e}")
            return
    
    export_list = []
    for var in variables:
        # On ne garde que les champs nécessaires pour l'import
        export_item = {
            "key": var.get("key"),
            "value": var.get("value"),
            "filiere": var.get("filiere"),
            "description": var.get("description", ""),
            "isRoot": var.get("isRoot", False),
            "isObfuscated": var.get("isObfuscated", False)
        }
        
        # Si l'option d'obfuscation est activée et que la variable est marquée comme obfusquée
        if obfuscate and var.get("isObfuscated"):
            export_item["value"] = "*****"

        export_list.append(export_item)
        
    print(f"{len(export_list)} variables found.")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_list, f, indent=4, ensure_ascii=False)
        print(f"File {output_file} created successfully.")
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export variables to JSON')
    parser.add_argument('output_file', help='Path to the output JSON file')
    parser.add_argument('--filiere', help='Filter by environment (filiere)')
    parser.add_argument('--obfuscate', action='store_true', help='Obfuscate sensitive values')
    
    args = parser.parse_args()
    
    export_variables(args.output_file, args.filiere, args.obfuscate)
