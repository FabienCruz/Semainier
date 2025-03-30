"""
app/controllers/activity.py

Rôle fonctionnel: Contrôleur gérant les opérations CRUD sur les activités et leurs états

Description: Ce fichier contient l'ensemble des routes API permettant de manipuler 
les activités du semainier (création, consultation, mise à jour, suppression) ainsi
que les transitions d'état spécifiques (complétion, planification hebdomadaire).

Données attendues: 
- Requêtes HTTP avec paramètres d'URL ou corps JSON
- Formats des données définis dans le dictionnaire de données

Données produites:
- Réponses JSON contenant les activités ou messages d'erreur/succès
- Codes HTTP correspondant au résultat de l'opération (200, 201, 400, 404)

Contraintes:
- Validation des relations entre listes et sous-listes
- Gestion des transitions d'état (terminé, non-terminé)
- Planification temporelle (semaine courante, semaine prochaine)
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models import List, Activity
from app.models.activity import DurationSize
from app.utils.request_format_utils import parse_request_data

# Création du Blueprint pour les routes d'activité
bp = Blueprint('activity', __name__, url_prefix='/api/activities')

@bp.route('/', methods=['GET'])
def get_activities():
    """
    Récupérer les activités avec possibilité de filtrage.
    
    Paramètres d'URL acceptés:
    - list_id: Filtrer par identifiant de liste
    - sublist_id: Filtrer par identifiant de sous-liste
    - is_completed: Filtrer par état de complétion (0/1)
    
    Retourne:
    - Liste des activités au format JSON
    """
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
    """
    Récupérer une activité spécifique par son ID.
    
    Paramètres:
    - id: Identifiant unique de l'activité
    
    Retourne:
    - Activité au format JSON ou erreur 404 si non trouvée
    """
    activity = db.session.get(Activity, id)
    if not activity:
        return jsonify({'error': 'Activité non trouvée'}), 404
    return jsonify(activity.to_dict()), 200

@bp.route('/', methods=['POST'])
@parse_request_data
def create_activity():
    """
    Créer une nouvelle activité.
    
    Décorateur @parse_request_data: 
    - Analyse et convertit automatiquement les données envoyées par HTMX (ou tout autre client) quel que soit le format (JSON, form-data, x-www-form-urlencoded).
    - Standardise également les types de données pour les booléens, dates et identifiants.

    Données JSON attendues:
    - title: Titre de l'activité (requis)
    - list_id: ID de la liste parente (requis)
    - sublist_id: ID de la sous-liste (optionnel)
    - duration: Durée (S/M/L, par défaut: S)
    - due_date: Date d'échéance (optionnel, format YYYY-MM-DD)
    - start_time: Heure de début (optionnel, format HH:MM)
    - is_template: Indique si l'activité est un modèle (optionnel)
    - is_priority: Indique si l'activité est prioritaire (optionnel)
    - position: Position dans l'ordre d'affichage (optionnel)
    - is_active: Statut d'activité (optionnel)
    
    Retourne:
    - Activité créée au format JSON avec code 201
    - Erreur 400 si données invalides
    - Erreur 404 si liste parente non trouvée
    """
    data = request.parsed_data
    
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
    # Correction: is_template → is_model pour respecter la convention
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

@bp.route('/<int:id>', methods=['PUT', 'POST'])
@parse_request_data
def update_activity(id):
    """
    Mettre à jour une activité existante.
    
    Paramètres:
    - id: Identifiant unique de l'activité à mettre à jour

    Décorateur @parse_request_data: 
    - Analyse et convertit automatiquement les données envoyées par HTMX (ou tout autre client) quel que soit le format (JSON, form-data, x-www-form-urlencoded).
    - Standardise également les types de données pour les booléens, dates et identifiants.

    Données JSON attendues:
    - Identiques à la création, tous les champs sont optionnels
    
    Retourne:
    - Activité mise à jour au format JSON
    - Erreur 404 si activité non trouvée
    - Erreur 400 si données invalides
    """
    activity = db.session.get(Activity, id)
    if not activity:
        return jsonify({'error': 'Activité non trouvée'}), 404
    
    data = request.parsed_data
    
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
    # Correction: is_template → is_model pour respecter la convention
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
    """
    Supprimer une activité.
    
    Paramètres:
    - id: Identifiant unique de l'activité à supprimer
    
    Retourne:
    - Message de confirmation avec code 200
    - Erreur 404 si activité non trouvée
    """
    activity = db.session.get(Activity, id)
    if not activity:
        return jsonify({'error': 'Activité non trouvée'}), 404
    
    db.session.delete(activity)
    db.session.commit()
    
    return jsonify({'message': f'Activité {id} supprimée avec succès'}), 200

@bp.route('/<int:id>/complete', methods=['POST'])
def complete_activity(id):
    """
    Marquer une activité comme terminée.
    
    Paramètres:
    - id: Identifiant unique de l'activité
    
    Retourne:
    - Activité mise à jour au format JSON
    - Erreur 404 si activité non trouvée
    """
    activity = db.session.get(Activity, id)
    if not activity:
        return jsonify({'error': 'Activité non trouvée'}), 404
    
    activity.mark_as_completed()
    db.session.commit()
    
    return jsonify(activity.to_dict()), 200

@bp.route('/<int:id>/uncomplete', methods=['POST'])
def uncomplete_activity(id):
    """
    Marquer une activité comme non terminée.
    
    Paramètres:
    - id: Identifiant unique de l'activité
    
    Retourne:
    - Activité mise à jour au format JSON
    - Erreur 404 si activité non trouvée
    """
    activity = db.session.get(Activity, id)
    if not activity:
        return jsonify({'error': 'Activité non trouvée'}), 404
    
    activity.is_completed = False
    activity.completed_at = None
    db.session.commit()
    
    return jsonify(activity.to_dict()), 200

@bp.route('/<int:id>/set-current-week', methods=['POST'])
def set_current_week(id):
    """
    Définir l'échéance à la semaine courante.
    
    Cette fonction met à jour la date d'échéance de l'activité pour qu'elle
    corresponde au dimanche de la semaine en cours (23h59).
    
    Paramètres:
    - id: Identifiant unique de l'activité
    
    Retourne:
    - Activité mise à jour au format JSON
    - Erreur 404 si activité non trouvée
    """
    activity = db.session.get(Activity, id)
    if not activity:
        return jsonify({'error': 'Activité non trouvée'}), 404
    
    activity.mark_as_current_week()
    db.session.commit()
    
    return jsonify(activity.to_dict()), 200

@bp.route('/<int:id>/set-next-week', methods=['POST'])
def set_next_week(id):
    """
    Définir l'échéance à la semaine prochaine.
    
    Cette fonction met à jour la date d'échéance de l'activité pour qu'elle
    corresponde au dimanche de la semaine suivante (23h59).
    
    Paramètres:
    - id: Identifiant unique de l'activité
    
    Retourne:
    - Activité mise à jour au format JSON
    - Erreur 404 si activité non trouvée
    """
    activity = db.session.get(Activity, id)
    if not activity:
        return jsonify({'error': 'Activité non trouvée'}), 404
    
    activity.mark_as_next_week()
    db.session.commit()
    
    return jsonify(activity.to_dict()), 200