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
    
    # Enregistrement des blueprints (contrôleurs)
    # On les ajoutera au fur et à mesure de leur création
    # from app.controllers.home import bp as home_bp
    # app.register_blueprint(home_bp)
    
    # Simple route pour tester que l'application fonctionne
    @app.route('/hello')
    def hello():
        return 'Bonjour, le semainier fonctionne!'
    
    return app