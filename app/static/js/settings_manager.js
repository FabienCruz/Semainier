// app/static/js/settings_manager.js

/**
 * File: app/static/js/settings_manager.js
 * Role: Gestionnaire des interactions pour la page de paramètres
 * Description: Gère les notifications après soumission du formulaire de paramètres
 * Input data: Réponses des requêtes HTMX vers /api/settings
 * Output data: Notifications de succès ou d'erreur pour l'utilisateur
 * Business constraints: N/A
 */

document.addEventListener('DOMContentLoaded', function() {
    // Intercepter la réponse HTMX pour afficher les messages de succès/erreur
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.elt.id !== 'settings-form') return;
        
        const resultDiv = document.getElementById('settings-result');
        resultDiv.classList.remove('hidden', 'bg-green-100', 'text-green-800', 'bg-red-100', 'text-red-800');
        
        if (evt.detail.successful) {
            try {
                const response = JSON.parse(evt.detail.xhr.response);
                
                if (response.success) {
                    resultDiv.textContent = 'Paramètres enregistrés avec succès';
                    resultDiv.classList.add('bg-green-100', 'text-green-800');
                } else {
                    resultDiv.textContent = response.error || 'Erreur lors de l\'enregistrement des paramètres';
                    resultDiv.classList.add('bg-red-100', 'text-red-800');
                }
            } catch (e) {
                resultDiv.textContent = 'Erreur lors du traitement de la réponse';
                resultDiv.classList.add('bg-red-100', 'text-red-800');
            }
        } else {
            resultDiv.textContent = 'Erreur lors de l\'enregistrement des paramètres';
            resultDiv.classList.add('bg-red-100', 'text-red-800');
        }
        
        // Masquer après 3 secondes
        setTimeout(() => {
            resultDiv.classList.add('hidden');
        }, 3000);
    });
});