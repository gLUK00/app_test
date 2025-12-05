# Gestion des Tokens JWT - Expiration et Invalidité

## Vue d'ensemble

Ce document explique comment l'application TestGyver gère les tokens JWT invalides ou expirés, en assurant une expérience utilisateur fluide avec des messages d'erreur appropriés.

## Fonctionnement

### 1. Détection des Tokens Invalides ou Expirés

La fonction `decode_token()` dans `utils/auth.py` gère deux types d'erreurs :

- **Token expiré** (`jwt.ExpiredSignatureError`) : Le token était valide mais sa durée de validité est dépassée
- **Token invalide** (`jwt.InvalidTokenError`) : Le token est malformé, a une signature invalide, ou est corrompu

### 2. Gestion Différenciée selon le Type de Requête

Le décorateur `token_required` distingue les requêtes API des requêtes web :

#### Requêtes API (routes commençant par `/api/`)
- Retourne une réponse JSON avec le code HTTP 401
- Inclut un message d'erreur descriptif dans le corps de la réponse

```json
{
  "message": "Votre session a expiré. Veuillez vous reconnecter."
}
```

#### Requêtes Web (pages HTML)
- Utilise Flask flash messages pour afficher l'erreur
- Redirige automatiquement vers la page de login (`/`)
- Supprime le cookie invalide pour éviter des boucles de redirection

### 3. Affichage des Messages d'Erreur

#### Sur la page de login
Les messages flash sont affichés en haut du formulaire avec un style approprié :
- **Erreur** (rouge) : Token invalide ou problèmes graves
- **Avertissement** (orange) : Session expirée ou accès refusé

#### Sur les autres pages
Les messages flash sont affichés dans le template `base.html` avec des icônes FontAwesome :
- ❌ Erreur
- ⚠️ Avertissement
- ✅ Succès
- ℹ️ Information

### 4. Gestion Côté Client (JavaScript)

Le fichier `static/js/app.js` gère également les erreurs d'authentification :

```javascript
if (response.status === 401) {
    // Afficher un message à l'utilisateur
    Notification.error(message);
    
    // Supprimer le token du localStorage
    Auth.removeToken();
    
    // Rediriger vers la page de login après un délai
    setTimeout(() => {
        window.location.href = '/?error=session_expired';
    }, 1500);
}
```

## Scénarios d'Utilisation

### Scénario 1 : Token Expiré lors de la Navigation
1. L'utilisateur accède à une page protégée avec un token expiré
2. Le décorateur `token_required` détecte l'expiration
3. Un message flash "Votre session a expiré. Veuillez vous reconnecter." s'affiche
4. L'utilisateur est redirigé vers la page de login
5. Le cookie invalide est supprimé

### Scénario 2 : Token Expiré lors d'un Appel API
1. Le JavaScript fait un appel API avec un token expiré
2. L'API retourne un code 401 avec le message d'erreur
3. Le JavaScript affiche une notification temporaire
4. Le token est supprimé du localStorage
5. L'utilisateur est redirigé vers la page de login

### Scénario 3 : Token Invalide (Manipulé)
1. Un token corrompu ou invalide est détecté
2. Un message "Token invalide. Veuillez vous reconnecter." s'affiche
3. Redirection immédiate vers la page de login
4. Suppression du cookie/token

### Scénario 4 : Accès Administrateur Refusé
1. Un utilisateur non-admin tente d'accéder à une page admin
2. Le décorateur `admin_required` détecte le problème
3. Message : "Accès refusé : vous devez être administrateur"
4. Redirection vers le dashboard (pas de déconnexion)

## Configuration

La durée de validité des tokens est configurable dans `configuration.json` :

```json
{
  "security": {
    "token_expiration_minutes": 60
  }
}
```

## Messages d'Erreur

### Messages Utilisateur
| Type d'Erreur | Message |
|--------------|---------|
| Token expiré | "Votre session a expiré. Veuillez vous reconnecter." |
| Token invalide | "Token invalide. Veuillez vous reconnecter." |
| Token manquant | "Vous devez vous connecter pour accéder à cette page" |
| Accès refusé (admin) | "Accès refusé : vous devez être administrateur pour accéder à cette page" |

## Tests

Un script de test `test_token_validation.py` est disponible pour valider le bon fonctionnement :

```bash
python test_token_validation.py
```

Tests effectués :
- ✅ Token valide
- ✅ Token expiré
- ✅ Token invalide
- ✅ Token malformé

## Sécurité

### Bonnes Pratiques Implémentées
1. **Suppression automatique des tokens invalides** : Évite les boucles de redirection
2. **Messages génériques** : Ne révèle pas trop d'informations sur la nature de l'erreur
3. **HTTPOnly cookies** : Protège contre les attaques XSS
4. **Validation côté serveur et client** : Double vérification de l'authenticité

### Points d'Attention
- Les tokens sont stockés dans les cookies (HTTPOnly) et le localStorage
- La durée d'expiration doit être un équilibre entre sécurité et confort utilisateur
- Les messages d'erreur ne doivent pas révéler d'informations sensibles

## Flux de Redirection

```
┌─────────────────────────────────────────────────────────┐
│                  Requête Protégée                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
                ┌───────────────┐
                │ Token présent?│
                └───────┬───────┘
                        │
                  ┌─────┴─────┐
                  │           │
                NON          OUI
                  │           │
                  ▼           ▼
          ┌────────────┐  ┌────────────────┐
          │Flash: Login│  │ Token valide ? │
          │Required    │  └────────┬───────┘
          └─────┬──────┘           │
                │            ┌─────┴─────┐
                │            │           │
                │          NON          OUI
                │            │           │
                │            ▼           ▼
                │    ┌──────────────┐ ┌──────────────┐
                │    │Flash: Expired│ │  Accès OK    │
                │    │or Invalid    │ │              │
                │    └──────┬───────┘ └──────────────┘
                │           │
                └───────────┴────►  Redirect: /
```

## Améliorations Futures

- [ ] Implémenter un système de refresh tokens
- [ ] Ajouter une alerte avant l'expiration du token
- [ ] Logger les tentatives d'accès avec tokens invalides
- [ ] Implémenter un système de révocation de tokens
- [ ] Ajouter une option "Se souvenir de moi" avec tokens longue durée

## Support Multi-langue

Les messages d'erreur devront être traduits lors de l'implémentation de Flask-Babel :
- Français (fr)
- Anglais (en)
- Espagnol (es)
- Allemand (de)
- Italien (it)
