// Script de débogage pour vérifier le contenu exact de jsShowForm
console.log('=== DEBUT DEBUG ===');
console.log('actionJavaScriptFunctions.ftp:', window.testActionsManager.actionJavaScriptFunctions.ftp);

if (window.testActionsManager.actionJavaScriptFunctions.ftp?.jsShowForm) {
    const code = window.testActionsManager.actionJavaScriptFunctions.ftp.jsShowForm;
    console.log('Longueur du code jsShowForm:', code.length);
    console.log('Premiers 500 caractères:', code.substring(0, 500));
    console.log('Contient 🔵 ?', code.includes('🔵'));
    console.log('Contient "console.log(\'🔵" ?', code.includes("console.log('🔵"));
    
    // Chercher les console.log
    const matches = code.match(/console\.log\([^)]+\)/g);
    console.log('Tous les console.log trouvés:', matches);
}
console.log('=== FIN DEBUG ===');
