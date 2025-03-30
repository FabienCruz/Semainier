"""
app/controllers/list.py

Rôle fonctionnel: Contrôleur gérant les opérations CRUD sur les listes

Description: Ce fichier contient l'ensemble des routes API permettant de manipuler 
les listes du semainier (création, consultation, mise à jour, suppression).
Les listes sont les containers principaux qui peuvent contenir des sous-listes 
et des activités.

Données attendues: 
- Requêtes HTTP avec paramètres d'URL ou corps JSON
- Format des données défini dans le dictionnaire de données:
  - name: String(50), requis
  - color_code: String(7), optionnel, format HEX (#RRGGBB)

Données produites:
- Réponses JSON contenant les listes ou messages d'erreur/succès
- Codes HTTP correspondant au résultat de l'opération (200, 201, 400, 404)

Contraintes:
- Les noms de liste doivent être uniques
- La suppression d'une liste entraîne la suppression en cascade des sous-listes 
  et activités associées
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models import List
from app.utils.request_format_utils import parse_request_data

# Création du Blueprint pour les routes de liste
bp = Blueprint('list', __name__, url_prefix='/api/lists')

@bp.route('/', methods=['GET'])
def get_lists():
    """
    Récupérer toutes les listes.
    
    Cette route retourne l'ensemble des listes disponibles dans l'application,
    triées par ordre alphabétique.
    
    Retourne:
    - Liste des objets list au format JSON
    - Code 200 OK
    """
    lists = List.query.order_by(List.name).all()
    return jsonify([list_obj.to_dict() for list_obj in lists]), 200

@bp.route('/<int:id>', methods=['GET'])
def get_list(id):
    """
    Récupérer une liste par son ID.
    
    Paramètres:
    - id: Identifiant unique de la liste à récupérer
    
    Retourne:
    - Objet list au format JSON
    - Code 200 OK
    - Erreur 404 si la liste n'existe pas
    """
    list_obj = db.session.get(List, id)
    if not list_obj:
        return jsonify({'error': 'Liste non trouvée'}), 404
    return jsonify(list_obj.to_dict()), 200

@bp.route('/', methods=['POST'])
@parse_request_data
def create_list():
    """
    Créer une nouvelle liste.

    Décorateur @parse_request_data: 
    - Analyse et convertit automatiquement les données envoyées par HTMX (ou tout autre client) quel que soit le format (JSON, form-data, x-www-form-urlencoded).
    - Standardise également les types de données pour les booléens, dates et identifiants.
    
    Données JSON attendues:
    - name: Nom de la liste (requis, unique)
    - color_code: Code couleur HEX (optionnel, ex: "#3C91E6")
    
    Retourne:
    - Objet list créé au format JSON
    - Code 201 Created
    - Erreur 400 si données invalides ou nom déjà utilisé
    """
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
    
    return jsonify(list_obj.to_dict()), 201

@bp.route('/<int:id>', methods=['PUT', 'POST'])
@parse_request_data
def update_list(id):
    """
    Mettre à jour une liste existante.

    Décorateur @parse_request_data: 
    - Analyse et convertit automatiquement les données envoyées par HTMX (ou tout autre client) quel que soit le format (JSON, form-data, x-www-form-urlencoded).
    - Standardise également les types de données pour les booléens, dates et identifiants.
    
    Paramètres:
    - id: Identifiant unique de la liste à mettre à jour
    
    Données JSON attendues:
    - name: Nouveau nom de la liste (requis, unique)
    - color_code: Nouveau code couleur HEX (optionnel)
    
    Retourne:
    - Objet list mis à jour au format JSON
    - Code 200 OK
    - Erreur 404 si liste non trouvée
    - Erreur 400 si données invalides ou nom déjà utilisé
    """
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
    
    return jsonify(list_obj.to_dict()), 200

@bp.route('/<int:id>', methods=['DELETE'])
def delete_list(id):
    """
    Supprimer une liste.
    
    Cette opération supprime également toutes les sous-listes et activités
    associées à cette liste (suppression en cascade).
    
    Paramètres:
    - id: Identifiant unique de la liste à supprimer
    
    Retourne:
    - Message de confirmation au format JSON
    - Code 200 OK
    - Erreur 404 si liste non trouvée
    """
    list_obj = db.session.get(List, id)
    if not list_obj:
        return jsonify({'error': 'Liste non trouvée'}), 404
    
    # Suppression de la liste (les sous-listes et activités seront supprimées en cascade)
    db.session.delete(list_obj)
    db.session.commit()
    
    return jsonify({'message': f'Liste {id} supprimée avec succès'}), 200