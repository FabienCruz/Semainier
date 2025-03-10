# app/__init__.py
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
    from app.models import List, Sublist, Activity
    
    # Enregistrement des blueprints (contrôleurs)
    from app.controllers.list import bp as list_bp
    from app.controllers.sublist import bp as sublist_bp
    from app.controllers.activity import bp as activity_bp
    from app.controllers.views import views
    
    app.register_blueprint(list_bp)
    app.register_blueprint(sublist_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(views)
    
    # Simple route pour tester que l'application fonctionne
    @app.route('/hello')
    def hello():
        return 'Bonjour, le semainier fonctionne!'
    
    return app

"""
token git: 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
"""