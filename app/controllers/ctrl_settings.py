"""
app/controllers/ctrl_settings.py

Rôle fonctionnel: Contrôleur métier pour les paramètres de l'application

Description: Ce fichier contient la logique métier pour les opérations sur les paramètres
de l'application, sans aucune référence aux routes HTTP ou au routage. Il sert de couche
intermédiaire entre le routeur et le modèle Settings.

Données attendues: 
- Paramètres directs ou dictionnaires de données
- Format des données défini dans le dictionnaire de données:
  - time_unit_minutes: Integer (5-60, multiple de 5)
  - day_start_time: String au format HH:MM
  - time_units_per_day: Integer (positif)
  - wip_limit: Integer (positif, max = time_units_per_day × 7)

Données produites:
- Objets métier, tuples (succès/échec, données/message) ou dictionnaires
- Aucun objet de réponse HTTP (pas de jsonify, render_template, etc.)

Contraintes:
- Une seule entrée de paramètres est autorisée dans la base de données
- Les paramètres doivent être validés selon les règles définies
"""

from app.models.settings import Settings
from app.utils.settings_utils import (
    validate_settings_input, convert_settings_input,
    calculate_suggested_units_per_day, generate_time_slots,
    calculate_day_end_time
)

def get_settings():
    """
    Récupère les paramètres actuels de l'application.
    
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objet Settings)
            - Si échec: (False, message d'erreur)
    """
    try:
        settings = Settings.get_settings()
        if not settings:
            return False, "Aucun paramètre trouvé, la base de données n'a pas été correctement initialisée"
        return True, settings
    except Exception as e:
        return False, f"Erreur lors de la récupération des paramètres: {str(e)}"

def update_settings(data):
    """
    Met à jour les paramètres de l'application.
    
    Args:
        data (dict): Dictionnaire contenant les données des paramètres
            - time_unit_minutes: Durée d'une unité de temps (requis)
            - day_start_time: Heure de début de journée (requis)
            - time_units_per_day: Nombre d'unités par jour (requis)
            - wip_limit: Limite de travail en cours (requis)
    
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objet Settings mis à jour)
            - Si échec: (False, message d'erreur ou dict d'erreurs)
    """
    # Valider les données
    is_valid, errors = validate_settings_input(data)
    if not is_valid:
        return False, errors
    
    # Convertir les données
    converted_data = convert_settings_input(data)
    
    try:
        # Mettre à jour les paramètres
        updated_settings = Settings.update(converted_data)
        if not updated_settings:
            return False, "Erreur lors de la mise à jour des paramètres"
        
        return True, updated_settings
    except Exception as e:
        return False, f"Erreur lors de la mise à jour des paramètres: {str(e)}"

def calculate_units_suggestion(time_unit_minutes):
    """
    Calcule la suggestion d'unités par jour pour une unité de temps donnée.
    
    Args:
        time_unit_minutes (int): Durée d'une unité de temps en minutes
        
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, dict contenant les données calculées)
            - Si échec: (False, message d'erreur)
    """
    # Validation basique
    if not time_unit_minutes or time_unit_minutes < 5 or time_unit_minutes > 60 or time_unit_minutes % 5 != 0:
        return False, "Unité de temps invalide"
    
    suggested_units = calculate_suggested_units_per_day(time_unit_minutes)
    max_weekly_units = suggested_units * 7
    
    return True, {
        'suggested_units_per_day': suggested_units,
        'max_weekly_units': max_weekly_units,
        'time_unit_minutes': time_unit_minutes
    }

def get_time_slots():
    """
    Récupère les créneaux horaires calculés à partir des paramètres actuels.
    
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, dict contenant les créneaux et infos)
            - Si échec: (False, message d'erreur)
    """
    try:
        success, settings_or_error = get_settings()
        if not success:
            return False, settings_or_error
        
        settings = settings_or_error
        
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
        
        return True, {
            'time_unit_minutes': settings.time_unit_minutes,
            'day_start_time': settings.day_start_time,
            'time_units_per_day': settings.time_units_per_day,
            'day_end_time': day_end_time,
            'slots': slots
        }
    except Exception as e:
        return False, f"Erreur lors de la génération des créneaux horaires: {str(e)}"