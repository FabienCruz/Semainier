from flask import Blueprint, request, jsonify
from app import db
from app.models import List, Sublist, Activity
from app.models.activity import DurationSize
from datetime import datetime, date, timedelta

# Création du Blueprint pour les routes d'activité
bp = Blueprint('activity', __name__, url_prefix='/api/activities')

@bp.route('/', methods=['GET'])
def get_activities():
    """Récupérer les activités avec possibilité de filtrage."""
    list_id = request.args.get('list_id', type=int)
    sublist_id = request.args.get('sublist_id', type=int)
    is_completed = request.args.get('is_completed', type=int)
    
    # Construction de la requête de base
    query = Activity.query
    
    # Application des filtres
    if list_id is not None:
        query = query.filter_by(list_id=list_id)
    if sublist_id is not None:
        query = query.filter_by(sublist_id=sublist_id)
    if is_completed is not None:
        query = query.filter_by(is_completed=bool(is_completed))
    
    # Récupération des résultats ordonnés
    activities = query.order_by(Activity.due_date, Activity.position).all()
    
    return jsonify([activity.to_dict() for activity in activities]), 200

@bp.route('/<int:id>', methods=['GET'])
def get_activity(id):
    """Récupérer une activité par son ID."""
    activity = db.session.get(Activity, id)
    if not activity:
        return jsonify({'error': 'Activité non trouvée'}), 404
    return jsonify(activity.to_dict()), 200

@bp.route('/', methods=['POST'])
def create_activity():
    """Créer une nouvelle activité."""
    data = request.get_json() or {}
    
    # Validation des données requises
    if 'title' not in data or 'list_id' not in data:
        return jsonify({'error': 'Le titre et l\'ID de la liste sont requis'}), 400
    
    # Vérification que la liste existe
    list_obj = db.session.get(List, data['list_id'])
    if not list_obj:
        return jsonify({'error': 'La liste spécifiée n\'existe pas'}), 404
    
    # Validation de la sous-liste si fournie
    if 'sublist_id' in data and data['sublist_id']:
        if not Activity.validate_sublist_belongs_to_list(data['list_id'], data['sublist_id']):
            return jsonify({'error': 'La sous-liste n\'appartient pas à la liste spécifiée'}), 400
    
    # Traitement de la durée
    duration = DurationSize.SMALL  # Valeur par défaut
    if 'duration' in data:
        try:
            duration = DurationSize(data['duration'])
        except ValueError:
            return jsonify({'error': 'Valeur de durée invalide (doit être S, M ou L)'}), 400
    
    # Création de l'activité avec les valeurs obligatoires
    activity_params = {
        'title': data['title'],
        'list_id': data['list_id'],
        'duration': duration
    }
    
    # Ajout des paramètres optionnels
    optional_params = ['sublist_id', 'due_date', 'start_time', 'is_template', 
                       'is_priority', 'position', 'is_active']
    
    for param in optional_params:
        if param in data:
            activity_params[param] = data[param]
    
    # Création de l'activité
    activity = Activity(**activity_params)
    
    # Sauvegarde avec validation
    try:
        activity.save()
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    return jsonify(activity.to_dict()), 201

@bp.route('/<int:id>', methods=['PUT'])
def update_activity(id):
    """Mettre à jour une activité existante."""
    activity = db.session.get(Activity, id)
    if not activity:
        return jsonify({'error': 'Activité non trouvée'}), 404
    
    data = request.get_json() or {}
    
    # Validation de la liste si changée
    if 'list_id' in data and data['list_id'] != activity.list_id:
        list_obj = db.session.get(List, data['list_id'])
        if not list_obj:
            return jsonify({'error': 'La liste spécifiée n\'existe pas'}), 404
    
    # Validation de la relation sous-liste/liste si les deux sont changés
    if 'list_id' in data and 'sublist_id' in data and data['sublist_id']:
        if not Activity.validate_sublist_belongs_to_list(data['list_id'], data['sublist_id']):
            return jsonify({'error': 'La sous-liste n\'appartient pas à la liste spécifiée'}), 400
    
    # Validation de la relation sous-liste/liste si seule la sous-liste est changée
    elif 'sublist_id' in data and data['sublist_id']:
        list_id = data.get('list_id', activity.list_id)
        if not Activity.validate_sublist_belongs_to_list(list_id, data['sublist_id']):
            return jsonify({'error': 'La sous-liste n\'appartient pas à la liste spécifiée'}), 400
    
    # Traitement de la durée si changée
    if 'duration' in data:
        try:
            data['duration'] = DurationSize(data['duration'])
        except ValueError:
            return jsonify({'error': 'Valeur de durée invalide (doit être S, M ou L)'}), 400
    
    # Mise à jour des champs
    for field in ['title', 'list_id', 'sublist_id', 'duration', 'due_date', 
                 'start_time', 'is_template', 'is_priority', 'position', 'is_active']:
        if field in data:
            setattr(activity, field, data[field])
    
    # Sauvegarde avec validation
    try:
        activity.save()
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    return jsonify(activity.to_dict()), 200

@bp.route('/<int:id>', methods=['DELETE'])
def delete_activity(id):
    """Supprimer une activité."""
    activity = db.session.get(Activity, id)
    if not activity:
        return jsonify({'error': 'Activité non trouvée'}), 404
    
    db.session.delete(activity)
    db.session.commit()
    
    return jsonify({'message': f'Activité {id} supprimée avec succès'}), 200

@bp.route('/<int:id>/complete', methods=['POST'])
def complete_activity(id):
    """Marquer une activité comme terminée."""
    activity = db.session.get(Activity, id)
    if not activity:
        return jsonify({'error': 'Activité non trouvée'}), 404
    
    activity.mark_as_completed()
    db.session.commit()
    
    return jsonify(activity.to_dict()), 200

@bp.route('/<int:id>/uncomplete', methods=['POST'])
def uncomplete_activity(id):
    """Marquer une activité comme non terminée."""
    activity = db.session.get(Activity, id)
    if not activity:
        return jsonify({'error': 'Activité non trouvée'}), 404
    
    activity.is_completed = False
    activity.completed_at = None
    db.session.commit()
    
    return jsonify(activity.to_dict()), 200

@bp.route('/<int:id>/set-current-week', methods=['POST'])
def set_current_week(id):
    """Définir l'échéance à la semaine courante."""
    activity = db.session.get(Activity, id)
    if not activity:
        return jsonify({'error': 'Activité non trouvée'}), 404
    
    activity.mark_as_current_week()
    db.session.commit()
    
    return jsonify(activity.to_dict()), 200

@bp.route('/<int:id>/set-next-week', methods=['POST'])
def set_next_week(id):
    """Définir l'échéance à la semaine prochaine."""
    activity = db.session.get(Activity, id)
    if not activity:
        return jsonify({'error': 'Activité non trouvée'}), 404
    
    activity.mark_as_next_week()
    db.session.commit()
    
    return jsonify(activity.to_dict()), 200
