"""
app/controllers/ctrl_sublist.py

Rôle fonctionnel: Contrôleur métier pour les sous-listes

Description: Ce fichier contient la logique métier pour les opérations CRUD sur les sous-listes,
sans aucune référence aux routes HTTP ou au routage. Il sert de couche intermédiaire entre
le routeur et les modèles.

Données attendues: 
- Paramètres directs ou dictionnaires de données
- Format des données défini dans le dictionnaire de données:
  - name: String(50), requis
  - list_id: Integer, requis
  - position: Integer, optionnel
  - is_visible: Boolean, optionnel, par défaut True
  - is_default: Boolean, optionnel, par défaut False

Données produites:
- Objets métier, tuples (succès/échec, données/message) ou dictionnaires
- Aucun objet de réponse HTTP (pas de jsonify, render_template, etc.)

Contraintes:
- Les noms de sous-liste doivent être uniques au sein d'une même liste parente
- La suppression d'une sous-liste entraîne la suppression en cascade des activités associées
- Une sous-liste doit toujours être liée à une liste parente existante
"""

from app.models.sublist import Sublist
from app.models.list import List

def get_sublist(id):
    """
    Récupère une sous-liste par son ID.
    
    Args:
        id (int): Identifiant unique de la sous-liste à récupérer
        
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objet Sublist)
            - Si échec: (False, message d'erreur)
    """
    sublist = Sublist.get_by_id(id)
    if not sublist:
        return False, "Sous-liste non trouvée"
    return True, sublist

def get_sublists_for_list(list_id):
    """
    Récupère toutes les sous-listes d'une liste spécifique.
    
    Args:
        list_id (int): Identifiant de la liste parente
        
    Returns:
        list: Liste des sous-listes associées à la liste parente,
             ou liste vide si list_id est None ou invalide
    """
    if not list_id:
        return []
    
    return Sublist.get_by_list_id(list_id)

def create_sublist(data):
    """
    Crée une nouvelle sous-liste.
    
    Args:
        data (dict): Dictionnaire contenant les données de la sous-liste
            - name: Nom de la sous-liste (requis)
            - list_id: ID de la liste parente (requis)
            - position: Position d'affichage (optionnel, défaut: 0)
            - is_visible: Visibilité de la sous-liste (optionnel)
            - is_default: Indique si c'est la sous-liste par défaut (optionnel)
            
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objet Sublist créé)
            - Si échec: (False, message d'erreur)
    """
    # Validation des données requises
    if 'name' not in data or 'list_id' not in data:
        return False, "Le nom et l'ID de la liste parente sont requis"
    
    # Vérification que la liste parente existe
    list_obj = List.get_by_id(data['list_id'])
    if not list_obj:
        return False, "La liste parente spécifiée n'existe pas"
    
    # Vérification que le nom n'existe pas déjà dans la même liste parente
    if Sublist.exists_with_name_in_list(data['name'], data['list_id']):
        return False, "Une sous-liste avec ce nom existe déjà dans cette liste"
    
    # Création de la sous-liste
    sublist = Sublist.create(
        name=data['name'],
        list_id=data['list_id'],
        position=data.get('position', 0),
        is_default=data.get('is_default', False)
    )
    
    if not sublist:
        return False, "Erreur lors de la création de la sous-liste"
    
    return True, sublist

def update_sublist(id, data):
    """
    Met à jour une sous-liste existante.
    
    Args:
        id (int): Identifiant unique de la sous-liste à mettre à jour
        data (dict): Données à mettre à jour
            - name: Nouveau nom de la sous-liste (requis)
            - list_id: Nouvelle liste parente (optionnel)
            - position: Nouvelle position (optionnel)
            - is_visible: Nouvel état de visibilité (optionnel)
            
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objet Sublist mis à jour)
            - Si échec: (False, message d'erreur)
    """
    # Récupération de la sous-liste existante
    sublist = Sublist.get_by_id(id)
    if not sublist:
        return False, "Sous-liste non trouvée"
        
    # Validation des données requises
    if 'name' not in data:
        return False, "Le nom de la sous-liste est requis"
    
    # Si changement de liste parente, vérifier qu'elle existe
    if 'list_id' in data and data['list_id'] != sublist.list_id:
        list_obj = List.get_by_id(data['list_id'])
        if not list_obj:
            return False, "La liste parente spécifiée n'existe pas"
    
    # Vérification d'unicité du nom dans la même liste
    list_id = data.get('list_id', sublist.list_id)
    if Sublist.exists_with_name_in_list(data['name'], list_id, exclude_id=id):
        return False, "Une sous-liste avec ce nom existe déjà dans cette liste"
    
    # Préparation des données à mettre à jour
    update_data = {
        'name': data['name']
    }
    
    # Ajout des champs optionnels s'ils sont présents
    if 'list_id' in data:
        update_data['list_id'] = data['list_id']
    
    if 'position' in data:
        update_data['position'] = data['position']
    
    if 'is_visible' in data:
        update_data['is_visible'] = data['is_visible']
    
    # Mise à jour de la sous-liste
    updated_sublist = Sublist.update(id, update_data)
    if not updated_sublist:
        return False, "Erreur lors de la mise à jour de la sous-liste"
    
    return True, updated_sublist

def delete_sublist(id):
    """
    Supprime une sous-liste et toutes les activités associées.
    
    Args:
        id (int): Identifiant unique de la sous-liste à supprimer
        
    Returns:
        tuple: (succès, message)
            - Si succès: (True, message de confirmation)
            - Si échec: (False, message d'erreur)
    """
    # Récupération de la sous-liste
    sublist = Sublist.get_by_id(id)
    if not sublist:
        return False, "Sous-liste non trouvée"
    
    # Récupérer le nom pour le message de confirmation
    sublist_name = sublist.name
    
    # Suppression de la sous-liste
    if not Sublist.delete(id):
        return False, "Erreur lors de la suppression de la sous-liste"
    
    return True, f"Sous-liste '{sublist_name}' supprimée avec succès"