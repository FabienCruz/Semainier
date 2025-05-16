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

# Importation des contrôleurs
from app.controllers import ctrl_list

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
    def dashboard():
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
    def new_list():
        """
        Affiche le formulaire de création de liste.
        
        Cette route est appelée par HTMX pour ouvrir la modale de création.
        
        Retourne:
        - Rendu HTML du formulaire de création de liste
        """
        return render_template('modals/create_edit_list_modal.html', 
                              title="Créer une liste")
    
    @app.route('/modals/edit-list/<int:list_id>')
    def edit_list(list_id):
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
    def create_list():
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
    def update_list(list_id):
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
    def delete_list(list_id):
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
