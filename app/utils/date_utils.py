"""
File: app/utils/date_utils.py
Role: Utilitaires de gestion des dates
Description: Fournit des fonctions pour manipuler et formater les dates, en particulier pour les calculs liés aux semaines
Input data: Objets de type date, datetime ou chaînes de caractères représentant des dates
Output data: Dates formatées, bornes de semaine, informations de semaine pour le contexte global
Business constraints:
- La semaine commence le lundi et se termine le dimanche
- Les formats courts utilisent des abréviations françaises pour les jours et mois
"""

from datetime import datetime, date, timedelta
from typing import Tuple, Union, Dict, Optional

def get_week_bounds(reference_date: Optional[Union[date, str]] = None) -> Tuple[date, date]:
    """
    Calcule les dates de début (lundi) et fin (dimanche) de la semaine
    
    Args:
        reference_date: Date de référence (aujourd'hui par défaut)
        
    Returns:
        tuple: (date_debut, date_fin)
    """
    if reference_date is None:
        reference_date = date.today()
    elif isinstance(reference_date, str):
        reference_date = datetime.strptime(reference_date, "%Y-%m-%d").date()
    
    # Calcul du lundi (0=lundi dans la norme ISO)
    weekday = reference_date.weekday()
    start_date = reference_date - timedelta(days=weekday)
    
    # Calcul du dimanche
    end_date = start_date + timedelta(days=6)
    
    return start_date, end_date

def format_date_short(dt: Union[date, datetime, None]) -> str:
    """
    Formate une date au format "JJ/MM" (ex: "01/03")
    
    Args:
        dt: Objet date ou datetime
        
    Returns:
        str: Date formatée
    """
    if not dt:
        return ""
    
    if isinstance(dt, datetime):
        dt = dt.date()
    
    return f"{dt.day:02d}/{dt.month:02d}"

def format_weekday_short(dt: Union[date, datetime, None]) -> str:
    """
    Formate le jour de la semaine en version courte (3 lettres)
    
    Args:
        dt: Objet date ou datetime
        
    Returns:
        str: Jour de la semaine formaté (ex: "lun")
    """
    if not dt:
        return ""
        
    if isinstance(dt, datetime):
        dt = dt.date()
        
    weekdays = ['lun', 'mar', 'mer', 'jeu', 'ven', 'sam', 'dim']
    return weekdays[dt.weekday()]

def format_date_full_short(dt: Union[date, datetime, None]) -> str:
    """
    Formate une date au format "jjj JJ/MM" (ex: "lun 01/03")
    
    Args:
        dt: Objet date ou datetime
        
    Returns:
        str: Date formatée
    """
    if not dt:
        return ""
    
    if isinstance(dt, datetime):
        dt = dt.date()
        
    return f"{format_weekday_short(dt)} {format_date_short(dt)}"

def get_server_date_info() -> Dict:
    """
    Génère les informations de date nécessaires pour le contexte global de l'application
    
    Returns:
        dict: Données de date pour le contexte de l'application, incluant:
            - current_date: Date actuelle au format ISO
            - week_start: Date du lundi de la semaine courante au format ISO
            - week_end: Date du dimanche de la semaine courante au format ISO
            - display_range: Plage de dates formatée pour affichage (ex: "lun 01/03 au dim 07/03")
            - days: Liste des informations sur chaque jour de la semaine
            - is_current_week: Booléen indiquant s'il s'agit de la semaine courante
    """
    today = date.today()
    start_date, end_date = get_week_bounds(today)
    
    days = []
    for i in range(7):
        day_date = start_date + timedelta(days=i)
        days.append({
            'date': day_date.isoformat(),
            'day_name': ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][i],
            'day_short': format_weekday_short(day_date),
            'display_date': format_date_full_short(day_date),
            'is_past': day_date < today,
            'is_today': day_date == today,
            'is_future': day_date > today
        })
    
    return {
        'current_date': today.isoformat(),
        'week_start': start_date.isoformat(),
        'week_end': end_date.isoformat(),
        'display_range': f"{format_date_full_short(start_date)} au {format_date_full_short(end_date)}",
        'days': days,
        'is_current_week': True  # Toujours vrai pour la semaine courante
    }

def get_date_status(date):
    """
    Détermine le statut d'une date par rapport à aujourd'hui
    
    Args:
        date: Date à vérifier
        
    Returns:
        str: 'past', 'today' ou 'future'
    """
    today = datetime.now().date()
    
    if date < today:
        return 'past'
    elif date > today:
        return 'future'
    else:
        return 'today'

def get_date_from_string(date_str: str) -> date:
    """
    Convertit une chaîne de caractères au format YYYY-MM-DD en objet date
    
    Args:
        date_str: Date au format YYYY-MM-DD
        
    Returns:
        date: Objet date correspondant
        
    Raises:
        ValueError: Si le format de date est invalide
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Format de date invalide: {date_str}. Format attendu: YYYY-MM-DD")