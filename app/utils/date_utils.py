"""
File: app/utils/date_utils.py
Role: Utilitaires de gestion des dates
Description: Fournit des fonctions pour manipuler et formater les dates, en particulier pour les calculs liés aux semaines
Input data: Objets de type date, datetime ou chaînes de caractères représentant des dates
Output data: Dates formatées, bornes de semaine, informations de semaine
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
    Formate une date au format "j mmm" (ex: "1 mar")
    
    Args:
        dt: Objet date ou datetime
        
    Returns:
        str: Date formatée
    """
    if not dt:
        return ""
    
    if isinstance(dt, datetime):
        dt = dt.date()
    
    months = ['jan', 'fév', 'mar', 'avr', 'mai', 'juin', 
              'juil', 'aoû', 'sep', 'oct', 'nov', 'déc']
    return f"{dt.day} {months[dt.month-1]}"

def get_week_column_title(reference_date: Optional[Union[date, str]] = None) -> str:
    """
    Génère le titre formaté pour la colonne "Objectifs de la semaine"
    
    Args:
        reference_date: Date de référence (aujourd'hui par défaut)
        
    Returns:
        str: Titre formaté (ex: "Semaine du 1 mar au 7 mar")
    """
    start_date, end_date = get_week_bounds(reference_date)
    return f"Semaine du {format_date_short(start_date)} au {format_date_short(end_date)}"

def is_date_in_current_week(check_date: Union[date, str]) -> bool:
    """
    Vérifie si une date se trouve dans la semaine en cours
    
    Args:
        check_date: Date à vérifier
        
    Returns:
        bool: True si dans la semaine courante
    """
    if isinstance(check_date, str):
        check_date = datetime.strptime(check_date, "%Y-%m-%d").date()
        
    start_date, end_date = get_week_bounds()
    return start_date <= check_date <= end_date

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
        
    return f"{format_weekday_short(dt)} {dt.day:02d}/{dt.month:02d}"

def get_week_info(reference_date: Optional[Union[date, str]] = None) -> Dict:
    """
    Récupère les informations complètes sur une semaine
    
    Args:
        reference_date: Date de référence dans la semaine (aujourd'hui par défaut)
        
    Returns:
        dict: Informations sur la semaine (dates de début/fin, titre, jours, etc.)
    """
    start_date, end_date = get_week_bounds(reference_date)
    today = date.today()
    
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
    
    is_current_week = is_date_in_current_week(start_date)
    
    return {
        'week_start': start_date.isoformat(),
        'week_end': end_date.isoformat(),
        'display_range': f"{format_date_short(start_date)} au {format_date_short(end_date)}",
        'days': days,
        'is_current_week': is_current_week
    }

def get_next_week_start() -> date:
    """
    Retourne la date de début de la semaine prochaine
    
    Returns:
        date: Date du lundi de la semaine prochaine
    """
    start_date, _ = get_week_bounds()
    return start_date + timedelta(days=7)

def get_previous_week_start() -> date:
    """
    Retourne la date de début de la semaine précédente
    
    Returns:
        date: Date du lundi de la semaine précédente
    """
    start_date, _ = get_week_bounds()
    return start_date - timedelta(days=7)