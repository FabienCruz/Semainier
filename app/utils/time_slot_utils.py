"""
File: app/utils/time_slot_utils.py
Role: Utilitaires pour la gestion des créneaux horaires
Description: Fournit des fonctions d'aide pour générer et formater les créneaux horaires
             utilisés dans la colonne "Emploi du temps"
Input data: Paramètres d'unité de temps, heure de début, nombre d'unités
Output data: Créneaux horaires, formatage d'affichage
Business constraints:
- Les créneaux sont basés sur les paramètres de l'application (unité de temps, heure de début)
"""

from datetime import datetime, timedelta


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
    try:
        start_time = datetime.strptime(start_time_str, "%H:%M")
    except ValueError:
        # En cas d'erreur de format, utiliser une valeur par défaut
        start_time = datetime.strptime("09:00", "%H:%M")
    
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
    try:
        start_time = datetime.strptime(start_time_str, "%H:%M")
    except ValueError:
        # En cas d'erreur de format, utiliser une valeur par défaut
        start_time = datetime.strptime("09:00", "%H:%M")
    
    total_minutes = time_unit_minutes * units_per_day
    end_time = start_time + timedelta(minutes=total_minutes)
    return end_time.strftime("%H:%M")


def format_time_for_display(time_str):
    """
    Formate une heure au format "HH:MM" pour l'affichage
    
    Args:
        time_str: Heure au format "HH:MM"
        
    Returns:
        str: Heure formatée pour l'affichage (ex: "9h00", "14h30")
    """
    try:
        time_obj = datetime.strptime(time_str, "%H:%M")
        return time_obj.strftime("%-Hh%M").replace("h00", "h")
    except ValueError:
        return time_str
