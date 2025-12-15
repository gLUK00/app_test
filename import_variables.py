import sys
import os
import argparse

# Add project root to path
sys.path.append(os.getcwd())

from utils.initialization import initialize_variables_from_json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Import variables from JSON')
    parser.add_argument('json_file', help='Path to the JSON file containing variables')
    parser.add_argument('--obfuscate', action='store_true', help='Force obfuscation for imported variables (optional)')
    
    args = parser.parse_args()
    
    json_file = args.json_file
    force_obfuscate = args.obfuscate
    
    print(f"Importing variables from {json_file}...")
    if os.path.exists(json_file):
        # Note: initialize_variables_from_json needs to be updated to handle force_obfuscate if we want to override the JSON value
        # For now, we rely on the JSON content, but we could pass this flag down if needed.
        # However, the requirement says "ajouter une option pour obfusquer les valeurs (clé facultative)"
        # which might mean "set isObfuscated=True for all imported variables" OR "respect isObfuscated key in JSON".
        # Given the context, it likely means "allow setting isObfuscated=True for all imported variables via a flag".
        
        # Let's modify initialize_variables_from_json to accept an optional override
        initialize_variables_from_json(json_file, force_obfuscate=force_obfuscate)
    else:
        print(f"Error: File {json_file} not found.")
