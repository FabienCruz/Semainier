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

from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from datetime import datetime, timedelta
from app import db
from app.utils.date_utils import get_week_bounds, format_date_full_short, get_date_status
from app.utils.time_slot_utils import generate_time_slots, format_time_for_display
from app.controllers.settings import get_settings_obj

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
    # Obtenir les paramètres de l'application via la fonction du contrôleur settings
    try:
        settings = get_settings_obj()
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des paramètres: {str(e)}")
        return render_template('components/timetable_column.html', 
                              current_day_info={'display_date': 'Erreur de paramètres'},
                              time_slots=[])
    
    # Générer les créneaux horaires
    time_slots = generate_time_slots(
        settings.day_start_time,
        settings.time_unit_minutes,
        settings.time_units_per_day
    )
    
    # Formater les créneaux pour l'affichage (optionnel, si nécessaire)
    formatted_slots = [format_time_for_display(slot) for slot in time_slots]
    
    # Informations sur le jour
    week_start, week_end = get_week_bounds()
    day_status = get_date_status(date)
    
    current_day_info = {
        'date': date.strftime('%Y-%m-%d'),
        'display_date': format_date_full_short(date),
        'is_past': day_status == 'past',
        'is_today': day_status == 'today',
        'is_future': day_status == 'future',
        'is_first_day': date <= week_start,
        'is_last_day': date >= week_end
    }
    
    return render_template('components/timetable_column.html',
                          current_day_info=current_day_info,
                          time_slots=time_slots,
                          formatted_slots=formatted_slots,
                          settings=settings)


@bp.route('/api/timetable/day', methods=['GET'])
def get_timetable_day_api():
    """
    API pour récupérer les données de l'emploi du temps d'un jour spécifique
    
    Query Parameters:
        date: Date au format YYYY-MM-DD
    
    Returns:
        JSON: Données de l'emploi du temps pour le jour spécifié
    """
    try:
        # Récupérer la date depuis les paramètres
        date_str = request.args.get('date')
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            target_date = datetime.now().date()
        
        # Obtenir les paramètres
        settings = get_settings_obj()
        
        # Générer les créneaux horaires
        time_slots = generate_time_slots(
            settings.day_start_time,
            settings.time_unit_minutes,
            settings.time_units_per_day
        )
        
        # Informations sur le jour
        day_status = get_date_status(target_date)
        
        # Pour l'instant, retourner seulement les créneaux et infos basiques
        # Dans le futur, cette fonction pourrait retourner aussi les activités
        return jsonify({
            'success': True,
            'data': {
                'date': target_date.strftime('%Y-%m-%d'),
                'day_name': target_date.strftime('%A'),
                'is_past': day_status == 'past',
                'is_today': day_status == 'today',
                'is_future': day_status == 'future',
                'time_slots': time_slots,
                'activities': []  # Sera implémenté plus tard
            }
        })
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération de l'emploi du temps: {str(e)}")
        return jsonify({
            'success': False,
            'error': "Impossible de récupérer l'emploi du temps"
        }), 500
