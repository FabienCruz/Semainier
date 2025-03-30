"""
app/controllers/sublist.py

Rôle fonctionnel: Contrôleur gérant les opérations CRUD sur les sous-listes

Description: Ce fichier contient l'ensemble des routes API permettant de manipuler 
les sous-listes du semainier (création, consultation, mise à jour, suppression).
Les sous-listes sont des regroupements d'activités au sein d'une liste principale.

Données attendues: 
- Requêtes HTTP avec paramètres d'URL ou corps JSON
- Format des données défini dans le dictionnaire de données:
  - name: String(50), requis
  - list_id: Integer, requis, référence à une liste parente
  - position: Integer, optionnel, ordre d'affichage
  - is_visible: Boolean, optionnel (par défaut: True)
  - is_default: Boolean, optionnel (par défaut: False)

Données produites:
- Réponses JSON contenant les sous-listes ou messages d'erreur/succès
- Codes HTTP correspondant au résultat de l'opération (200, 201, 400, 404)

Contraintes:
- Les noms de sous-liste doivent être uniques au sein d'une même liste parente
- La suppression d'une sous-liste entraîne la suppression en cascade des activités associées
- Une sous-liste doit toujours être liée à une liste parente existante
- Une activité peut n'être attachée à aucune sous-liste. Dans ce cas, elle est rattachée à une sous-liste "par défaut" qui sera invisible.
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models import List, Sublist
from app.utils.request_format_utils import parse_request_data

# Création du Blueprint pour les routes de sous-liste
bp = Blueprint('sublist', __name__, url_prefix='/api/sublists')

@bp.route('/', methods=['GET'])
def get_sublists():
    """
    Récupérer toutes les sous-listes avec possibilité de filtrage.
    
    Paramètres d'URL acceptés:
    - list_id: Filtrer par identifiant de liste parente
    
    Retourne:
    - Liste des sous-listes au format JSON
    - Code 200 OK
    """
    list_id = request.args.get('list_id', type=int)
    
    # Filtrer par liste parent si list_id est fourni
    if list_id:
        sublists = Sublist.query.filter_by(list_id=list_id).order_by(Sublist.position).all()
    else:
        sublists = Sublist.query.order_by(Sublist.list_id, Sublist.position).all()
    
    return jsonify([sublist.to_dict() for sublist in sublists]), 200

@bp.route('/<int:id>', methods=['GET'])
def get_sublist(id):
    """
    Récupérer une sous-liste par son ID.
    
    Paramètres:
    - id: Identifiant unique de la sous-liste
    
    Retourne:
    - Sous-liste au format JSON
    - Code 200 OK
    - Erreur 404 si sous-liste non trouvée
    """
    sublist = db.session.get(Sublist, id)
    if not sublist:
        return jsonify({'error': 'Sous-liste non trouvée'}), 404
    return jsonify(sublist.to_dict()), 200

@bp.route('/', methods=['POST'])
@parse_request_data
def create_sublist():
    """
    Créer une nouvelle sous-liste.
    
    Le décorateur @parse_request_data analyse et convertit automatiquement les données
    envoyées par HTMX quel que soit le format (JSON, form-data, x-www-form-urlencoded)
    et standardise les types de données pour les booléens, dates et identifiants.
    
    Données JSON attendues:
    - name: Nom de la sous-liste (requis)
    - list_id: ID de la liste parente (requis)
    - position: Position d'affichage (optionnel, défaut: 0)
    - is_visible: Visibilité de la sous-liste (optionnel)
    - is_default: Indique si c'est la sous-liste par défaut (optionnel)
    
    Retourne:
    - Sous-liste créée au format JSON avec code 201
    - Erreur 400 si données invalides ou nom déjà utilisé
    - Erreur 404 si liste parente non trouvée
    """
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
    
    # Création de la sous-liste avec paramètres obligatoires
    sublist_params = {
        'name': data['name'],
        'list_id': data['list_id'],
        'position': data.get('position', 0)
    }
    
    # Ajout des paramètres optionnels selon le dictionnaire de données
    
    if 'is_default' in data:
        sublist_params['is_default'] = data['is_default']
    
    # Création de l'objet sous-liste
    sublist = Sublist(**sublist_params)
    
    db.session.add(sublist)
    db.session.commit()
    
    return jsonify(sublist.to_dict()), 201

@bp.route('/<int:id>', methods=['PUT', 'POST'])
@parse_request_data
def update_sublist(id):
    """
    Mettre à jour une sous-liste existante.
    
    Le décorateur @parse_request_data analyse et convertit automatiquement les données
    envoyées par HTMX quel que soit le format (JSON, form-data, x-www-form-urlencoded)
    et standardise les types de données pour les booléens, dates et identifiants.
    
    Paramètres:
    - id: Identifiant unique de la sous-liste à modifier
    
    Données JSON attendues:
    - name: Nouveau nom de la sous-liste (requis)
    - list_id: Nouvelle liste parente (optionnel)
    - position: Nouvelle position (optionnel)
    - is_visible: Nouvel état de visibilité (optionnel)
    
    Retourne:
    - Sous-liste mise à jour au format JSON
    - Code 200 OK
    - Erreur 404 si sous-liste ou liste parente non trouvée
    - Erreur 400 si données invalides ou nom déjà utilisé
    """
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
    
    # Mise à jour des champs optionnels
    if 'list_id' in data:
        sublist.list_id = data['list_id']
    
    if 'position' in data:
        sublist.position = data['position']
    
    if 'is_visible' in data:
        sublist.is_visible = data['is_visible']
    
    db.session.commit()
    
    return jsonify(sublist.to_dict()), 200

@bp.route('/<int:id>', methods=['DELETE'])
def delete_sublist(id):
    """
    Supprimer une sous-liste.
    
    Cette opération supprime également toutes les activités associées
    à cette sous-liste (suppression en cascade).
    
    Paramètres:
    - id: Identifiant unique de la sous-liste à supprimer
    
    Retourne:
    - Message de confirmation au format JSON
    - Code 200 OK
    - Erreur 404 si sous-liste non trouvée
    """
    sublist = db.session.get(Sublist, id)
    if not sublist:
        return jsonify({'error': 'Sous-liste non trouvée'}), 404
    
    # Suppression de la sous-liste (les activités seront supprimées en cascade)
    db.session.delete(sublist)
    db.session.commit()
    
    return jsonify({'message': f'Sous-liste {id} supprimée avec succès'}), 200