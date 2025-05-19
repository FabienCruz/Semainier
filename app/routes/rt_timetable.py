"""
app/routes/rt_timetable.py

Rôle fonctionnel: Gestion des routes pour l'emploi du temps

Description: Ce fichier contient les routes pour l'affichage et la navigation
dans l'emploi du temps journalier.

Données attendues: Application Flask
Données produites: Réponses HTTP pour la gestion de l'emploi du temps

Contraintes:
- Ne doit jamais accéder directement aux modèles
- Toute la logique métier doit être déléguée aux contrôleurs
"""

from flask import render_template, request, flash
from datetime import date

# Importation des utilitaires et contrôleurs nécessaires
from app.utils.date_utils import get_date_from_string, get_server_date_info
from app.controllers import ctrl_timetable

def register_timetable_routes(app):
    """
    Enregistre les routes pour la gestion de l'emploi du temps.
    
    Args:
        app: L'application Flask
    """
    
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
        # Récupérer la date courante dans les paramètres de requête
        current_date_str = request.args.get('current_date')
        
        # Déterminer la date cible
        if current_date_str:
            try:
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

    # TODO: Ajouter les routes pour le positionnement des activités dans l'emploi du temps,
    # la vérification des disponibilités, etc.
    