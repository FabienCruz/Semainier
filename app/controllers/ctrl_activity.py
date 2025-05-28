"""
app/controllers/ctrl_activity.py

Rôle fonctionnel: Contrôleur métier pour les activités

Description: Ce fichier contient la logique métier pour les opérations CRUD sur les activités,
sans aucune référence aux routes HTTP ou au routage. Il sert de couche intermédiaire entre
le routeur et les modèles.

Données attendues: 
- Paramètres directs ou dictionnaires de données
- Format des données défini dans le dictionnaire de données

Données produites:
- Objets métier, tuples (succès/échec, données/message) ou dictionnaires
- Aucun objet de réponse HTTP (pas de jsonify, render_template, etc.)

Contraintes:
- Les activités doivent être associées à une liste valide
- Si une sous-liste est spécifiée, elle doit appartenir à la liste parente
- Validation des durées (S/M/L) et des dates
"""

from app.models.activity import Activity, DurationSize
from app.models.list import List
from app.models.sublist import Sublist
from datetime import date, time

def get_activity(id):
    """
    Récupère une activité par son ID.
    
    Args:
        id (int): Identifiant unique de l'activité à récupérer
        
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objet Activity)
            - Si échec: (False, message d'erreur)
    """
    activity = Activity.get_by_id(id)
    if not activity:
        return False, "Activité non trouvée"
    return True, activity

def get_activities(list_id=None, sublist_id=None, is_completed=None):
    """
    Récupère les activités avec possibilité de filtrage.
    
    Args:
        list_id (int, optional): Filtre par liste parente
        sublist_id (int, optional): Filtre par sous-liste
        is_completed (bool, optional): Filtre par statut de complétion
        
    Returns:
        list: Liste des objets Activity correspondant aux critères
    """
    return Activity.get_filtered(list_id, sublist_id, is_completed)

def create_activity(data):
    """
    Crée une nouvelle activité.
    
    Args:
        data (dict): Dictionnaire contenant les données de l'activité
            - title: Titre de l'activité (requis)
            - list_id: ID de la liste parente (requis)
            - sublist_id: ID de la sous-liste (optionnel)
            - duration: Durée (S/M/L, par défaut: S)
            - due_date: Date d'échéance (optionnel)
            - start_time: Heure de début (optionnel)
            - is_priority: Priorité (optionnel)
            - position: Position (optionnel)
            - is_active: Statut d'activité (optionnel)
            
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objet Activity créé)
            - Si échec: (False, message d'erreur)
    """
    # Validation des données requises
    if 'title' not in data or 'list_id' not in data:
        return False, "Le titre et l'ID de la liste sont requis"
    
    # Vérification que la liste existe
    list_obj = List.get_by_id(data['list_id'])
    if not list_obj:
        return False, "La liste spécifiée n'existe pas"
    
    # Validation de la sous-liste si fournie
    if 'sublist_id' in data and data['sublist_id']:
        if not Activity.validate_sublist_belongs_to_list(data['list_id'], data['sublist_id']):
            return False, "La sous-liste n'appartient pas à la liste spécifiée"
    
    # Traitement de la durée
    if 'duration' in data:
        try:
            data['duration'] = DurationSize(data['duration'])
        except ValueError:
            return False, "Valeur de durée invalide (doit être S, M ou L)"
    
    # Traitement des dates vides
    if 'due_date' in data and (data['due_date'] == '' or data['due_date'] is None):
        data.pop('due_date')
        
    if 'start_time' in data and (data['start_time'] == '' or data['start_time'] is None):
        data.pop('start_time')
    
    # Création de l'activité
    activity = Activity.create(data)
    if not activity:
        return False, "Erreur lors de la création de l'activité"
    
    return True, activity

def update_activity(id, data):
    """
    Met à jour une activité existante.
    
    Args:
        id (int): Identifiant unique de l'activité à mettre à jour
        data (dict): Données à mettre à jour (identiques à create_activity)
            
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objet Activity mis à jour)
            - Si échec: (False, message d'erreur)
    """
    # Récupération de l'activité
    activity = Activity.get_by_id(id)
    if not activity:
        return False, "Activité non trouvée"
    
    # Validation de la liste si changée
    if 'list_id' in data and data['list_id'] != activity.list_id:
        list_obj = List.get_by_id(data['list_id'])
        if not list_obj:
            return False, "La liste spécifiée n'existe pas"
    
    # Validation de la relation sous-liste/liste si les deux sont changés
    if 'list_id' in data and 'sublist_id' in data and data['sublist_id']:
        if not Activity.validate_sublist_belongs_to_list(data['list_id'], data['sublist_id']):
            return False, "La sous-liste n'appartient pas à la liste spécifiée"
    
    # Validation de la relation sous-liste/liste si seule la sous-liste est changée
    elif 'sublist_id' in data and data['sublist_id']:
        list_id = data.get('list_id', activity.list_id)
        if not Activity.validate_sublist_belongs_to_list(list_id, data['sublist_id']):
            return False, "La sous-liste n'appartient pas à la liste spécifiée"
    
    # Traitement de la durée si changée
    if 'duration' in data:
        try:
            data['duration'] = DurationSize(data['duration'])
        except ValueError:
            return False, "Valeur de durée invalide (doit être S, M ou L)"
        
    # Traitement des dates vides
    if 'due_date' in data and (data['due_date'] == '' or data['due_date'] is None):
        data.pop('due_date')
        
    if 'start_time' in data and (data['start_time'] == '' or data['start_time'] is None):
        data.pop('start_time')
    
    # Mise à jour de l'activité
    updated_activity = Activity.update(id, data)
    if not updated_activity:
        return False, "Erreur lors de la mise à jour de l'activité"
    
    return True, updated_activity

def delete_activity(id):
    """
    Supprime une activité.
    
    Args:
        id (int): Identifiant unique de l'activité à supprimer
        
    Returns:
        tuple: (succès, message)
            - Si succès: (True, message de confirmation)
            - Si échec: (False, message d'erreur)
    """
    # Récupération de l'activité pour le message de confirmation
    activity = Activity.get_by_id(id)
    if not activity:
        return False, "Activité non trouvée"
    
    activity_title = activity.title
    
    # Suppression
    if not Activity.delete(id):
        return False, "Erreur lors de la suppression de l'activité"
    
    return True, f"Activité '{activity_title}' supprimée avec succès"

def update_completion(activity_id):
    """
    Met à jour l'état de complétion d'une activité (bascule entre terminé et non terminé).
    
    Args:
        activity_id (int): Identifiant unique de l'activité
        
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objet Activity mis à jour)
            - Si échec: (False, message d'erreur)
    """
    activity = Activity.get_by_id(activity_id)
    if not activity:
        return False, "Activité non trouvée"
    
    # Basculer l'état de complétion
    new_status = not activity.is_completed
    activity.set_completion(new_status)
    
    try:
        updated_activity = activity.save()
        if not updated_activity:
            return False, "Erreur lors de la mise à jour du statut de l'activité"
        return True, updated_activity
    except Exception as e:
        return False, str(e)

def set_activity_current_week(id):
    """
    Définit l'échéance d'une activité à la semaine courante.
    
    Args:
        id (int): Identifiant unique de l'activité
        
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objet Activity mis à jour)
            - Si échec: (False, message d'erreur)
    """
    activity = Activity.get_by_id(id)
    if not activity:
        return False, "Activité non trouvée"
    
    activity.set_current_week()
    
    try:
        updated_activity = activity.save()
        if not updated_activity:
            return False, "Erreur lors de la mise à jour de l'échéance de l'activité"
        return True, updated_activity
    except Exception as e:
        return False, str(e)

def set_activity_next_week(id):
    """
    Définit l'échéance d'une activité à la semaine prochaine.
    
    Args:
        id (int): Identifiant unique de l'activité
        
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objet Activity mis à jour)
            - Si échec: (False, message d'erreur)
    """
    activity = Activity.get_by_id(id)
    if not activity:
        return False, "Activité non trouvée"
    
    activity.set_next_week()
    
    try:
        updated_activity = activity.save()
        if not updated_activity:
            return False, "Erreur lors de la mise à jour de l'échéance de l'activité"
        return True, updated_activity
    except Exception as e:
        return False, str(e)

def duplicate_activity(id):
    """
    Duplique une activité existante.
    
    Args:
        id (int): Identifiant unique de l'activité à dupliquer
        
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objet Activity nouvellement créé)
            - Si échec: (False, message d'erreur)
    """
    result = Activity.create_duplicate(id)
    if not result:
        return False, "Erreur lors de la duplication de l'activité"
    
    return True, result

def set_activity_default_date(id):
    """
    Réinitialise l'échéance d'une activité à la valeur par défaut (31/12/2099).
    
    Args:
        id (int): Identifiant unique de l'activité
        
    Returns:
        tuple: (succès, données/message)
            - Si succès: (True, objet Activity mis à jour)
            - Si échec: (False, message d'erreur)
    """
    activity = Activity.get_by_id(id)
    if not activity:
        return False, "Activité non trouvée"
    
    # Réinitialiser à la date par défaut
    activity.due_date = date(2099, 12, 31)
    activity.start_time = time(23, 59)
    
    try:
        updated_activity = activity.save()
        if not updated_activity:
            return False, "Erreur lors de la réinitialisation de l'échéance de l'activité"
        return True, updated_activity
    except Exception as e:
        return False, str(e)