// app/static/js/date_utils.js

/**
 * File: app/static/js/date_utils.js
 * Role: Utilitaires de dates côté client
 * Description: Fournit des fonctions de manipulation et formatage des dates pour l'interface utilisateur
 * Input data: Dates, informations de semaine provenant du serveur
 * Output data: Dates formatées, informations temporelles pour l'interface
 * Business constraints:
 * - La semaine commence le lundi et se termine le dimanche
 * - Les formats courts utilisent des abréviations françaises pour les jours et mois
 * - Utilise en priorité les informations du serveur, avec fallback sur des calculs locaux
 */

const DateUtils = (function() {
    // Stockage privé pour les informations de semaine
    let serverInfo = null;

    /**
     * Initialise les utilitaires de date avec les informations du serveur
     * @param {Object} info - Les informations de date fournies par le serveur
     */
    function initWithServerInfo(info) {
        serverInfo = info;
        console.log("Date Utils initialized with server information");
    }

    /**
     * Obtient les dates de début et fin de la semaine courante
     * @returns {Object} Objet contenant les dates de début et fin
     */
    function getCurrentWeekBounds() {
        if (serverInfo) {
            return {
                startDate: new Date(serverInfo.weekStart),
                endDate: new Date(serverInfo.weekEnd)
            };
        }
        
        // Fallback sur calcul local si info serveur non disponible
        const today = new Date();
        const monday = getMonday(today);
        const sunday = new Date(monday);
        sunday.setDate(monday.getDate() + 6);
        
        return {
            startDate: monday,
            endDate: sunday
        };
    }

    /**
     * Calcule la date du dimanche de la semaine en cours
     * @returns {Date} Date du dimanche de la semaine en cours
     */
    function getCurrentWeekEndDate() {
        if (serverInfo) {
            return new Date(serverInfo.weekEnd);
        }
        
        const today = new Date();
        const dayOfWeek = today.getDay(); // 0 pour dimanche, 1 pour lundi, etc.
        const daysUntilSunday = dayOfWeek === 0 ? 0 : 7 - dayOfWeek;
        const sunday = new Date(today);
        sunday.setDate(today.getDate() + daysUntilSunday);
        return sunday;
    }

    /**
     * Calcule la date du dimanche de la semaine prochaine
     * @returns {Date} Date du dimanche de la semaine prochaine
     */
    function getNextWeekEndDate() {
        if (serverInfo) {
            const nextSunday = new Date(serverInfo.weekEnd);
            nextSunday.setDate(nextSunday.getDate() + 7);
            return nextSunday;
        }
        
        const today = new Date();
        const dayOfWeek = today.getDay(); // 0 pour dimanche, 1 pour lundi, etc.
        const daysUntilNextSunday = dayOfWeek === 0 ? 7 : 14 - dayOfWeek;
        const nextSunday = new Date(today);
        nextSunday.setDate(today.getDate() + daysUntilNextSunday);
        return nextSunday;
    }

    /**
     * Obtient le titre formaté de la semaine
     * @returns {string} Titre formaté (ex: "lun 01/03 au dim 07/03")
     */
    function getWeekTitle() {
        return serverInfo ? serverInfo.displayRange : "Semaine en cours";
    }

    /**
     * Vérifie si une date est dans la semaine courante
     * @param {Date|string} date - Date à vérifier
     * @returns {boolean} True si la date est dans la semaine courante
     */
    function isDateInCurrentWeek(date) {
        if (!serverInfo) return false;
        
        const checkDate = date instanceof Date ? date : new Date(date);
        const start = new Date(serverInfo.weekStart);
        const end = new Date(serverInfo.weekEnd);
        
        // Normaliser les dates (ignorer les heures)
        start.setHours(0, 0, 0, 0);
        end.setHours(23, 59, 59, 999);
        checkDate.setHours(12, 0, 0, 0); // Midi pour éviter les problèmes de fuseau horaire
        
        return checkDate >= start && checkDate <= end;
    }

    /**
     * Formate une date au format YYYY-MM-DD pour les inputs HTML de type date
     * @param {Date} date - L'objet Date à formater
     * @returns {string} La date formatée en YYYY-MM-DD
     */
    function formatDateForInput(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    /**
     * Définit la date d'échéance d'un élément input à la fin de la semaine en cours
     * @param {string} inputId - L'identifiant de l'élément input
     */
    function setCurrentWeekDueDate(inputId = 'due_date') {
        const sunday = getCurrentWeekEndDate();
        document.getElementById(inputId).value = formatDateForInput(sunday);
    }

    /**
     * Définit la date d'échéance d'un élément input à la fin de la semaine prochaine
     * @param {string} inputId - L'identifiant de l'élément input
     */
    function setNextWeekDueDate(inputId = 'due_date') {
        const nextSunday = getNextWeekEndDate();
        document.getElementById(inputId).value = formatDateForInput(nextSunday);
    }

    /**
     * Ajoute un nombre spécifié de jours à une date
     * @param {Date} date - La date de départ
     * @param {number} days - Le nombre de jours à ajouter
     * @returns {Date} La nouvelle date
     */
    function addDays(date, days) {
        const result = new Date(date);
        result.setDate(date.getDate() + days);
        return result;
    }

    /**
     * Formate une date selon la locale française (JJ/MM/AAAA)
     * @param {Date} date - La date à formater
     * @returns {string} La date formatée
     */
    function formatDateFR(date) {
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
    }

    /**
     * Retourne la date du lundi d'une semaine donnée
     * @param {Date} date - Une date dans la semaine
     * @returns {Date} La date du lundi de la semaine
     */
    function getMonday(date) {
        const d = new Date(date);
        const day = d.getDay();
        const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Adjust when day is Sunday
        return new Date(d.setDate(diff));
    }

    /**
     * Formate une date au format "jour de semaine abrégé + jour du mois + mois abrégé" (ex: "lun 01 jan")
     * @param {string|Date} dateStr - La date à formater (objet Date ou chaîne ISO)
     * @returns {string} La date formatée
     */
    function formatDueDateShort(dateStr) {
        if (!dateStr) return '';
        
        try {
            const date = dateStr instanceof Date ? dateStr : new Date(dateStr);
            if (isNaN(date)) return dateStr;
            
            // Jours de la semaine en français
            const weekdays = ['dim', 'lun', 'mar', 'mer', 'jeu', 'ven', 'sam'];
            
            // Mois en français
            const months = ['jan', 'fév', 'mar', 'avr', 'mai', 'juin', 'juil', 'aoû', 'sep', 'oct', 'nov', 'déc'];
            
            // Formater comme "jou JJ/MM" (mise à jour pour correspondre au format du serveur)
            const dayOfWeek = weekdays[date.getDay()];
            const dayOfMonth = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            
            return `${dayOfWeek} ${dayOfMonth}/${month}`;
        } catch (e) {
            console.error('Error formatting date:', e);
            return dateStr;
        }
    }

    /**
     * Récupère les informations d'un jour spécifique
     * @param {string} dateStr - Date ISO (YYYY-MM-DD)
     * @returns {Object|null} Informations sur le jour ou null si non trouvé
     */
    function getDayInfo(dateStr) {
        if (!serverInfo || !serverInfo.days) return null;
        
        return serverInfo.days.find(day => day.date === dateStr) || null;
    }

    // API publique
    return {
        initWithServerInfo,
        getCurrentWeekBounds,
        getCurrentWeekEndDate,
        getNextWeekEndDate,
        getWeekTitle,
        isDateInCurrentWeek,
        formatDateForInput,
        setCurrentWeekDueDate,
        setNextWeekDueDate,
        addDays,
        formatDateFR,
        getMonday,
        formatDueDateShort,
        getDayInfo
    };
})();

// Exposer globalement
window.DateUtils = DateUtils;