"""
File: app/controllers/timetable.py
Role: Contrôleur pour la gestion de la colonne "Emploi du temps"
Description: Définit les routes pour afficher et manipuler la colonne "Emploi du temps"
Input data: Requêtes HTTP avec paramètres de date et navigation
Output data: Templates rendus avec les données de créneaux horaires
Business constraints:
- Les jours sont limités à la semaine courante
- Les jours passés sont en lecture seule
- Les créneaux horaires dépendent des paramètres de l'application
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import datetime, timedelta
from app import db
from app.models.settings import Settings
from app.utils.date_utils import get_week_bounds, format_date_short, get_date_status
from app.utils.time_slot_utils import generate_time_slots

bp = Blueprint('timetable', __name__)


@bp.route('/timetable', methods=['GET'])
def get_timetable_column():
    """
    Affiche la colonne "Emploi du temps" avec le jour courant
    
    Returns:
        HTML: Template de la colonne "Emploi du temps"
    """
    # Obtenir la date du jour
    today = datetime.now().date()
    return get_timetable_for_day(today)


@bp.route('/timetable/<direction>', methods=['GET'])
def navigate_timetable(direction):
    """
    Navigue vers le jour précédent ou suivant dans la colonne "Emploi du temps"
    
    Args:
        direction: Direction de navigation ('prev' ou 'next')
    
    Query Parameters:
        current_date: Date actuellement affichée (YYYY-MM-DD)
    
    Returns:
        HTML: Template de la colonne "Emploi du temps" pour le jour cible
    """
    # Récupérer la date actuelle depuis les paramètres de la requête
    current_date_str = request.args.get('current_date')
    
    try:
        current_date = datetime.strptime(current_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        # En cas d'erreur, utiliser la date du jour
        current_date = datetime.now().date()
    
    # Calculer la date cible selon la direction
    if direction == 'prev':
        target_date = current_date - timedelta(days=1)
    elif direction == 'next':
        target_date = current_date + timedelta(days=1)
    else:
        target_date = current_date
    
    # Limiter à la semaine courante
    week_start, week_end = get_week_bounds()
    if target_date < week_start:
        target_date = week_start
    elif target_date > week_end:
        target_date = week_end
    
    return get_timetable_for_day(target_date)


def get_timetable_for_day(date):
    """
    Prépare les données et rend le template pour un jour spécifique
    
    Args:
        date: Date pour laquelle afficher l'emploi du temps
    
    Returns:
        HTML: Template de la colonne "Emploi du temps"
    """
    # Obtenir les paramètres de l'application
    settings = db.session.query(Settings).first()
    if not settings:
        current_app.logger.error("Paramètres non trouvés. Assurez-vous que l'application a été correctement initialisée.")
        return render_template('components/timetable_column.html', 
                              current_day_info={'display_date': 'Erreur de paramètres'},
                              time_slots=[])
    
    # Générer les créneaux horaires
    time_slots = generate_time_slots(
        settings.day_start_time,
        settings.time_unit_minutes,
        settings.time_units_per_day
    )
    
    # Informations sur le jour
    week_start, week_end = get_week_bounds()
    day_status = get_date_status(date)
    
    current_day_info = {
        'date': date.strftime('%Y-%m-%d'),
        'display_date': format_date_short(date),
        'is_past': day_status == 'past',
        'is_today': day_status == 'today',
        'is_future': day_status == 'future',
        'is_first_day': date <= week_start,
        'is_last_day': date >= week_end
    }
    
    return render_template('components/timetable_column.html',
                          current_day_info=current_day_info,
                          time_slots=time_slots,
                          settings=settings)
