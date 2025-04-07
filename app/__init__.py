"""
File: app/__init__.py
Role: Point d'entrée de l'application Flask
Description: Configure l'application Flask, initialise la base de données et enregistre les blueprints
Input data: N/A
Output data: Instance d'application Flask configurée
Business constraints:
- Utilise SQLite comme base de données stockée dans le dossier instance
- Initialise SQLAlchemy et Flask-Migrate pour la gestion de la base de données
- Importe tous les modèles pour que Flask-Migrate puisse détecter les changements
- Enregistre tous les blueprints (contrôleurs) pour définir les routes de l'application
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Initialisation des extensions
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
    
    # Enregistrement des blueprints (contrôleurs)
    from app.controllers.views import views
    from app.controllers.list import bp as list_bp
    from app.controllers.sublist import bp as sublist_bp
    from app.controllers.activity import bp as activity_bp
    from app.controllers.settings import settings_bp
    from app.controllers.weekly_goal import weekly_goal_bp
    
    app.register_blueprint(views)
    app.register_blueprint(list_bp)
    app.register_blueprint(sublist_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(weekly_goal_bp)
    
    # Simple route pour tester que l'application fonctionne
    @app.route('/hello')
    def hello():
        return 'Bonjour, le semainier fonctionne!'
    
    return app
