"""app/controllers/list.py"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import List
from app.utils.request_format_utils import parse_request_data

# Création du Blueprint pour les routes de liste
bp = Blueprint('list', __name__, url_prefix='/api/lists')

@bp.route('/', methods=['GET'])
def get_lists():
    """Récupérer toutes les listes."""
    lists = List.query.order_by(List.name).all()
    return jsonify([list_obj.to_dict() for list_obj in lists]), 200

@bp.route('/<int:id>', methods=['GET'])
def get_list(id):
    """Récupérer une liste par son ID."""
    list_obj = db.session.get(List, id)
    if not list_obj:
        return jsonify({'error': 'Liste non trouvée'}), 404
    return jsonify(list_obj.to_dict()), 200

@bp.route('/', methods=['POST'])
@parse_request_data
def create_list():
    """Créer une nouvelle liste."""
    data = request.parsed_data
    
    # Validation des données requises
    if 'name' not in data:
        return jsonify({'error': 'Le nom de la liste est requis'}), 400
    
    # Vérification que le nom n'existe pas déjà
    if List.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Une liste avec ce nom existe déjà'}), 400
    
    # Création de la liste
    list_obj = List(
        name=data['name'],
        color_code=data.get('color_code')
    )
    
    db.session.add(list_obj)
    db.session.commit()
    
    return jsonify(list_obj.to_dict()), 201  # 201 Created pour la création réussie

@bp.route('/<int:id>', methods=['PUT'])
@parse_request_data
def update_list(id):
    """Mettre à jour une liste existante."""
    list_obj = db.session.get(List, id)
    if not list_obj:
        return jsonify({'error': 'Liste non trouvée'}), 404
        
    data = request.parsed_data
    
    # Validation des données requises
    if 'name' not in data:
        return jsonify({'error': 'Le nom de la liste est requis'}), 400
    
    # Vérification que le nouveau nom n'existe pas déjà (sauf s'il s'agit du même)
    existing_list = List.query.filter_by(name=data['name']).first()
    if existing_list and existing_list.id != id:
        return jsonify({'error': 'Une liste avec ce nom existe déjà'}), 400
    
    # Mise à jour des champs
    list_obj.name = data['name']
    if 'color_code' in data:
        list_obj.color_code = data['color_code']
    
    db.session.commit()
    
    return jsonify(list_obj.to_dict()), 200  # 200 OK pour la mise à jour réussie

@bp.route('/<int:id>', methods=['DELETE'])
def delete_list(id):
    """Supprimer une liste."""
    list_obj = db.session.get(List, id)
    if not list_obj:
        return jsonify({'error': 'Liste non trouvée'}), 404
    
    # Suppression de la liste (les sous-listes et activités seront supprimées en cascade)
    db.session.delete(list_obj)
    db.session.commit()
    
    return jsonify({'message': f'Liste {id} supprimée avec succès'}), 200  # 200 OK avec message de confirmation
