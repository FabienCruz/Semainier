"""
app/routes/rt_main.py

Rôle fonctionnel: Gestion des routes principales et des gestionnaires d'erreurs

Description: Ce fichier contient les routes pour les pages principales (dashboard)
et les gestionnaires d'erreurs (404, 500).

Données attendues: Application Flask
Données produites: Réponses HTTP pour les pages principales

Contraintes:
- Ne doit jamais accéder directement aux modèles
- Toute la logique métier doit être déléguée aux contrôleurs
"""

from flask import render_template, flash

# Importation des contrôleurs nécessaires
from app.controllers import ctrl_settings

def register_main_routes(app):
    """
    Enregistre les routes principales de l'application.
    
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