// app/static/js/timetable_navigation.js

/**
 * File: app/static/js/timetable_navigation.js
 * Role: Gestion de la navigation et des interactions dans la colonne "Emploi du temps"
 * Description: Fournit les fonctions pour naviguer entre les jours et gérer les interactions
 *              avec la grille de créneaux horaires
 * Input data: Événements utilisateur, état actuel de la colonne (jour affiché)
 * Output data: Mises à jour de l'interface, requêtes HTMX pour navigation
 * Business constraints:
 * - La navigation est limitée aux jours de la semaine courante
 * - Les jours passés sont en lecture seule
 */

const TimetableManager = (function() {
    /**
     * Initialise le gestionnaire de la colonne "Emploi du temps"
     */
    function init() {
        // Écouter les événements personnalisés de HTMX
        document.addEventListener('htmx:afterSwap', handleAfterSwap);
        
        // Initialiser l'état de la colonne
        updateColumnState();
    }
    
    /**
     * Gère les événements après un swap HTMX
     * @param {Event} event - L'événement HTMX
     */
    function handleAfterSwap(event) {
        // Si le swap concerne la colonne "Emploi du temps"
        if (event.detail.target.closest('.timetable-column')) {
            updateColumnState();
        }
    }
    
    /**
     * Met à jour l'état visuel de la colonne selon le jour affiché
     */
    function updateColumnState() {
        const timetableColumn = document.querySelector('.timetable-column');
        if (!timetableColumn) return;
        
        const dayInfo = getCurrentDayInfo();
        if (!dayInfo) return;
        
        // Mettre à jour les classes visuelles selon le statut du jour
        const columnContent = timetableColumn.querySelector('.column-content');
        if (columnContent) {
            columnContent.classList.remove('past-day', 'current-day', 'future-day');
            if (dayInfo.isPast) {
                columnContent.classList.add('past-day');
            } else if (dayInfo.isToday) {
                columnContent.classList.add('current-day');
            } else {
                columnContent.classList.add('future-day');
            }
        }
    }
    
    /**
     * Récupère les informations sur le jour actuellement affiché
     * @returns {Object|null} Informations sur le jour ou null
     */
    function getCurrentDayInfo() {
        const dateDisplay = document.querySelector('#timetable-date');
        if (!dateDisplay) return null;
        
        // Extraire la date du format affiché (ex: "mer 01/03")
        const displayText = dateDisplay.textContent.trim();
        
        // Déterminer si c'est un jour passé, le jour courant ou un jour futur
        // Note: Cette info devrait venir d'attributs data-* plutôt que du texte
        const columnContent = document.querySelector('.column-content');
        const isPast = columnContent?.classList.contains('past-day') || false;
        const isToday = columnContent?.classList.contains('current-day') || false;
        
        return {
            displayText,
            isPast,
            isToday,
            isFuture: !isPast && !isToday
        };
    }
    
    /**
     * Rafraîchit le contenu de la colonne "Emploi du temps"
     */
    function refreshContent() {
        document.body.dispatchEvent(new Event('timetableRefresh'));
    }
    
    // API publique
    return {
        init,
        refreshContent,
        getCurrentDayInfo
    };
})();

// Initialiser le gestionnaire au chargement de la page
document.addEventListener('DOMContentLoaded', TimetableManager.init);

// Exposer globalement
window.TimetableManager = TimetableManager;
