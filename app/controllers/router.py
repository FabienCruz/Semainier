"""
app/controllers/router.py

Rôle fonctionnel: Routeur centralisant toutes les routes HTTP de l'application

Description: Ce fichier contient toutes les définitions de routes de l'application.
Il fait le lien entre les URLs et les contrôleurs appropriés, sans contenir de
logique métier directe.

Données attendues: Requêtes HTTP
Données produites: Réponses HTTP (HTML, JSON, redirections)

Contraintes:
- Ne doit jamais accéder directement aux modèles
- Toute la logique métier doit être déléguée aux contrôleurs
"""

from flask import render_template, redirect, url_for, request, flash, jsonify
from werkzeug.exceptions import NotFound

# Importation du décorateur qui gère les formats des données de requête
from app.utils.request_format_utils import parse_request_data

# Importation des contrôleurs
from app.controllers import ctrl_activity
from app.controllers import ctrl_list
from app.controllers import ctrl_sublist
from app.controllers import ctrl_timetable
from app.controllers import ctrl_weekly_goal
from app.controllers import ctrl_settings


def register_routes(app):
    """
    Enregistre toutes les routes de l'application sur l'objet app Flask.
    
    Args:
        app: L'application Flask
    """
    
    # =========================================================================
    # Routes principales / Tableaux de bord
    # =========================================================================
    
    @app.route('/')
    def show_dashboard():
        """Page d'accueil - Tableau de bord principal avec les 3 colonnes."""
        return render_template('pages/dashboard.html')
    @app.route('/settings')
    def show_settings():
        """Page des paramètres de l'application."""
        # Récupérer les paramètres actuels pour les afficher dans le template
        success, settings_data = ctrl_settings.get_settings()
        if not success:
            flash(settings_data, "error")
            settings_data = {}  # Utiliser un dictionnaire vide en cas d'erreur
            
        return render_template('pages/settings.html', settings=settings_data)
    # =========================================================================
    # Gestionnaires d'erreurs
    # =========================================================================
    
    @app.errorhandler(404)
    def page_not_found(e):
        """Gestion des erreurs 404."""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        """Gestion des erreurs 500."""
        return render_template('errors/500.html'), 500

    # =========================================================================
    # Routes pour les paramètres (settings)
    # =========================================================================
        
    @app.route('/settings/update', methods=['PUT', 'POST'])
    @parse_request_data
    def edit_settings():
        """
        Met à jour les paramètres de l'application.

        Cette route est appelée par HTMX lors de la soumission du formulaire de paramètres.

        Retourne:
        - Si succès: Réponse JSON avec les paramètres mis à jour
        - Si échec: Réponse JSON avec le message d'erreur
        """
        success, data = ctrl_settings.update_settings(request.parsed_data)

        if not success:
            return jsonify({"success": False, "error": data}), 400

        return jsonify({"success": True, "data": data}), 200

    # =========================================================================
    # Routes pour les suppressions
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
    # Routes pour les activités
    # =========================================================================
    
    @app.route('/modals/edit-activity/<int:activity_id>')
    def show_edit_activity(activity_id):
        """
        Affiche le formulaire d'édition d'une activité.
        
        Cette route est appelée par HTMX pour ouvrir la modale d'édition
        pré-remplie avec les données de l'activité existante.
        
        Paramètres:
        - activity_id: Identifiant unique de l'activité à modifier
        
        Retourne:
        - Rendu HTML du formulaire d'édition d'activité
        - Erreur 404 si l'activité n'existe pas
        """
        success, activity_data = ctrl_activity.get_activity(activity_id)
        if not success:
            return NotFound(activity_data)
        
        # Récupérer les listes et sous-listes pour le formulaire
        lists = ctrl_list.get_all_lists()
        
        # Si l'activité est dans une liste, récupérer ses sous-listes
        sublists = []
        if activity_data.list_id:
            success, data = ctrl_list.get_list_with_content(activity_data.list_id)
            if success:
                sublists = data["sublists"]
        
        return render_template('modals/create_edit_activity_modal.html', 
                            title="Modifier une activité",
                            activity=activity_data,
                            lists=lists,
                            sublists=sublists,
                            activity_id=activity_id)
    @app.route('/activities/<int:activity_id>/edit_completion', methods=['POST'])
    def edit_activity_completion(activity_id):
        """
        Modifie l'état de complétion d'une activité.
        
        Cette route est appelée par HTMX lorsque l'utilisateur clique sur la case à cocher.
        
        Paramètres:
        - activity_id: Identifiant unique de l'activité
        
        Retourne:
        - Rendu HTML mis à jour de la carte d'activité
        - Erreur 404 si l'activité n'existe pas
        """
        success, result = ctrl_activity.update_completion(activity_id)
        
        if not success:
            return NotFound(result)
        
        # Récupérer les informations de liste pour la couleur
        list_color = "#3C91E6"  # Couleur par défaut
        if result.list_id:
            success, list_data = ctrl_list.get_list(result.list_id)
            if success:
                list_color = list_data.color_code
        
        # Renvoyer la carte mise à jour
        return render_template('components/activity_card.html', 
                            activity=result, 
                            list_color=list_color)

    #
    # ===== Routes pour les modales d'activités ========================
    # 

    @app.route('/modals/create-activity')
    def show_new_activity():
        """
        Affiche le formulaire de création d'une activité.
        
        Cette route est appelée par HTMX pour ouvrir la modale de création.
        
        Retourne:
        - Rendu HTML du formulaire de création d'activité
        """
        lists = ctrl_list.get_all_lists()
        return render_template('modals/create_edit_activity_modal.html', 
                            title="Créer une activité",
                            lists=lists)

    @app.route('/activities', methods=['POST'])
    @parse_request_data
    def new_activity():
        """
        Crée une nouvelle activité.
        
        Cette route est appelée par HTMX lors de la soumission du formulaire de création.
        
        Retourne:
        - Si succès: Réponse JSON avec l'activité créée
        - Si échec: Réponse JSON avec le message d'erreur
        """
        success, data = ctrl_activity.create_activity(request.parsed_data)
        
        if not success:
            return jsonify({"error": data}), 400
        
        return jsonify(data.to_dict()), 201

    @app.route('/activities/<int:activity_id>', methods=['POST', 'PUT'])
    @parse_request_data
    def edit_activity(activity_id):
        """
        Met à jour une activité existante.
        
        Cette route est appelée par HTMX lors de la soumission du formulaire d'édition.
        
        Paramètres:
        - activity_id: Identifiant unique de l'activité à mettre à jour
        
        Retourne:
        - Si succès: Réponse JSON avec l'activité mise à jour
        - Si échec: Réponse JSON avec le message d'erreur
        """
        success, data = ctrl_activity.update_activity(activity_id, request.parsed_data)
        
        if not success:
            return jsonify({"error": data}), 400
        
        return jsonify(data.to_dict()), 200

    @app.route('/activities/<int:activity_id>', methods=['DELETE'])
    def erase_activity(activity_id):
        """
        Supprime une activité.
        
        Cette route est appelée par HTMX lors de la confirmation de suppression.
        
        Paramètres:
        - activity_id: Identifiant unique de l'activité à supprimer
        
        Retourne:
        - Si succès: Réponse JSON avec le message de confirmation
        - Si échec: Réponse JSON avec le message d'erreur
        """
        success, message = ctrl_activity.delete_activity(activity_id)
        
        if not success:
            return jsonify({"error": message}), 404
        
        return jsonify({"message": message}), 200

    @app.route('/activities/<int:activity_id>/default-date', methods=['POST'])
    def edit_activity_default_date(activity_id):
        """
        Réinitialise la date d'échéance d'une activité à la valeur par défaut.
        
        Cette route est appelée par HTMX lors du clic sur le bouton "Sans échéance".
        
        Paramètres:
        - activity_id: Identifiant unique de l'activité
        
        Retourne:
        - Si succès: Réponse JSON avec l'activité mise à jour
        - Si échec: Réponse JSON avec le message d'erreur
        """
        success, data = ctrl_activity.set_activity_default_date(activity_id)
        
        if not success:
            return jsonify({"error": data}), 404
        
        return jsonify(data.to_dict()), 200

    @app.route('/activities/<int:activity_id>/duplicate', methods=['POST'])
    def duplicate_activity(activity_id):
        """
        Duplique une activité existante.
        
        Cette route est appelée par HTMX lors du clic sur le bouton "Dupliquer".
        
        Paramètres:
        - activity_id: Identifiant unique de l'activité à dupliquer
        
        Retourne:
        - Si succès: Réponse JSON avec la nouvelle activité créée
        - Si échec: Réponse JSON avec le message d'erreur
        """
        success, data = ctrl_activity.duplicate_activity(activity_id)
        
        if not success:
            return jsonify({"error": data}), 404
        
        return jsonify(data.to_dict()), 201

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

    # =========================================================================
    # Routes pour les listes
    # =========================================================================
    
    @app.route('/lists')
    def show_lists():
        """
        Récupère et affiche toutes les listes avec leurs sous-listes et activités.
        
        Cette route est appelée par HTMX pour charger la colonne de gauche "Liste".
        
        Retourne:
        - Rendu HTML du composant de liste complet
        """
        lists = ctrl_list.get_all_lists()
        return render_template('components/lists.html', lists=lists)
    
    @app.route('/list/<int:list_id>')
    def show_list(list_id):
        """
        Récupère et affiche une liste spécifique avec ses sous-listes et activités.
        
        Cette route est appelée par HTMX lors du clic sur une liste ou
        après la modification/création d'une liste.
        
        Paramètres:
        - list_id: Identifiant unique de la liste à afficher
        
        Retourne:
        - Rendu HTML du contenu de la liste spécifiée
        - Erreur 404 si la liste n'existe pas
        """
        success, data = ctrl_list.get_list_with_content(list_id)
        if not success:
            return NotFound(data)
        
        return render_template(
            'components/list_content.html',
            list_item=data["list"],
            sublists=data["sublists"],
            activities=data["activities"]
        )
    
    @app.route('/modals/create-list')
    def show_new_list():
        """
        Affiche le formulaire de création de liste.
        
        Cette route est appelée par HTMX pour ouvrir la modale de création.
        
        Retourne:
        - Rendu HTML du formulaire de création de liste
        """
        return render_template('modals/create_edit_list_modal.html', 
                              title="Créer une liste")
    
    @app.route('/modals/edit-list/<int:list_id>')
    def show_edit_list(list_id):
        """
        Affiche le formulaire d'édition de liste.
        
        Cette route est appelée par HTMX pour ouvrir la modale d'édition
        pré-remplie avec les données de la liste existante.
        
        Paramètres:
        - list_id: Identifiant unique de la liste à modifier
        
        Retourne:
        - Rendu HTML du formulaire d'édition de liste
        - Erreur 404 si la liste n'existe pas
        """
        success, data = ctrl_list.get_list(list_id)
        if not success:
            return NotFound(data)
        
        return render_template('modals/create_edit_list_modal.html', 
                              title="Modifier une liste",
                              list=data,
                              list_id=list_id)
    
    @app.route('/lists', methods=['POST'])
    @parse_request_data
    def new_list():
        """
        Crée une nouvelle liste.
        
        Cette route est appelée par HTMX lors de la soumission du formulaire de création.
        
        Retourne:
        - Si succès: Réponse JSON avec la liste créée
        - Si échec: Réponse JSON avec le message d'erreur
        """
        success, data = ctrl_list.create_list(request.parsed_data)
        
        if not success:
            return jsonify({"error": data}), 400
        
        return jsonify(data.to_dict()), 201
    
    @app.route('/lists/<int:list_id>', methods=['POST', 'PUT'])
    @parse_request_data
    def edit_list(list_id):
        """
        Met à jour une liste existante.
        
        Cette route est appelée par HTMX lors de la soumission du formulaire d'édition.
        
        Paramètres:
        - list_id: Identifiant unique de la liste à mettre à jour
        
        Retourne:
        - Si succès: Réponse JSON avec la liste mise à jour
        - Si échec: Réponse JSON avec le message d'erreur
        """
        success, data = ctrl_list.update_list(list_id, request.parsed_data)
        
        if not success:
            return jsonify({"error": data}), 400
        
        return jsonify(data.to_dict()), 200
    
    @app.route('/lists/<int:list_id>', methods=['DELETE'])
    def erase_list(list_id):
        """
        Supprime une liste.
        
        Cette route est appelée par HTMX lors de la confirmation de suppression.
        
        Paramètres:
        - list_id: Identifiant unique de la liste à supprimer
        
        Retourne:
        - Si succès: Réponse JSON avec le message de confirmation
        - Si échec: Réponse JSON avec le message d'erreur
        """
        success, message = ctrl_list.delete_list(list_id)
        
        if not success:
            return jsonify({"error": message}), 404
        
        return jsonify({"message": message}), 200
    
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

    @app.route('/lists/<int:list_id>/sublists')
    def get_list_with_sublists(list_id):
        """
        Récupère une liste avec ses sous-listes.
        
        Cette route est utilisée pour obtenir les sous-listes d'une liste spécifique,
        notamment pour peupler dynamiquement les sélecteurs de sous-listes.
        
        Paramètres:
        - list_id: Identifiant unique de la liste
        
        Retourne:
        - Si succès: Réponse JSON avec la liste et ses sous-listes
        - Si échec: Réponse JSON avec le message d'erreur
        """
        success, data = ctrl_list.get_list_with_sublists(list_id)
        
        if not success:
            return jsonify({"error": data}), 404
        
        return jsonify({
            "list": data["list"].to_dict() if "list" in data else None,
            "sublists": [s.to_dict() for s in data["sublists"]] if "sublists" in data else []
        }), 200
    
    # =========================================================================
    # Routes pour les objectifs hebdomadaires
    # =========================================================================

    @app.route('/modals/weekly-goal')
    def show_weekly_goal():
        """
        Affiche la modale d'édition des objectifs de la semaine.
        
        Cette route est appelée par HTMX lorsque l'utilisateur clique sur 
        "Objectifs de la semaine" dans le menu de la colonne Objectifs.
        
        Retourne:
        - Rendu HTML du formulaire d'édition des objectifs hebdomadaires
        """
        # Récupérer les objectifs de la semaine en cours avec les infos de date
        success, data = ctrl_weekly_goal.get_weekly_goal_with_week_info()
        
        if not success:
            flash(data, "error")
            return render_template('modals/create_edit_weekly_goal_modal.html', 
                                week_display="", 
                                content="")
        
        return render_template('modals/create_edit_weekly_goal_modal.html',
                            week_display=data['week_display'],
                            content=data.get('content', ""))

    @app.route('/weekly-goals', methods=['GET'])
    def get_weekly_goal():
        """
        Récupère l'objectif textuel de la semaine en cours ou d'une semaine spécifiée.
        
        Paramètres de requête:
        - week_start: Date du lundi (format YYYY-MM-DD, optionnel)
        
        Retourne:
        - Réponse JSON avec les objectifs de la semaine et les informations de date
        """
        week_start = request.args.get('week_start')
        
        # Convertir la date si elle est fournie
        if week_start:
            try:
                from datetime import date
                week_start = date.fromisoformat(week_start)
            except ValueError:
                return jsonify({"success": False, "error": "Format de date invalide"}), 400
        
        # Récupérer les objectifs avec les infos de la semaine
        success, data = ctrl_weekly_goal.get_weekly_goal_with_week_info(week_start)
        
        if not success:
            return jsonify({"success": False, "error": data}), 400
        
        return jsonify({"success": True, "data": data}), 200

    @app.route('/weekly-goals', methods=['POST'])
    @parse_request_data
    def new_weekly_goal():
        """
        Crée ou met à jour l'objectif textuel de la semaine.
        
        Données attendues:
        - content: Contenu textuel des objectifs (max 500 caractères)
        - week_start: Date du lundi (optionnel, format YYYY-MM-DD)
        
        Retourne:
        - Réponse JSON avec les objectifs mis à jour et un message de confirmation
        """
        content = request.parsed_data.get('content', '')
        week_start = request.parsed_data.get('week_start')
        
        # Convertir la date si elle est fournie
        if week_start:
            try:
                from datetime import date
                week_start = date.fromisoformat(week_start)
            except ValueError:
                return jsonify({"success": False, "error": "Format de date invalide"}), 400
        
        # Créer ou mettre à jour les objectifs
        success, data = ctrl_weekly_goal.create_or_update_weekly_goal(content, week_start)
        
        if not success:
            return jsonify({"success": False, "error": data}), 400
        
        # Récupérer les données complètes pour la réponse
        success, full_data = ctrl_weekly_goal.get_weekly_goal_with_week_info(week_start)
        
        if not success:
            return jsonify({"success": True, "data": {"message": "Objectifs enregistrés avec succès"}}), 200
        
        return jsonify({
            "success": True, 
            "data": {
                **full_data,
                "message": "Objectifs enregistrés avec succès"
            }
        }), 200

    @app.route('/objectives')
    def show_objectives():
        """
        Affiche la colonne des objectifs de la semaine avec les activités réparties
        en sections prioritaires et standard.
        
        Cette route est appelée par HTMX pour charger la colonne "Objectifs de la semaine".
        
        Retourne:
        - Rendu HTML de la colonne des objectifs
        """
        # Récupérer les activités de la semaine
        from datetime import date
        today = date.today()
        
        # TODO: Implémenter la fonction dans ctrl_activity pour récupérer les activités de la semaine
        # Pour l'instant, utilisons des listes vides
        priority_activities = []
        standard_activities = []
        
        # Récupérer les informations de date pour l'affichage
        success, data = ctrl_weekly_goal.get_weekly_goal_with_week_info()
        server_date_info = data if success else {}
        
        return render_template('components/objectives_column.html',
                            priority_activities=priority_activities,
                            standard_activities=standard_activities,
                            server_date_info=server_date_info)
    
    # =========================================================================
    # Routes pour l'emploi du temps
    # =========================================================================

    @app.route('/timetable', defaults={'direction': None})
    @app.route('/timetable/<string:direction>')
    def show_timetable(direction):
        """
        Affiche la colonne Emploi du temps pour un jour spécifique.
        
        Cette route permet également de naviguer entre les jours de la semaine
        en utilisant les paramètres de direction ('prev' ou 'next').
        
        Paramètres:
        - direction (str, optionnel): Direction de navigation ('prev' ou 'next')
        
        Paramètres de requête:
        - current_date (str, optionnel): Date actuellement affichée au format YYYY-MM-DD
        
        Retourne:
        - Rendu HTML de la colonne emploi du temps
        """
        from datetime import date
        
        # Récupérer la date courante dans les paramètres de requête
        current_date_str = request.args.get('current_date')
        
        # Déterminer la date cible
        if current_date_str:
            try:
                from app.utils.date_utils import get_date_from_string
                current_date = get_date_from_string(current_date_str)
            except ValueError:
                current_date = date.today()
        else:
            current_date = date.today()
        
        # Si une direction est spécifiée, naviguer vers le jour précédent/suivant
        if direction:
            success, target_date = ctrl_timetable.navigate_to_day(current_date, direction)
            if not success:
                flash(target_date, "error")
                target_date = current_date
        else:
            target_date = current_date
        
        # Récupérer les données de l'emploi du temps pour la date cible
        success, timetable_data = ctrl_timetable.get_timetable_data(target_date)
        
        if not success:
            flash(timetable_data, "error")
            # Récupérer les informations de date du serveur pour affichage de secours
            from app.utils.date_utils import get_server_date_info
            server_date_info = get_server_date_info()
            return render_template('components/timetable_column.html', server_date_info=server_date_info)
        
        # Préparer les données pour le template
        return render_template(
            'components/timetable_column.html',
            current_day_info=timetable_data['day_info'],
            time_slots=timetable_data['formatted_slots'],  # Utiliser les créneaux déjà formatés
            settings=timetable_data['settings'],
            activities=timetable_data['activities']
        )
