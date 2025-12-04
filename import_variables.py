import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from utils.initialization import initialize_variables_from_json

if __name__ == "__main__":
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        print("Usage: python import_variables.py <path_to_json_file>")
        sys.exit(1)
    
    print(f"Importing variables from {json_file}...")
    if os.path.exists(json_file):
        initialize_variables_from_json(json_file)
    else:
        print(f"Error: File {json_file} not found.")
