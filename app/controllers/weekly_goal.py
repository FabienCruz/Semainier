"""
File: app/controllers/weekly_goal.py
Role: Contrôleur pour la gestion des objectifs hebdomadaires
Description: Fournit les routes API pour créer, récupérer et mettre à jour les objectifs textuels de la semaine
Input data: Requêtes HTTP avec contenu textuel des objectifs
Output data: Réponses JSON avec les données des objectifs hebdomadaires
Business constraints:
- Le contenu textuel est limité à 500 caractères maximum
- Une seule entrée par semaine est autorisée
"""

from flask import Blueprint, request, jsonify
from datetime import date
from app import db
from app.models.weekly_goals import WeeklyGoal
from app.utils.date_utils import get_server_date_info
from app.utils.request_format_utils import parse_request_data

# Création du blueprint
weekly_goal_bp = Blueprint('weekly_goal', __name__, url_prefix='/api/planning')

@weekly_goal_bp.route('/weekly-goal', methods=['GET'])
def get_weekly_goal():
    """Récupère l'objectif textuel de la semaine en cours"""
    # Récupérer les informations de la semaine courante
    week_info = get_server_date_info()
    start_date = date.fromisoformat(week_info['week_start'])
    
    # Rechercher l'objectif pour cette semaine
    weekly_goal = WeeklyGoal.query.filter_by(week_start=start_date).first()
    
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
                'week_start': week_info['week_start'],
                'week_end': week_info['week_end'],
                'content': "",
                'week_display': week_info['display_range'],
                'days': week_info['days']
            }
        })

@weekly_goal_bp.route('/weekly-goal', methods=['POST'])
@parse_request_data
def create_update_weekly_goal():
    """Crée ou met à jour l'objectif de la semaine courante
    
    Décorateur @parse_request_data: 
    - Analyse et convertit automatiquement les données envoyées quel que soit le format
    
    Données attendues:
    - content: Contenu textuel des objectifs (requis, max 500 caractères)
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
    
    # Récupérer les informations de la semaine courante
    week_info = get_server_date_info()
    start_date = date.fromisoformat(week_info['week_start'])
    
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