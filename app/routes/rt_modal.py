"""
app/routes/rt_modal.py

Rôle fonctionnel: Gestion des routes pour les modales de confirmation

Description: Ce fichier contient les routes pour l'affichage des modales de 
confirmation, principalement utilisées pour les suppressions d'éléments.

Données attendues: Application Flask
Données produites: Réponses HTTP pour les modales de confirmation

Contraintes:
- Ne doit jamais accéder directement aux modèles
- Toute la logique métier doit être déléguée aux contrôleurs
"""

from flask import render_template, url_for
from werkzeug.exceptions import NotFound

# Importation des contrôleurs nécessaires
from app.controllers import ctrl_list, ctrl_sublist, ctrl_activity

def register_modal_routes(app):
    """
    Enregistre les routes pour les modales de confirmation.
    
    Args:
        app: L'application Flask
    """
    
    # =========================================================================
    # Routes pour les modales de confirmation
    # =========================================================================
    
    @app.route('/modals/confirm-delete/<string:type>/<int:id>')
    def show_erase(type, id):
        """
        Affiche la modale de confirmation de suppression pour différents types d'éléments.
        
        Cette route est appelée par HTMX lorsque l'utilisateur clique sur "Supprimer"
        pour demander confirmation avant de procéder à la suppression.
        
        Paramètres:
        - type: Type d'élément à supprimer ('list', 'sublist', 'activity')
        - id: Identifiant unique de l'élément à supprimer
        
        Retourne:
        - Rendu HTML de la modale de confirmation
        - Erreur 404 si l'élément n'existe pas
        """
        # Variables qui seront définies selon le type
        item_name = None
        delete_url = None
        
        # Traitement selon le type d'élément
        if type == 'list':
            success, list_item = ctrl_list.get_list(id)
            if not success:
                return NotFound(list_item)
            item_name = list_item.name
            delete_url = url_for('erase_list', list_id=id)
            message = f"Êtes-vous sûr de vouloir supprimer la liste '{item_name}' ? Cette action supprimera également toutes les sous-listes et activités associées."
            
        elif type == 'sublist':
            success, sublist = ctrl_sublist.get_sublist(id)
            if not success:
                return NotFound(sublist)
            item_name = sublist.name
            delete_url = url_for('erase_sublist', sublist_id=id)
            message = f"Êtes-vous sûr de vouloir supprimer la sous-liste '{item_name}' ? Cette action supprimera également toutes les activités associées."
            
        elif type == 'activity':
            success, activity = ctrl_activity.get_activity(id)
            if not success:
                return NotFound(activity)
            item_name = activity.title
            delete_url = url_for('erase_activity', activity_id=id)
            message = f"Êtes-vous sûr de vouloir supprimer l'activité '{item_name}' ?"
            
        else:
            return NotFound(f"Type d'élément '{type}' non reconnu")
        
        return render_template('modals/confirm_delete.html',
                            message=message,
                            delete_url=delete_url)

    # =========================================================================
    # Routes pour les autres modales génériques (pourraient être ajoutées à l'avenir)
    # =========================================================================
    
    # Exemple : modale d'information générique, modale d'aide, etc.
    # @app.route('/modals/info/<string:type>')
    # def show_info_modal(type):
    #     """
    #     Affiche une modale d'information pour différents types de contenu.
    #     """
    #     pass