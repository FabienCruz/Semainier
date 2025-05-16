"""
app/controllers/ctrl_list.py

Rôle fonctionnel: Contrôleur métier pour les listes

Description: Ce fichier contient la logique métier pour les opérations CRUD sur les listes,
sans aucune référence aux routes HTTP ou au routage. Il sert de couche intermédiaire entre
le routeur et les modèles.

Données attendues: 
- Paramètres directs ou dictionnaires de données
- Format des données défini dans le dictionnaire de données:
  - name: String(50), requis
  - color_code: String(7), optionnel, format HEX (#RRGGBB)

Données produites:
- Objets métier, tuples (succès/échec, données/message) ou dictionnaires
- Aucun objet de réponse HTTP (pas de jsonify, render_template, etc.)

Contraintes:
- Les noms de liste doivent être uniques
- La suppression d'une liste entraîne la suppression en cascade des sous-listes 
  et activités associées
"""

from app import db
from app.models.list import List
from app.models.sublist import Sublist
from app.models.activity import Activity

def get_all_lists():
    """
    Récupère toutes les listes ordonnées par nom.
    
    Returns:
        list: Liste des objets List triés par nom
    """
    return List.query.order_by(List.name).all()

def get_list(id):
    """
    Récupère une liste par son ID.
    
    Args:
        id (int): Identifiant unique de la liste à récupérer
    
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objet List)
            - Si échec: (False, message d'erreur)
    """
    list_obj = db.session.get(List, id)
    if not list_obj:
        return False, "Liste non trouvée"
    return True, list_obj

def create_list(data):
    """
    Crée une nouvelle liste.
    
    Args:
        data (dict): Dictionnaire contenant les données de la liste
            - name: Nom de la liste (requis, unique)
            - color_code: Code couleur HEX (optionnel, ex: "#3C91E6")
    
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objet List créé)
            - Si échec: (False, message d'erreur)
    """
    # Validation des données requises
    if 'name' not in data:
        return False, "Le nom de la liste est requis"
    
    # Vérification que le nom n'existe pas déjà
    if List.query.filter_by(name=data['name']).first():
        return False, "Une l[48;38;116;1520;2320tiste avec ce nom existe déjà"
    
    # Création de la liste
    list_obj = List(
        name=data['name'],
        color_code=data.get('color_code')
    )
    
    db.session.add(list_obj)
    db.session.commit()
    
    return True, list_obj

def update_list(id, data):
    """
    Met à jour une liste existante.
    
    Args:
        id (int): Identifiant unique de la liste à mettre à jour
        data (dict): Données à mettre à jour
            - name: Nouveau nom de la liste (requis, unique)
            - color_code: Nouveau code couleur HEX (optionnel)
    
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objet List mis à jour)
            - Si échec: (False, message d'erreur)
    """
    list_obj = db.session.get(List, id)
    if not list_obj:
        return False, "Liste non trouvée"
        
    # Validation des données requises
    if 'name' not in data:
        return False, "Le nom de la liste est requis"
    
    # Vérification que le nouveau nom n'existe pas déjà (sauf s'il s'agit du même)
    existing_list = List.query.filter_by(name=data['name']).first()
    if existing_list and existing_list.id != id:
        return False, "Une liste avec ce nom existe déjà"
    
    # Mise à jour des champs
    list_obj.name = data['name']
    if 'color_code' in data:
        list_obj.color_code = data['color_code']
    
    db.session.commit()
    
    return True, list_obj

def delete_list(id):
    """
    Supprime une liste et toutes les sous-listes et activités associées.
    
    Args:
        id (int): Identifiant unique de la liste à supprimer
    
    Returns:
        tuple: (succès, message)
            - Si succès: (True, message de confirmation)
            - Si échec: (False, message d'erreur)
    """
    list_obj = db.session.get(List, id)
    if not list_obj:
        return False, "Liste non trouvée"
    
    # Récupérer le nom pour le message de confirmation
    list_name = list_obj.name
    
    # Suppression de la liste (les sous-listes et activités seront supprimées en cascade)
    db.session.delete(list_obj)
    db.session.commit()
    
    return True, f"Liste '{list_name}' supprimée avec succès"

def get_list_with_content(list_id):
    """
    Récupère une liste avec ses sous-listes et activités.
    
    Args:
        id (int): Identifiant unique de la liste
    
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, dict contenant la liste, ses sous-listes et activités)
            - Si échec: (False, message d'erreur)
    """
    list_obj = db.session.get(List, list_id)
    if not list_obj:
        return False, "Liste non trouvée"
    
    # Récupérer les sous-listes et activités associées
    sublists = Sublist.get_by_list_id(list_id)
    activities = Activity.get_by_list_id(list_id)
    
    return True, {
        "list": list_obj,
        "sublists": sublists,
        "activities": activities
    }
