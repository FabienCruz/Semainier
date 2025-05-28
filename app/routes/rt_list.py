"""
app/routes/rt_list.py

Rôle fonctionnel: Gestion des routes pour les listes

Description: Ce fichier contient les routes pour l'affichage, la création, 
la modification et la suppression des listes.

Données attendues: Application Flask
Données produites: Réponses HTTP pour la gestion des listes

Contraintes:
- Ne doit jamais accéder directement aux modèles
- Toute la logique métier doit être déléguée aux contrôleurs
"""

from flask import render_template, request, jsonify, url_for
from werkzeug.exceptions import NotFound

# Importation du décorateur qui gère les formats des données de requête
from app.utils.request_format_utils import parse_request_data

# Importation des contrôleurs nécessaires
from app.controllers import ctrl_list

def register_list_routes(app):
    """
    Enregistre les routes pour la gestion des listes.
    
    Args:
        app: L'application Flask
    """
    
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
    