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
        return render_template('pages/settings.html')
    
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
    
    @app.route('/settings', methods=['PUT', 'POST'])
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
            success, data = ctrl_list.get_list_with_sublists(activity_data.list_id)
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
