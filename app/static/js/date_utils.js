// app/static/js/date_utils.js

/**
 * Utilitaires pour la manipulation de dates dans l'application Semainier
 */

/**
 * Calcule la date du dimanche de la semaine en cours
 * @returns {Date} Date du dimanche de la semaine en cours
 */
function getCurrentWeekEndDate() {
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
    const today = new Date();
    const dayOfWeek = today.getDay(); // 0 pour dimanche, 1 pour lundi, etc.
    const daysUntilNextSunday = dayOfWeek === 0 ? 7 : 14 - dayOfWeek;
    const nextSunday = new Date(today);
    nextSunday.setDate(today.getDate() + daysUntilNextSunday);
    return nextSunday;
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
    const day = date.getDay();
    const diff = date.getDate() - day + (day === 0 ? -6 : 1); // Adjust when day is Sunday
    return new Date(date.setDate(diff));
}
