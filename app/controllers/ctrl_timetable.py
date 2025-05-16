"""
app/controllers/ctrl_timetable.py

Rôle fonctionnel: Contrôleur métier pour la gestion de l'emploi du temps

Description: Ce fichier contient la logique métier pour les opérations sur l'emploi du temps,
sans aucune référence aux routes HTTP ou au routage. Il sert de couche intermédiaire entre
le routeur et les différents utilitaires et modèles nécessaires.

Données attendues: 
- Paramètres directs (dates, directions de navigation)
- Format des données défini dans les spécifications

Données produites:
- Dictionnaires structurés avec les informations d'emploi du temps
- Aucun objet de réponse HTTP (pas de jsonify, render_template, etc.)

Contraintes:
- Les jours sont limités à la semaine courante
- Les jours passés sont en lecture seule
- Les créneaux horaires dépendent des paramètres de l'application
"""

from datetime import datetime, timedelta
from app.utils.date_utils import get_week_bounds, format_date_full_short, get_date_status
from app.utils.time_slot_utils import generate_time_slots, format_time_for_display
from app.models.settings import Settings
from app.models.activity import Activity

def get_timetable_day_info(target_date):
    """
    Récupère les informations d'un jour spécifique pour l'emploi du temps.
    
    Args:
        target_date (date): Date pour laquelle récupérer les informations
    
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, dict contenant les informations du jour)
            - Si échec: (False, message d'erreur)
    """
    try:
        # Informations sur le jour
        week_start, week_end = get_week_bounds()
        day_status = get_date_status(target_date)
        
        day_info = {
            'date': target_date.strftime('%Y-%m-%d'),
            'display_date': format_date_full_short(target_date),
            'day_name': target_date.strftime('%A'),
            'is_past': day_status == 'past',
            'is_today': day_status == 'today',
            'is_future': day_status == 'future',
            'is_first_day': target_date <= week_start,
            'is_last_day': target_date >= week_end
        }
        
        return True, day_info
    except Exception as e:
        return False, f"Erreur lors de la récupération des informations du jour: {str(e)}"

def navigate_to_day(current_date, direction):
    """
    Calcule la date cible en fonction de la direction de navigation.
    
    Args:
        current_date (date): Date actuellement affichée
        direction (str): Direction de navigation ('prev' ou 'next')
    
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, date cible)
            - Si échec: (False, message d'erreur)
    """
    try:
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
        
        return True, target_date
    except Exception as e:
        return False, f"Erreur lors du calcul de la date cible: {str(e)}"

def get_timetable_data(target_date):
    """
    Récupère toutes les données nécessaires pour afficher l'emploi du temps d'un jour.
    
    Args:
        target_date (date): Date pour laquelle récupérer les données
    
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, dict contenant toutes les données de l'emploi du temps)
            - Si échec: (False, message d'erreur)
    """
    try:
        # Récupérer les paramètres de l'application
        settings = Settings.get_settings()
        if not settings:
            return False, "Impossible de récupérer les paramètres de l'application"
        
        # Générer les créneaux horaires
        time_slots = generate_time_slots(
            settings.day_start_time,
            settings.time_unit_minutes,
            settings.time_units_per_day
        )
        
        # Formater les créneaux pour l'affichage
        formatted_slots = [format_time_for_display(slot) for slot in time_slots]
        
        # Récupérer les informations du jour
        success, day_info = get_timetable_day_info(target_date)
        if not success:
            return False, day_info
        
        # Récupérer les activités pour ce jour (à implémenter plus tard)
        activities = []  # Activity.get_by_date(target_date)
        
        # Combiner toutes les données
        timetable_data = {
            'day_info': day_info,
            'time_slots': time_slots,
            'formatted_slots': formatted_slots,
            'settings': settings.to_dict(),
            'activities': activities  # Liste vide pour l'instant
        }
        
        return True, timetable_data
    except Exception as e:
        return False, f"Erreur lors de la récupération des données de l'emploi du temps: {str(e)}"

def get_timetable_api_data(target_date, include_slots=True):
    """
    Prépare les données au format API pour l'emploi du temps d'un jour.
    
    Args:
        target_date (date): Date pour laquelle récupérer les données
        include_slots (bool, optional): Si True, inclut tous les créneaux horaires
        
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, dict formaté pour l'API)
            - Si échec: (False, message d'erreur)
    """
    try:
        # Récupérer les données de l'emploi du temps
        success, timetable_data = get_timetable_data(target_date)
        if not success:
            return False, timetable_data
        
        # Extraire les informations nécessaires
        day_info = timetable_data['day_info']
        time_slots = timetable_data['time_slots']
        activities = timetable_data['activities']
        
        # Créer la structure de données API
        api_data = {
            'date': day_info['date'],
            'day_name': day_info['day_name'],
            'is_past': day_info['is_past'],
            'is_today': day_info['is_today'],
            'is_future': day_info['is_future'],
            'activities': activities  # À convertir en dictionnaires si ce sont des objets
        }
        
        # Ajouter les créneaux horaires si demandé
        if include_slots:
            api_data['time_slots'] = []
            for slot in time_slots:
                # Pour chaque créneau, indiquer s'il est occupé par une activité
                slot_info = {
                    'time': slot,
                    'is_occupied': False,  # À déterminer selon les activités
                    'activity_id': None  # À remplir si occupé
                }
                api_data['time_slots'].append(slot_info)
        
        return True, api_data
    except Exception as e:
        return False, f"Erreur lors de la préparation des données API: {str(e)}"

def check_timetable_availability(date_str, start_time, duration, exclude_activity_id=None):
    """
    Vérifie la disponibilité des créneaux pour une activité.
    
    Args:
        date_str (str): Date au format YYYY-MM-DD
        start_time (str): Heure de début au format HH:MM
        duration (str): Durée (S/M/L)
        exclude_activity_id (int, optional): ID de l'activité à exclure
        
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, dict contenant les informations de disponibilité)
            - Si échec: (False, message d'erreur)
    """
    # Cette fonction sera implémentée plus tard
    # Elle vérifiera si les créneaux demandés sont disponibles pour placer une activité
    
    # Pour l'instant, retourner une disponibilité positive
    return True, {
        'is_available': True,
        'required_slots': [start_time],  # À remplacer par la liste complète des créneaux nécessaires
        'conflicts': []  # Activités en conflit, le cas échéant
    }