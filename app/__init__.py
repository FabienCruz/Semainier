"""
File: app/__init__.py
Role: Point d'entrée de l'application Flask
Description: Configure l'application Flask, initialise la base de données et enregistre les routes centralisées
Input data: N/A
Output data: Instance d'application Flask configurée
Business constraints:
- Utilise SQLite comme base de données stockée dans le dossier instance
- Initialise SQLAlchemy et Flask-Migrate pour la gestion de la base de données
- Importe tous les modèles pour que Flask-Migrate puisse détecter les changements
- Utilise un routeur central 
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Initialisation de la base de données
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    # Création de l'instance Flask
    app = Flask(__name__, instance_relative_config=True)
    
    # Assurer que le dossier d'instance existe
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{os.path.join(app.instance_path, "semainier.sqlite")}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    
    # Initialisation des extensions avec l'application
    db.init_app(app)
    migrate.init_app(app, db)

    # Import des modèles pour que Flask-Migrate les détecte
    from app.models import List, Sublist, Activity, Settings, WeeklyGoal
    
    # Enregistrement des routes centralisées via le routeur
    from app.controllers.router import register_routes
    register_routes(app)
    """
    # Enregistrement des filtres personnalisés
    from app.utils.date_utils import format_time
    
    @app.template_filter('format_time')
    def format_time_filter(time_str):
        return format_time(time_str)
    """

    # Initialisation des paramètres par défaut au démarrage de l'application
    with app.app_context():
        # Vérifier si des paramètres existent déjà
        settings = db.session.query(Settings).first()
        if not settings:
            # Créer des paramètres par défaut
            settings = Settings(
                time_unit_minutes=30,
                day_start_time="09:00",
                time_units_per_day=20,
                wip_limit=100
            )
            db.session.add(settings)
            db.session.commit()
            app.logger.info("Paramètres par défaut créés avec succès")

    @app.context_processor
    def inject_date_info():
        """
        Injecte les informations de date dans tous les templates
        """
        from app.utils.date_utils import get_server_date_info
        
        return {
            'server_date_info': get_server_date_info()
        }
    
    return app
