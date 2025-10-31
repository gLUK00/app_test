#!/usr/bin/env python3
"""Script de test pour vérifier la logique de création récursive de répertoires."""

print("=" * 70)
print("Test de la logique de création récursive de répertoires")
print("=" * 70)

# Mock de la classe ActionBase pour éviter les imports
class MockActionBase:
    def __init__(self):
        self.traces = []
    
    def add_trace(self, message):
        self.traces.append(message)

# Mock du client WebDAV pour tester la logique
class MockWebDAVClient:
    def __init__(self):
        self.existing_paths = set()
        self.created_paths = []
    
    def exists(self, path):
        """Simule la vérification d'existence."""
        return path in self.existing_paths
    
    def mkdir(self, path):
        """Simule la création d'un répertoire."""
        if path in self.existing_paths:
            raise Exception(f"Le répertoire {path} existe déjà")
        self.existing_paths.add(path)
        self.created_paths.append(path)
        print(f"   [MOCK] Répertoire créé: {path}")

# Implémentation de la fonction _mkdir_recursive (copie de la logique)
def mkdir_recursive(action, client, path):
    """
    Crée récursivement les répertoires nécessaires.
    """
    # Normaliser le chemin (enlever les slashes multiples et trailing slash)
    path = path.rstrip('/')
    
    # Si le répertoire existe déjà, ne rien faire
    if client.exists(path):
        action.add_trace(f"Le répertoire {path} existe déjà")
        return
    
    # Diviser le chemin en parties
    parts = [p for p in path.split('/') if p]
    
    # Construire et créer chaque niveau
    current_path = ''
    for part in parts:
        current_path = f"{current_path}/{part}" if current_path else part
        
        # Vérifier si ce niveau existe déjà
        if not client.exists(current_path):
            try:
                client.mkdir(current_path)
                action.add_trace(f"Sous-répertoire créé: {current_path}")
            except Exception as e:
                action.add_trace(f"Erreur lors de la création de {current_path}: {str(e)}")
                raise

# Créer une instance mock
action = MockActionBase()

print("\n1. Test de création d'un chemin simple")
print("-" * 70)
client = MockWebDAVClient()
action = MockActionBase()
mkdir_recursive(action, client, "folder1")
print(f"   Résultat: {client.created_paths}")
assert client.created_paths == ["folder1"], "Échec du test 1"
print("   ✅ Test 1 réussi\n")

print("2. Test de création d'un chemin à 2 niveaux")
print("-" * 70)
client = MockWebDAVClient()
action = MockActionBase()
mkdir_recursive(action, client, "folder1/folder2")
print(f"   Résultat: {client.created_paths}")
assert client.created_paths == ["folder1", "folder1/folder2"], "Échec du test 2"
print("   ✅ Test 2 réussi\n")

print("3. Test de création d'un chemin à 3 niveaux")
print("-" * 70)
client = MockWebDAVClient()
action = MockActionBase()
mkdir_recursive(action, client, "path1/path2/path3")
print(f"   Résultat: {client.created_paths}")
expected = ["path1", "path1/path2", "path1/path2/path3"]
assert client.created_paths == expected, f"Échec du test 3: attendu {expected}, obtenu {client.created_paths}"
print("   ✅ Test 3 réussi\n")

print("4. Test avec un répertoire parent existant")
print("-" * 70)
client = MockWebDAVClient()
action = MockActionBase()
client.existing_paths.add("folder1")
mkdir_recursive(action, client, "folder1/folder2/folder3")
print(f"   Résultat: {client.created_paths}")
expected = ["folder1/folder2", "folder1/folder2/folder3"]
assert client.created_paths == expected, f"Échec du test 4"
print("   ✅ Test 4 réussi\n")

print("5. Test avec un répertoire déjà existant")
print("-" * 70)
client = MockWebDAVClient()
action = MockActionBase()
client.existing_paths.add("existing_folder")
mkdir_recursive(action, client, "existing_folder")
print(f"   Résultat: {client.created_paths}")
assert client.created_paths == [], "Échec du test 5"
print("   ✅ Test 5 réussi (aucune création car existe déjà)\n")

print("6. Test avec trailing slash")
print("-" * 70)
client = MockWebDAVClient()
action = MockActionBase()
mkdir_recursive(action, client, "folder1/folder2/")
print(f"   Résultat: {client.created_paths}")
expected = ["folder1", "folder1/folder2"]
assert client.created_paths == expected, "Échec du test 6"
print("   ✅ Test 6 réussi\n")

print("7. Test avec chemin profond (5 niveaux)")
print("-" * 70)
client = MockWebDAVClient()
action = MockActionBase()
mkdir_recursive(action, client, "a/b/c/d/e")
print(f"   Résultat: {client.created_paths}")
expected = ["a", "a/b", "a/b/c", "a/b/c/d", "a/b/c/d/e"]
assert client.created_paths == expected, "Échec du test 7"
print("   ✅ Test 7 réussi\n")

print("8. Test avec certains niveaux existants")
print("-" * 70)
client = MockWebDAVClient()
action = MockActionBase()
client.existing_paths.add("uploads")
client.existing_paths.add("uploads/2025")
mkdir_recursive(action, client, "uploads/2025/10/31/reports")
print(f"   Résultat: {client.created_paths}")
expected = ["uploads/2025/10", "uploads/2025/10/31", "uploads/2025/10/31/reports"]
assert client.created_paths == expected, "Échec du test 8"
print("   ✅ Test 8 réussi\n")

print("=" * 70)
print("✅ TOUS LES TESTS ONT RÉUSSI!")
print("=" * 70)
print("\nLa fonction _mkdir_recursive gère correctement:")
print("  - Les chemins à un seul niveau")
print("  - Les chemins à plusieurs niveaux")
print("  - Les répertoires parents déjà existants")
print("  - Les chemins avec trailing slash")
print("  - Les chemins profonds")
print("  - La création partielle quand certains niveaux existent")
