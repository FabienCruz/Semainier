"""
app/controllers/ctrl_weekly_goal.py

Rôle fonctionnel: Contrôleur métier pour les objectifs hebdomadaires

Description: Ce fichier contient la logique métier pour les opérations sur les objectifs
hebdomadaires, sans aucune référence aux routes HTTP ou au routage. Il sert de couche
intermédiaire entre le routeur et le modèle WeeklyGoal.

Données attendues: 
- Paramètres directs ou dictionnaires de données
- Format des données défini dans le dictionnaire de données:
  - week_start: Date de début de semaine (lundi)
  - content: Contenu textuel des objectifs (max 500 caractères)

Données produites:
- Objets métier, tuples (succès/échec, données/message)
- Aucun objet de réponse HTTP (pas de jsonify, render_template, etc.)

Contraintes:
- Une seule entrée par semaine est autorisée
- Le contenu textuel est limité à 500 caractères maximum
"""

from app.models.weekly_goals import WeeklyGoal
from app.utils.date_utils import get_week_info_for_date
from datetime import date

def get_weekly_goal(week_start=None):
    """
    Récupère l'objectif textuel d'une semaine spécifique ou de la semaine en cours.
    
    Args:
        week_start (date, optional): Date de début de semaine (lundi)
        
    Returns:
        tuple: (succès, données/message)
            - Si succès et objectif trouvé: (True, objectif)
            - Si succès mais aucun objectif: (True, None)
            - Si échec: (False, message d'erreur)
    """
    try:
        # Si aucune date n'est fournie, utiliser la date du jour
        current_date = date.today() if week_start is None else week_start
        
        # Obtenir l'objectif de la semaine
        if week_start is None:
            weekly_goal = WeeklyGoal.get_current_week_goal()
        else:
            weekly_goal = WeeklyGoal.get_by_week_start(week_start)
        
        # Retourner l'objectif (même si None)
        return True, weekly_goal
    except Exception as e:
        return False, f"Erreur lors de la récupération de l'objectif: {str(e)}"

def create_or_update_weekly_goal(content, week_start=None):
    """
    Crée ou met à jour l'objectif d'une semaine spécifique ou de la semaine en cours.
    
    Args:
        content (str): Contenu textuel des objectifs
        week_start (date, optional): Date de début de semaine (lundi)
        
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objectif mis à jour)
            - Si échec: (False, message d'erreur)
    """
    # Validation du contenu
    if not content:
        return False, "Le contenu ne peut pas être vide"
    
    if len(content) > 500:
        return False, "Le contenu est limité à 500 caractères"
    
    try:
        # Si aucune date n'est fournie, utiliser la date du jour
        if week_start is None:
            week_start = date.today()
        
        # Créer ou mettre à jour l'objectif
        success, result = WeeklyGoal.create_or_update(week_start, content)
        if not success:
            return False, result
        
        return True, result
    except Exception as e:
        return False, f"Erreur lors de la création/mise à jour de l'objectif: {str(e)}"

def get_weekly_goal_with_week_info(week_start=None):
    """
    Récupère l'objectif textuel d'une semaine avec les informations de la semaine.
    
    Args:
        week_start (date, optional): Date de début de semaine (lundi)
        
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, dict contenant l'objectif et les infos de la semaine)
            - Si échec: (False, message d'erreur)
    """
    try:
        # Récupérer l'objectif
        success, weekly_goal = get_weekly_goal(week_start)
        if not success:
            return False, weekly_goal
        
        # Si aucune date n'est fournie, utiliser la date du jour
        current_date = date.today() if week_start is None else week_start
        
        # Obtenir les informations de la semaine
        week_info = get_week_info_for_date(current_date)
        
        # Créer un dictionnaire de réponse
        response_data = {
            'week_start': week_info['week_start'],
            'week_end': week_info['week_end'],
            'week_display': week_info['display_range'],
            'days': week_info['days'],
            'content': weekly_goal.content if weekly_goal else "",
        }
        
        # Ajouter les infos de l'objectif s'il existe
        if weekly_goal:
            response_data.update({
                'id': weekly_goal.id,
                'created_at': weekly_goal.created_at.isoformat() if weekly_goal.created_at else None,
                'updated_at': weekly_goal.updated_at.isoformat() if weekly_goal.updated_at else None
            })
        
        return True, response_data
    except Exception as e:
        return False, f"Erreur lors de la récupération des informations: {str(e)}"