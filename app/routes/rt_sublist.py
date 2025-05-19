"""
app/routes/rt_sublist.py

Rôle fonctionnel: Gestion des routes pour les sous-listes

Description: Ce fichier contient les routes pour l'affichage, la création, 
la modification et la suppression des sous-listes.

Données attendues: Application Flask
Données produites: Réponses HTTP pour la gestion des sous-listes

Contraintes:
- Ne doit jamais accéder directement aux modèles
- Toute la logique métier doit être déléguée aux contrôleurs
"""

from flask import render_template, request, jsonify
from werkzeug.exceptions import NotFound

# Importation du décorateur qui gère les formats des données de requête
from app.utils.request_format_utils import parse_request_data

# Importation des contrôleurs nécessaires
from app.controllers import ctrl_list, ctrl_sublist

def register_sublist_routes(app):
    """
    Enregistre les routes pour la gestion des sous-listes.
    
    Args:
        app: L'application Flask
    """
    
    # =========================================================================
    # Routes pour les sous-listes
    # =========================================================================
    
    @app.route('/modals/create-sublist')
    def show_new_sublist():
        """
        Affiche le formulaire de création d'une sous-liste.
        
        Cette route est appelée par HTMX pour ouvrir la modale de création.
        
        Paramètres de requête:
        - list_id: Identifiant de la liste parente (optionnel)
        
        Retourne:
        - Rendu HTML du formulaire de création de sous-liste
        """
        # Récupérer l'ID de liste si fourni
        list_id = request.args.get('list_id', type=int)
        
        # Récupérer toutes les listes pour le sélecteur
        lists = ctrl_list.get_all_lists()
        
        # Récupérer la liste sélectionnée si une liste_id est fournie
        selected_list = None
        if list_id:
            success, data = ctrl_list.get_list(list_id)
            if success:
                selected_list = data
        
        return render_template('modals/create_edit_sublist_modal.html',
                            title="Créer une sous-liste",
                            lists=lists,
                            selected_list=selected_list,
                            selected_list_id=list_id)

    @app.route('/modals/edit-sublist/<int:sublist_id>')
    def show_edit_sublist(sublist_id):
        """
        Affiche le formulaire d'édition d'une sous-liste.
        
        Cette route est appelée par HTMX pour ouvrir la modale d'édition
        pré-remplie avec les données de la sous-liste existante.
        
        Paramètres:
        - sublist_id: Identifiant unique de la sous-liste à modifier
        
        Retourne:
        - Rendu HTML du formulaire d'édition de sous-liste
        - Erreur 404 si la sous-liste n'existe pas
        """
        # Récupérer la sous-liste
        success, sublist = ctrl_sublist.get_sublist(sublist_id)
        if not success:
            return NotFound(sublist)
        
        # Récupérer toutes les listes pour le sélecteur
        lists = ctrl_list.get_all_lists()
        
        return render_template('modals/create_edit_sublist_modal.html',
                            title="Modifier une sous-liste",
                            sublist=sublist,
                            lists=lists,
                            selected_list_id=sublist.list_id,
                            sublist_id=sublist_id)

    @app.route('/sublists', methods=['POST'])
    @parse_request_data
    def new_sublist():
        """
        Crée une nouvelle sous-liste.
        
        Cette route est appelée par HTMX lors de la soumission du formulaire de création.
        
        Retourne:
        - Si succès: Réponse JSON avec la sous-liste créée
        - Si échec: Réponse JSON avec le message d'erreur
        """
        success, data = ctrl_sublist.create_sublist(request.parsed_data)
        
        if not success:
            return jsonify({"error": data}), 400
        
        # Déclencher le rafraîchissement de la liste parente
        list_id = request.parsed_data.get('list_id')
        
        response = jsonify(data.to_dict())
        response.headers['HX-Trigger'] = f'listContentRefresh-{list_id}, listRefresh'
        
        return response, 201

    @app.route('/sublists/<int:sublist_id>', methods=['POST', 'PUT'])
    @parse_request_data
    def edit_sublist(sublist_id):
        """
        Met à jour une sous-liste existante.
        
        Cette route est appelée par HTMX lors de la soumission du formulaire d'édition.
        
        Paramètres:
        - sublist_id: Identifiant unique de la sous-liste à mettre à jour
        
        Retourne:
        - Si succès: Réponse JSON avec la sous-liste mise à jour
        - Si échec: Réponse JSON avec le message d'erreur
        """
        success, data = ctrl_sublist.update_sublist(sublist_id, request.parsed_data)
        
        if not success:
            return jsonify({"error": data}), 400
        
        # Déclencher le rafraîchissement de la liste parente
        list_id = request.parsed_data.get('list_id')
        if not list_id and hasattr(data, 'list_id'):
            list_id = data.list_id
        
        response = jsonify(data.to_dict())
        
        if list_id:
            response.headers['HX-Trigger'] = f'listContentRefresh-{list_id}, listRefresh'
        else:
            response.headers['HX-Trigger'] = 'listRefresh'
        
        return response, 200

    @app.route('/sublists/<int:sublist_id>', methods=['DELETE'])
    def erase_sublist(sublist_id):
        """
        Supprime une sous-liste.
        
        Cette route est appelée par HTMX lors de la confirmation de suppression.
        
        Paramètres:
        - sublist_id: Identifiant unique de la sous-liste à supprimer
        
        Retourne:
        - Si succès: Réponse JSON avec le message de confirmation
        - Si échec: Réponse JSON avec le message d'erreur
        """
        # Récupérer d'abord l'ID de la liste parente pour le rafraîchissement
        success, sublist = ctrl_sublist.get_sublist(sublist_id)
        list_id = sublist.list_id if success else None
        
        # Supprimer la sous-liste
        success, message = ctrl_sublist.delete_sublist(sublist_id)
        
        if not success:
            return jsonify({"error": message}), 404
        
        # Préparer la réponse
        response = jsonify({"message": message})
        
        # Ajouter le déclencheur pour rafraîchir la liste parente
        if list_id:
            response.headers['HX-Trigger'] = f'listContentRefresh-{list_id}, listRefresh'
        else:
            response.headers['HX-Trigger'] = 'listRefresh'
        
        return response, 200

    @app.route('/sublists-for-list')
    def show_sublists_for_list():
        """
        Récupère les sous-listes pour une liste spécifique.
        
        Cette route est appelée par HTMX lors du changement de liste dans le formulaire.
        
        Paramètres de requête:
        - list_id: Identifiant unique de la liste sélectionnée
        
        Retourne:
        - Rendu HTML des options du select pour les sous-listes
        """
        list_id = request.args.get('list_id', type=int)
        sublists = []
        
        if list_id:
            success, data = ctrl_list.get_list_with_sublists(list_id)
            if success:
                sublists = data["sublists"]
        
        return render_template('components/sublist_options.html', sublists=sublists)