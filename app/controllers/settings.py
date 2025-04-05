"""
File: app/controllers/settings.py
Role: Contrôleur pour la gestion des paramètres de l'application
Description: Définit les routes API pour récupérer et mettre à jour les paramètres de l'application
Input data: Requêtes HTTP GET et PUT avec données JSON
Output data: Réponses JSON avec les paramètres ou messages d'erreur
Business constraints:
- Les paramètres doivent être validés selon les règles définies dans settings_utils.py
- Une seule entrée de paramètres est autorisée dans la base de données
"""

from flask import Blueprint, jsonify, request, render_template
from app import db
from app.models.settings import Settings
from app.utils.settings_utils import get_settings, validate_settings_input, convert_settings_input
from app.utils.request_format_utils import parse_request_data

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/api/settings', methods=['GET'])
def get_app_settings():
    """
    Récupère les paramètres actuels de l'application
    
    Returns:
        JSON: Réponse contenant les paramètres actuels
    """
    settings = get_settings(db.session)
    
    # Ajouter des informations calculées
    settings_dict = settings.to_dict()
    
    return jsonify({
        'success': True,
        'data': settings_dict
    })


@settings_bp.route('/api/settings', methods=['PUT', 'POST'])
@parse_request_data
def update_settings():
    """
    Met à jour les paramètres de l'application
    
    Données attendues (JSON/Form):
        time_unit_minutes: Durée d'une unité de temps (5-60, multiple de 5)
        day_start_time: Heure de début de journée (format HH:MM)
        time_units_per_day: Nombre d'unités par jour (entier positif)
        wip_limit: Limite de travail en cours (entier positif)
    
    Returns:
        JSON: Réponse indiquant le succès ou l'échec de la mise à jour
    """
    # Récupérer les données (JSON ou form-data)
    data = request.parsed_data
    
    # Valider les données
    is_valid, errors = validate_settings_input(data)
    
    if not is_valid:
        return jsonify({
            'success': False,
            'error': 'Données invalides',
            'errors': errors
        }), 400
    
    # Convertir les données
    converted_data = convert_settings_input(data)
    
    # Récupérer les paramètres actuels
    settings = get_settings(db.session)
    
    # Mettre à jour les paramètres
    for key, value in converted_data.items():
        setattr(settings, key, value)
    
    # Valider une dernière fois avec le modèle (double validation)
    is_model_valid, model_errors = settings.validate()
    
    if not is_model_valid:
        return jsonify({
            'success': False,
            'error': 'Validation du modèle échouée',
            'errors': model_errors
        }), 400
    
    # Sauvegarder les modifications
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': settings.to_dict(),
        'message': 'Paramètres mis à jour avec succès'
    })


@settings_bp.route('/api/settings/check-units-per-day', methods=['GET'])
def check_units_per_day():
    """
    Calcule la suggestion d'unités par jour pour une unité de temps donnée
    
    Query Parameters:
        time_unit_minutes: Durée d'une unité de temps en minutes
    
    Returns:
        JSON: Nombre suggéré d'unités par jour
    """
    from app.utils.settings_utils import calculate_suggested_units_per_day
    
    time_unit = request.args.get('time_unit_minutes', type=int)
    
    if not time_unit or time_unit < 5 or time_unit > 60 or time_unit % 5 != 0:
        return jsonify({
            'success': False,
            'error': 'Unité de temps invalide'
        }), 400
    
    suggested_units = calculate_suggested_units_per_day(time_unit)
    max_weekly_units = suggested_units * 7
    
    return jsonify({
        'success': True,
        'data': {
            'suggested_units_per_day': suggested_units,
            'max_weekly_units': max_weekly_units,
            'time_unit_minutes': time_unit
        }
    })


@settings_bp.route('/api/settings/time-slots', methods=['GET'])
def get_time_slots():
    """
    Récupère les créneaux horaires calculés à partir des paramètres actuels
    
    Returns:
        JSON: Liste des créneaux horaires au format HH:MM
    """
    from app.utils.settings_utils import generate_time_slots, calculate_day_end_time
    
    settings = get_settings(db.session)
    
    slots = generate_time_slots(
        settings.day_start_time,
        settings.time_unit_minutes,
        settings.time_units_per_day
    )
    
    day_end_time = calculate_day_end_time(
        settings.day_start_time,
        settings.time_unit_minutes,
        settings.time_units_per_day
    )
    
    return jsonify({
        'success': True,
        'data': {
            'time_unit_minutes': settings.time_unit_minutes,
            'day_start_time': settings.day_start_time,
            'time_units_per_day': settings.time_units_per_day,
            'day_end_time': day_end_time,
            'slots': slots
        }
    })


@settings_bp.route('/settings', methods=['GET'])
def settings_page():
    """
    Affiche la page de paramétrage
    
    Returns:
        HTML: Page de paramétrage
    """
    settings = get_settings(db.session)
    
    return render_template('pages/settings.html', settings=settings)