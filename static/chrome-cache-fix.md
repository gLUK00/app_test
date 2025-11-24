# Désactiver le cache Chrome pour le développement

## Pendant que DevTools est ouvert :

1. **Ouvrez DevTools** (F12)
2. Allez dans l'onglet **Network**
3. **Cochez la case "Disable cache"** (en haut)
4. **Gardez DevTools ouvert** tant que vous développez

Le cache sera désactivé uniquement quand DevTools est ouvert.

## OU via les paramètres Chrome :

1. F12 → Engrenage (⚙️) en haut à droite
2. Dans "Preferences" → "Network"
3. Cocher "Disable cache (while DevTools is open)"

---

## Pour votre cas actuel :

**Faites Ctrl + Shift + R** puis rééditez une action FTP.

Vous devriez enfin voir :
- 🔵 dans la console
- Le bandeau bleu "Fonction JavaScript FTP activée !"
