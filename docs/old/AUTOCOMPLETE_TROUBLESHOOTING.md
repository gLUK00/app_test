# 🔍 Guide de Débogage - Autocomplétion des Variables

## Problème : "0 variables racines chargées"

Si vous voyez ce message dans la console du navigateur :
```
[VariableAutocomplete] 0 variables racines chargées
```

### Causes possibles et solutions

#### 1. ❌ Vous n'êtes pas connecté

**Symptôme** : L'API retourne une erreur 401 (Unauthorized)

**Solution** :
1. Connectez-vous à l'application
2. Allez sur une page de test (ajout ou édition)
3. Rechargez la page

**Vérification** :
```javascript
// Dans la console du navigateur
console.log(localStorage.getItem('token'));
// Devrait afficher un token JWT, pas null
```

#### 2. ❌ Aucune variable racine en base de données

**Symptôme** : L'API retourne un tableau vide ou `{ items: [] }`

**Solution** : Créer des variables racines
```bash
# Depuis le terminal
cd /home/hidalgo/Documents/projects/app_test
python3 create_test_variables.py
```

Cela créera automatiquement 12 variables racines de test :
- username
- password
- host
- hostname
- api_token
- api_key
- endpoint
- port
- database
- email
- base_url
- timeout

**Vérification manuelle** :
1. Allez dans Admin > Variables
2. Vérifiez qu'il existe des variables avec la propriété "Variable racine" cochée

#### 3. ❌ L'endpoint API n'est pas accessible

**Symptôme** : Erreur réseau dans la console

**Solution** :
1. Vérifiez que l'application Flask tourne :
```bash
ps aux | grep flask
```

2. Testez l'endpoint directement :
```bash
# Récupérez d'abord votre token depuis la console du navigateur
TOKEN="votre_token_jwt"

# Testez l'API
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/variables?isRoot=true
```

#### 4. ❌ Problème de format de réponse API

**Symptôme** : Le plugin ne reconnaît pas le format de la réponse

**Solution** : Vérifiez le format dans la console
```javascript
// Dans la console du navigateur, vérifiez la réponse
fetch('/api/variables?isRoot=true', {
    headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('token')
    }
})
.then(r => r.json())
.then(data => console.log('Format de réponse:', data));
```

La réponse attendue devrait être :
```json
{
    "items": [
        { "key": "username", "isRoot": true, "description": "..." },
        { "key": "password", "isRoot": true, "description": "..." }
    ],
    "total": 14,
    "page": 1
}
```

## 🧪 Tests de Diagnostic

### Test 1 : Vérifier l'authentification
```javascript
// Console du navigateur
console.log('Token:', localStorage.getItem('token'));
console.log('Token valide:', !!localStorage.getItem('token'));
```

### Test 2 : Tester l'API manuellement
```javascript
// Console du navigateur
API.get('/api/variables?isRoot=true')
    .then(data => {
        console.log('Réponse API:', data);
        console.log('Nombre de variables:', data.items?.length || 0);
        console.log('Variables racines:', data.items?.filter(v => v.isRoot));
    })
    .catch(err => console.error('Erreur:', err));
```

### Test 3 : Recharger les variables
```javascript
// Console du navigateur
if (window.variableAutocomplete) {
    window.variableAutocomplete.refresh();
}
```

### Test 4 : Vérifier l'état du plugin
```javascript
// Console du navigateur
console.log('Plugin existe:', !!window.variableAutocomplete);
console.log('Nombre de variables:', window.variableAutocomplete?.variables?.length);
console.log('Variables:', window.variableAutocomplete?.variables);
```

## 📝 Logs Détaillés

Pour activer les logs détaillés, le plugin affiche automatiquement :

```
[VariableAutocomplete] Chargement des variables depuis: /api/variables?isRoot=true&page_size=100
[VariableAutocomplete] Réponse API reçue: {items: Array(14), total: 14, ...}
[VariableAutocomplete] Format paginé détecté, nombre total: 14
[VariableAutocomplete] 14 variables racines chargées
[VariableAutocomplete] ✅ Variables chargées avec succès !
[VariableAutocomplete] Exemples: ["username", "password", "host"]
```

Si vous voyez `0 variables racines chargées`, les messages d'avertissement suivants apparaîtront :
```
[VariableAutocomplete] ⚠️  Aucune variable racine trouvée !
[VariableAutocomplete] Vérifiez que :
[VariableAutocomplete]   1. Vous êtes bien connecté
[VariableAutocomplete]   2. Des variables racines existent en base (isRoot=true)
[VariableAutocomplete]   3. L'endpoint API est accessible
```

## 🔧 Solutions Rapides

### Solution 1 : Tout réinitialiser
```bash
# Terminal
cd /home/hidalgo/Documents/projects/app_test

# Créer les variables de test
python3 create_test_variables.py

# Redémarrer l'application si nécessaire
# (Ctrl+C dans le terminal Flask, puis relancer)
```

### Solution 2 : Vérifier depuis l'interface
1. Connectez-vous à l'application
2. Allez dans **Admin** > **Variables**
3. Vérifiez que des variables avec "Variable racine" ✓ existent
4. Si aucune n'existe, créez-en manuellement ou utilisez le script

### Solution 3 : Recharger la page
Parfois, un simple rechargement de la page résout le problème :
- Appuyez sur **F5** ou **Ctrl+R**
- Ou faites **Ctrl+Shift+R** (rechargement complet)

## 💡 Astuces

### Astuce 1 : Tester sans l'application
Utilisez la page de test autonome :
```bash
# Ouvrez dans votre navigateur
firefox /home/hidalgo/Documents/projects/app_test/static/test-autocomplete.html
# ou
google-chrome /home/hidalgo/Documents/projects/app_test/static/test-autocomplete.html
```

Cette page utilise un mock de l'API et ne nécessite pas d'authentification.

### Astuce 2 : Vérifier les variables en base
```bash
# Terminal
cd /home/hidalgo/Documents/projects/app_test
python3 -c "
from models.variable import Variable
vars = [v for v in Variable.get_all() if v.get('isRoot')]
print(f'Variables racines: {len(vars)}')
for v in vars:
    print(f'  - {v[\"key\"]}: {v.get(\"description\", \"Pas de description\")}')
"
```

### Astuce 3 : Forcer le rechargement
```javascript
// Console du navigateur
localStorage.removeItem('variable_cache');
location.reload();
```

## 📞 Support

Si le problème persiste après avoir essayé toutes ces solutions :

1. **Vérifiez les logs Flask** dans le terminal où l'application tourne
2. **Ouvrez les DevTools** (F12) et regardez l'onglet Network
3. **Copiez les messages d'erreur** complets
4. **Vérifiez la configuration** dans `configuration.json`

## ✅ Checklist de Vérification

- [ ] Je suis connecté à l'application
- [ ] Des variables racines existent en base
- [ ] L'application Flask est en cours d'exécution
- [ ] J'ai rechargé la page après la création des variables
- [ ] La console ne montre pas d'erreur 401
- [ ] L'endpoint `/api/variables?isRoot=true` retourne des données
- [ ] Mon token JWT est valide (pas expiré)

---

**Si tous les points sont cochés et que ça ne fonctionne toujours pas, il y a peut-être un bug à signaler.**
