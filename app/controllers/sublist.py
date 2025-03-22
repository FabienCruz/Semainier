from flask import Blueprint, request, jsonify
from app import db
from app.models import List, Sublist
from app.utils.request_format_utils import parse_request_data

# Création du Blueprint pour les routes de sous-liste
bp = Blueprint('sublist', __name__, url_prefix='/api/sublists')

@bp.route('/', methods=['GET'])
def get_sublists():
    """Récupérer toutes les sous-listes."""
    list_id = request.args.get('list_id', type=int)
    
    # Filtrer par liste parent si list_id est fourni
    if list_id:
        sublists = Sublist.query.filter_by(list_id=list_id).order_by(Sublist.position).all()
    else:
        sublists = Sublist.query.order_by(Sublist.list_id, Sublist.position).all()
    
    return jsonify([sublist.to_dict() for sublist in sublists]), 200

@bp.route('/<int:id>', methods=['GET'])
def get_sublist(id):
    """Récupérer une sous-liste par son ID."""
    sublist = db.session.get(Sublist, id)
    if not sublist:
        return jsonify({'error': 'Sous-liste non trouvée'}), 404
    return jsonify(sublist.to_dict()), 200

@bp.route('/', methods=['POST'])
@parse_request_data
def create_sublist():
    """Créer une nouvelle sous-liste."""
    data = request.parsed_data
    
    # Validation des données requises
    if 'name' not in data or 'list_id' not in data:
        return jsonify({'error': 'Le nom et l\'ID de la liste parente sont requis'}), 400
    
    # Vérification que la liste parente existe
    list_obj = db.session.get(List, data['list_id'])
    if not list_obj:
        return jsonify({'error': 'La liste parente spécifiée n\'existe pas'}), 404
    
    # Vérification que le nom n'existe pas déjà dans la même liste parente
    if Sublist.query.filter_by(name=data['name'], list_id=data['list_id']).first():
        return jsonify({'error': 'Une sous-liste avec ce nom existe déjà dans cette liste'}), 400
    
    # Création de la sous-liste
    position = data.get('position', 0)
    sublist = Sublist(
        name=data['name'],
        list_id=data['list_id'],
        position=position
    )
    
    db.session.add(sublist)
    db.session.commit()
    
    return jsonify(sublist.to_dict()), 201

@bp.route('/<int:id>', methods=['PUT', 'POST'])
@parse_request_data
def update_sublist(id):
    """Mettre à jour une sous-liste existante."""
    sublist = db.session.get(Sublist, id)
    if not sublist:
        return jsonify({'error': 'Sous-liste non trouvée'}), 404
        
    data = request.parsed_data
    
    # Validation des données requises
    if 'name' not in data:
        return jsonify({'error': 'Le nom de la sous-liste est requis'}), 400
    
    # Si changement de liste parente, vérifier qu'elle existe
    if 'list_id' in data and data['list_id'] != sublist.list_id:
        list_obj = db.session.get(List, data['list_id'])
        if not list_obj:
            return jsonify({'error': 'La liste parente spécifiée n\'existe pas'}), 404
    
    # Vérification d'unicité du nom dans la même liste
    list_id = data.get('list_id', sublist.list_id)
    existing = Sublist.query.filter_by(name=data['name'], list_id=list_id).first()
    if existing and existing.id != id:
        return jsonify({'error': 'Une sous-liste avec ce nom existe déjà dans cette liste'}), 400
    
    # Mise à jour des champs
    sublist.name = data['name']
    if 'list_id' in data:
        sublist.list_id = data['list_id']
    if 'position' in data:
        sublist.position = data['position']
    
    db.session.commit()
    
    return jsonify(sublist.to_dict()), 200

@bp.route('/<int:id>', methods=['DELETE'])
def delete_sublist(id):
    """Supprimer une sous-liste."""
    sublist = db.session.get(Sublist, id)
    if not sublist:
        return jsonify({'error': 'Sous-liste non trouvée'}), 404
    
    # Suppression de la sous-liste
    db.session.delete(sublist)
    db.session.commit()
    
    return jsonify({'message': f'Sous-liste {id} supprimée avec succès'}), 200