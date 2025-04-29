"""
File: app/utils/wip_utils.py
Role: Utilitaires de calcul de la limite de travail en cours (WIP limit)
Description: Fournit des fonctions pour calculer et évaluer la limite de travail 
             en cours basée sur les durées des activités, sans interaction directe avec la base de données
Input data: Durées d'activités, listes d'activités (fournies par les contrôleurs)
Output data: Statistiques de WIP limit, nombre d'unités de temps, statut de la limite
Business constraints:
- Chaque activité a une durée (S, M, L) correspondant à un nombre spécifique d'unités de temps
- La WIP limit est définie dans les paramètres de l'application et s'applique à la semaine entière
"""

from typing import Dict, List, Union, Optional
from app.models.activity import DurationSize


def calculate_time_units(duration: str) -> int:
    """
    Calcule le nombre d'unités de temps pour une durée donnée
    
    Args:
        duration: Code de durée ('S', 'M' ou 'L')
        
    Returns:
        int: Nombre d'unités de temps
    """
    duration_map = {
        'S': 1,  # Small = 1 unité
        'M': 3,  # Medium = 3 unités
        'L': 6   # Large = 6 unités
    }
    
    # Gérer le cas où duration peut être un DurationSize.value ou une chaîne
    if isinstance(duration, DurationSize):
        duration = duration.value
        
    return duration_map.get(duration.upper(), 0)


def calculate_activities_stats(activities: List) -> Dict:
    """
    Calcule les statistiques liées aux activités
    
    Args:
        activities: Liste d'objets activités
        
    Returns:
        dict: Statistiques des activités
            - total_time_units: Nombre total d'unités de temps
            - activities_count: Nombre total d'activités
            - activities_by_duration: Répartition par durée (S, M, L)
            - completed_count: Nombre d'activités terminées
            - completion_rate: Taux de complétion en pourcentage
    """
    # Initialiser les compteurs
    total_units = 0
    duration_counts = {'S': 0, 'M': 0, 'L': 0}
    completed_count = 0
    
    # Parcourir les activités
    for activity in activities:
        # Obtenir la valeur de l'énumération si c'est un objet DurationSize
        duration_value = activity.duration.value if isinstance(activity.duration, DurationSize) else activity.duration
        
        # Calculer les unités de temps
        units = calculate_time_units(duration_value)
        total_units += units
        
        # Incrémenter le compteur de durée
        if duration_value in duration_counts:
            duration_counts[duration_value] += 1
        
        # Compter les activités terminées
        if activity.is_completed:
            completed_count += 1
    
    # Calculer le taux de complétion
    activities_count = len(activities)
    completion_rate = (completed_count / activities_count * 100) if activities_count > 0 else 0
    
    return {
        "total_time_units": total_units,
        "activities_count": activities_count,
        "activities_by_duration": duration_counts,
        "completed_count": completed_count,
        "completion_rate": round(completion_rate, 1)
    }


def evaluate_wip_limit_status(total_units: int, wip_limit: int) -> Dict:
    """
    Évalue le statut de la WIP limit par rapport au total d'unités
    
    Args:
        total_units: Nombre total d'unités de temps
        wip_limit: Valeur limite définie dans les paramètres
        
    Returns:
        dict: Évaluation du statut de la WIP limit
            - status: 'under', 'reached' ou 'exceeded'
            - percentage: Pourcentage d'utilisation de la limite
    """
    # Déterminer le statut
    status = "under"
    if total_units > wip_limit:
        status = "exceeded"
    elif total_units == wip_limit:
        status = "reached"
    
    # Calculer le pourcentage d'utilisation
    percentage = (total_units / wip_limit * 100) if wip_limit > 0 else 0
    
    return {
        "status": status,
        "percentage": round(percentage, 1)
    }


def get_wip_status_color(status: str) -> str:
    """
    Retourne la classe CSS de couleur correspondant au statut de la WIP limit
    
    Args:
        status: Statut de la WIP limit ('under', 'reached' ou 'exceeded')
        
    Returns:
        str: Classe CSS pour la couleur (vert, orange ou rouge)
    """
    status_colors = {
        "under": "text-green-600",
        "reached": "text-orange-500",
        "exceeded": "text-red-600"
    }
    return status_colors.get(status, "text-gray-700")