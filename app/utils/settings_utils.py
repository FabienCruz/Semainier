"""
File: app/utils/settings_utils.py
Role: Utilitaires pour la gestion des paramètres de l'application
Description: Fournit des fonctions d'aide pour manipuler et calculer des valeurs 
             basées sur les paramètres de l'application (Settings)
Input data: Objets Settings, valeurs de paramètres individuels
Output data: Valeurs calculées, créneaux horaires, validations
Business constraints:
- L'unité de temps doit être entre 5 et 60 minutes par palier de 5
- Le nombre d'unités par jour et la WIP limit doivent suivre les contraintes du modèle Settings
"""

from datetime import datetime, timedelta
from app.models.settings import Settings


def get_settings(db_session):
    """
    Récupère les paramètres de l'application, crée des valeurs par défaut si nécessaire
    
    Args:
        db_session: Session de base de données
        
    Returns:
        Settings: Objet contenant les paramètres
    """
    return Settings.get_settings(db_session)


def calculate_suggested_units_per_day(time_unit_minutes):
    """
    Calcule le nombre suggéré d'unités par jour basé sur une journée de 10 heures
    
    Args:
        time_unit_minutes: Durée d'une unité de temps en minutes
        
    Returns:
        int: Nombre suggéré d'unités par jour
    """
    # Base de calcul : 600 minutes (10 heures)
    return round(600 / time_unit_minutes)


def calculate_max_weekly_units(units_per_day):
    """
    Calcule le nombre maximum d'unités pour une semaine
    
    Args:
        units_per_day: Nombre d'unités par jour
        
    Returns:
        int: Nombre maximum d'unités par semaine
    """
    return units_per_day * 7


def generate_time_slots(start_time_str, time_unit_minutes, units_per_day):
    """
    Génère les créneaux horaires pour l'emploi du temps
    
    Args:
        start_time_str: Heure de début au format "HH:MM"
        time_unit_minutes: Durée d'une unité en minutes
        units_per_day: Nombre d'unités par jour
        
    Returns:
        list: Liste des créneaux horaires au format "HH:MM"
    """
    # Convertir l'heure de début en datetime
    start_time = datetime.strptime(start_time_str, "%H:%M")
    
    # Générer les créneaux
    slots = []
    for i in range(units_per_day):
        time_delta = timedelta(minutes=time_unit_minutes * i)
        slot_time = start_time + time_delta
        slots.append(slot_time.strftime("%H:%M"))
    
    return slots


def calculate_day_end_time(start_time_str, time_unit_minutes, units_per_day):
    """
    Calcule l'heure de fin de journée en fonction des paramètres
    
    Args:
        start_time_str: Heure de début au format "HH:MM"
        time_unit_minutes: Durée d'une unité en minutes
        units_per_day: Nombre d'unités par jour
        
    Returns:
        str: Heure de fin au format "HH:MM"
    """
    start_time = datetime.strptime(start_time_str, "%H:%M")
    total_minutes = time_unit_minutes * units_per_day
    end_time = start_time + timedelta(minutes=total_minutes)
    return end_time.strftime("%H:%M")


def validate_settings_input(data):
    """
    Valide les données d'entrée pour la mise à jour des paramètres
    
    Args:
        data: Dictionnaire contenant les paramètres à valider
        
    Returns:
        tuple: (is_valid, errors_dict)
    """
    errors = {}
    
    # Vérifier si les clés requises sont présentes
    required_keys = ['time_unit_minutes', 'day_start_time', 'time_units_per_day', 'wip_limit']
    for key in required_keys:
        if key not in data:
            errors[key] = f"Le champ {key} est requis"
    
    # Arrêter la validation si des clés sont manquantes
    if errors:
        return False, errors
    
    # Validation de time_unit_minutes
    try:
        time_unit = int(data['time_unit_minutes'])
        if time_unit < 5 or time_unit > 60:
            errors['time_unit_minutes'] = "L'unité de temps doit être entre 5 et 60 minutes"
        elif time_unit % 5 != 0:
            errors['time_unit_minutes'] = "L'unité de temps doit être un multiple de 5"
    except (ValueError, TypeError):
        errors['time_unit_minutes'] = "L'unité de temps doit être un nombre entier"
    
    # Validation de day_start_time
    try:
        start_time = data['day_start_time']
        datetime.strptime(start_time, "%H:%M")
        hours, minutes = map(int, start_time.split(':'))
        if minutes % 5 != 0:
            errors['day_start_time'] = "Les minutes doivent être par palier de 5"
    except ValueError:
        errors['day_start_time'] = "L'heure de début doit être au format HH:MM"
    
    # Validation de time_units_per_day
    try:
        units_per_day = int(data['time_units_per_day'])
        if units_per_day <= 0:
            errors['time_units_per_day'] = "Le nombre d'unités par jour doit être supérieur à 0"
    except (ValueError, TypeError):
        errors['time_units_per_day'] = "Le nombre d'unités par jour doit être un nombre entier"
    
    # Validation de wip_limit
    try:
        wip_limit = int(data['wip_limit'])
        units_per_day = int(data['time_units_per_day'])
        max_wip_limit = units_per_day * 7
        
        if wip_limit <= 0:
            errors['wip_limit'] = "La WIP limit doit être supérieure à 0"
        elif wip_limit > max_wip_limit:
            errors['wip_limit'] = f"La WIP limit ne peut pas dépasser {max_wip_limit} (time_units_per_day × 7)"
    except (ValueError, TypeError):
        errors['wip_limit'] = "La WIP limit doit être un nombre entier"
    
    return len(errors) == 0, errors


def convert_settings_input(data):
    """
    Convertit les données reçues du formulaire en types corrects pour le modèle Settings
    
    Args:
        data: Dictionnaire contenant les paramètres à convertir
        
    Returns:
        dict: Dictionnaire avec les valeurs converties
    """
    result = {}
    
    if 'time_unit_minutes' in data:
        result['time_unit_minutes'] = int(data['time_unit_minutes'])
    
    if 'day_start_time' in data:
        result['day_start_time'] = data['day_start_time']
    
    if 'time_units_per_day' in data:
        result['time_units_per_day'] = int(data['time_units_per_day'])
    
    if 'wip_limit' in data:
        result['wip_limit'] = int(data['wip_limit'])
    
    return result