"""
File: app/controllers/weekly_goal.py
Role: Contrôleur pour la gestion des objectifs hebdomadaires
Description: Fournit les routes API pour créer, récupérer et mettre à jour les objectifs textuels de la semaine
Input data: Requêtes HTTP avec date de début de semaine et contenu textuel des objectifs
Output data: Réponses JSON avec les données des objectifs hebdomadaires
Business constraints:
- La date de début doit toujours être un lundi (ajustée automatiquement si nécessaire)
- Le contenu textuel est limité à 500 caractères maximum
- Une seule entrée par semaine est autorisée
"""

from flask import Blueprint, request, jsonify
from datetime import date, datetime
from app import db
from app.models.weekly_goals import WeeklyGoal
from app.utils.date_utils import get_week_bounds, get_week_info
from app.utils.request_format_utils import parse_request_data

# Création du blueprint
weekly_goal_bp = Blueprint('weekly_goal', __name__, url_prefix='/api/planning')

@weekly_goal_bp.route('/weekly-goal', methods=['GET'])
def get_weekly_goal():
    """Récupère l'objectif textuel de la semaine en cours ou d'une semaine spécifiée"""
    # Récupérer le paramètre de date (optionnel)
    week_start_param = request.args.get('week_start', None)
    
    # Déterminer la date de début de semaine
    if week_start_param:
        try:
            reference_date = datetime.strptime(week_start_param, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': "Format de date invalide. Utilisez YYYY-MM-DD."
            }), 400
    else:
        reference_date = date.today()
    
    # Calculer les bornes de la semaine
    start_date, _ = get_week_bounds(reference_date)
    
    # Rechercher l'objectif pour cette semaine
    weekly_goal = WeeklyGoal.query.filter_by(week_start=start_date).first()
    
    # Récupérer les informations de la semaine
    week_info = get_week_info(start_date)
    
    if weekly_goal:
        response_data = weekly_goal.to_dict()
        response_data.update({
            'week_display': week_info['display_range'],
            'days': week_info['days']
        })
        return jsonify({
            'success': True,
            'data': response_data
        })
    else:
        return jsonify({
            'success': True,
            'data': {
                'week_start': start_date.isoformat(),
                'week_end': week_info['week_end'],
                'content': "",
                'week_display': week_info['display_range'],
                'days': week_info['days']
            }
        })

@weekly_goal_bp.route('/weekly-goal', methods=['POST'])
@parse_request_data
def create_update_weekly_goal():
    """Crée ou met à jour l'objectif de la semaine
    
    Décorateur @parse_request_data: 
    - Analyse et convertit automatiquement les données envoyées quel que soit le format
    - Standardise les types de données pour les dates
    
    Données attendues:
    - content: Contenu textuel des objectifs (requis, max 500 caractères)
    - week_start: Date de début de semaine au format YYYY-MM-DD (optionnel)
    """
    # Grâce au décorateur, les données sont disponibles dans request.parsed_data
    data = request.parsed_data
    
    # Vérifier que les champs requis sont présents
    if 'content' not in data:
        return jsonify({
            'success': False,
            'error': "Le champ 'content' est requis."
        }), 400
    
    # Vérifier la longueur du contenu
    if len(data['content']) > 500:
        return jsonify({
            'success': False,
            'error': "Le contenu est limité à 500 caractères."
        }), 400
    
    # Déterminer la date de début de semaine
    week_start_param = data.get('week_start', None)
    if week_start_param:
        try:
            if isinstance(week_start_param, str):
                reference_date = datetime.strptime(week_start_param, "%Y-%m-%d").date()
            else:
                reference_date = week_start_param
        except ValueError:
            return jsonify({
                'success': False,
                'error': "Format de date invalide. Utilisez YYYY-MM-DD."
            }), 400
    else:
        reference_date = date.today()
    
    # Calculer les bornes de la semaine
    start_date, end_date = get_week_bounds(reference_date)
    
    # Rechercher si un objectif existe déjà pour cette semaine
    weekly_goal = WeeklyGoal.query.filter_by(week_start=start_date).first()
    
    if weekly_goal:
        # Mettre à jour l'objectif existant
        weekly_goal.content = data['content']
    else:
        # Créer un nouvel objectif
        weekly_goal = WeeklyGoal(week_start=start_date, content=data['content'])
        db.session.add(weekly_goal)
    
    # Sauvegarder les changements
    db.session.commit()
    
    # Récupérer les informations de la semaine
    week_info = get_week_info(start_date)
    
    # Préparer la réponse
    response_data = weekly_goal.to_dict()
    response_data.update({
        'week_display': week_info['display_range'],
        'days': week_info['days']
    })
    
    return jsonify({
        'success': True,
        'data': response_data
    })