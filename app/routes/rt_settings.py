"""
app/routes/rt_settings.py

Rôle fonctionnel: Gestion des routes pour les paramètres de l'application

Description: Ce fichier contient les routes pour afficher et modifier les paramètres
de l'application (unités de temps, horaires, etc.).

Données attendues: Application Flask
Données produites: Réponses HTTP pour la gestion des paramètres

Contraintes:
- Ne doit jamais accéder directement aux modèles
- Toute la logique métier doit être déléguée aux contrôleurs
"""

from flask import request, jsonify

# Importation du décorateur qui gère les formats des données de requête
from app.utils.request_format_utils import parse_request_data

# Importation des contrôleurs nécessaires
from app.controllers import ctrl_settings

def register_settings_routes(app):
    """
    Enregistre les routes pour la gestion des paramètres.
    
    Args:
        app: L'application Flask
    """
    
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