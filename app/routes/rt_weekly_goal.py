"""
app/routes/rt_weekly_goal.py

Rôle fonctionnel: Gestion des routes pour les objectifs hebdomadaires

Description: Ce fichier contient les routes pour l'affichage, la création et 
la modification des objectifs textuels de la semaine, ainsi que la colonne 'Objectifs'.

Données attendues: Application Flask
Données produites: Réponses HTTP pour la gestion des objectifs hebdomadaires

Contraintes:
- Ne doit jamais accéder directement aux modèles
- Toute la logique métier doit être déléguée aux contrôleurs
"""

from flask import render_template, request, jsonify, flash
from datetime import date

# Importation du décorateur qui gère les formats des données de requête
from app.utils.request_format_utils import parse_request_data

# Importation des contrôleurs nécessaires
from app.controllers import ctrl_weekly_goal

def register_weekly_goal_routes(app):
    """
    Enregistre les routes pour la gestion des objectifs hebdomadaires.
    
    Args:
        app: L'application Flask
    """
    
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