// Script à exécuter dans la console du navigateur pour recharger les fonctions JavaScript
// Ouvrez la console (F12) et collez ce code

console.log('🔄 Rechargement forcé des fonctions JavaScript...');

// Récupérer l'instance du gestionnaire
if (typeof testActionsManager !== 'undefined') {
    // Recharger les fonctions JavaScript
    fetch('/api/actions/javascript')
        .then(response => response.json())
        .then(data => {
            testActionsManager.actionJavaScriptFunctions = data;
            console.log('✅ Fonctions JavaScript rechargées:', data);
            console.log('📋 Plugins avec JS:', Object.keys(data));
            
            // Afficher un aperçu de la fonction FTP
            if (data.ftp && data.ftp.jsShowForm) {
                console.log('🔵 Aperçu de FTP jsShowForm (premiers caractères):');
                console.log(data.ftp.jsShowForm.substring(0, 200) + '...');
            }
        })
        .catch(error => {
            console.error('❌ Erreur lors du rechargement:', error);
        });
} else {
    console.error('❌ testActionsManager introuvable. Êtes-vous sur la bonne page ?');
}
