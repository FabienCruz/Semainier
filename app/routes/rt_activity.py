"""
app/routes/rt_activity.py

Rôle fonctionnel: Gestion des routes pour les activités

Description: Ce fichier contient les routes pour l'affichage, la création, 
la modification, la suppression et les opérations spéciales sur les activités.

Données attendues: Application Flask
Données produites: Réponses HTTP pour la gestion des activités

Contraintes:
- Ne doit jamais accéder directement aux modèles
- Toute la logique métier doit être déléguée aux contrôleurs
"""

from flask import render_template, request, jsonify
from werkzeug.exceptions import NotFound

# Importation du décorateur qui gère les formats des données de requête
from app.utils.request_format_utils import parse_request_data

# Importation des contrôleurs nécessaires
from app.controllers import ctrl_activity, ctrl_list

def register_activity_routes(app):
    """
    Enregistre les routes pour la gestion des activités.
    
    Args:
        app: L'application Flask
    """
    
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