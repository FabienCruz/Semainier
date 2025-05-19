"""
app/routes/__init__.py

Rôle fonctionnel: Point d'entrée pour l'enregistrement de toutes les routes de l'application

Description: Ce fichier centralise l'importation et l'enregistrement de toutes les routes
modulaires de l'application auprès de l'instance Flask.

Données attendues: Application Flask
Données produites: Routes enregistrées sur l'application
"""

def register_routes(app):
    """
    Enregistre toutes les routes de l'application sur l'objet app Flask.
    
    Args:
        app: L'application Flask
    """
    # Importer ici pour éviter les imports circulaires
    from app.routes.rt_main import register_main_routes
    from app.routes.rt_list import register_list_routes
    from app.routes.rt_sublist import register_sublist_routes 
    from app.routes.rt_activity import register_activity_routes
    from app.routes.rt_settings import register_settings_routes
    from app.routes.rt_timetable import register_timetable_routes
    from app.routes.rt_weekly_goal import register_weekly_goal_routes
    from app.routes.rt_modal import register_modal_routes
    
    # Enregistrer les routes par catégorie
    register_main_routes(app)
    register_list_routes(app)
    register_sublist_routes(app)
    register_activity_routes(app)
    register_settings_routes(app)
    register_timetable_routes(app)
    register_weekly_goal_routes(app)
    register_modal_routes(app)