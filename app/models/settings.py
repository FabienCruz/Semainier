"""
File: app/models/settings.py
Role: Modèle de données pour les paramètres de l'application
Description: Définit le modèle Settings qui stocke les paramètres globaux de l'application semainier
Input data: N/A (géré par l'application)
Output data: Objet Settings contenant les paramètres de configuration
Business constraints:
- L'unité de temps doit être entre 5 et 60 minutes (par palier de 5)
- L'heure de début de journée est au format HH:MM
- Le nombre d'unités par jour est limité à un entier positif
- La WIP limit ne peut pas dépasser (units_per_day * 7)
"""

from datetime import datetime
from app import db

class Settings(db.Model):
    """
    Modèle de données pour les paramètres de l'application
    
    Stocke les paramètres globaux tels que l'unité de temps, l'heure de début
    de journée, le nombre d'unités par jour et la limite de travail en cours.
    """
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    time_unit_minutes = db.Column(db.Integer, nullable=False, default=30)
    day_start_time = db.Column(db.String(5), nullable=False, default="09:00")
    time_units_per_day = db.Column(db.Integer, nullable=False, default=20)
    wip_limit = db.Column(db.Integer, nullable=False, default=100)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Settings id={self.id}, time_unit={self.time_unit_minutes}min>"
    
    def to_dict(self):
        """
        Convertit l'objet Settings en dictionnaire
        
        Returns:
            dict: Dictionnaire des paramètres
        """
        return {
            'time_unit_minutes': self.time_unit_minutes,
            'day_start_time': self.day_start_time,
            'time_units_per_day': self.time_units_per_day,
            'wip_limit': self.wip_limit
        }
    
    def validate(self):
        """
        Valide les paramètres selon les contraintes métier
        
        Returns:
            tuple: (is_valid, errors_dict)
        """
        errors = {}
        
        # Validation de time_unit_minutes
        if self.time_unit_minutes < 5 or self.time_unit_minutes > 60:
            errors['time_unit_minutes'] = "L'unité de temps doit être entre 5 et 60 minutes"
        elif self.time_unit_minutes % 5 != 0:
            errors['time_unit_minutes'] = "L'unité de temps doit être un multiple de 5"
        
        # Validation de day_start_time
        try:
            datetime.strptime(self.day_start_time, "%H:%M")
            # Vérifier que les minutes sont par palier de 5
            hours, minutes = map(int, self.day_start_time.split(':'))
            if minutes % 5 != 0:
                errors['day_start_time'] = "Les minutes doivent être par palier de 5"
        except ValueError:
            errors['day_start_time'] = "L'heure de début doit être au format HH:MM"
        
        # Validation de time_units_per_day
        if self.time_units_per_day <= 0:
            errors['time_units_per_day'] = "Le nombre d'unités par jour doit être supérieur à 0"
        
        # Validation de wip_limit
        max_wip_limit = self.time_units_per_day * 7
        if self.wip_limit <= 0:
            errors['wip_limit'] = "La WIP limit doit être supérieure à 0"
        elif self.wip_limit > max_wip_limit:
            errors['wip_limit'] = f"La WIP limit ne peut pas dépasser {max_wip_limit} (time_units_per_day × 7)"
        
        return len(errors) == 0, errors
    
    # Méthodes d'accès aux données
    @classmethod
    def get_settings(cls):
        """
        Récupère les paramètres de l'application ou crée des valeurs par défaut
            
        Returns:
            Settings: Instance des paramètres, ou None en cas d'erreur
        """
        try:
            settings = cls.query.first()
            
            if not settings:
                settings = cls(
                    time_unit_minutes=30,
                    day_start_time="09:00",
                    time_units_per_day=20,
                    wip_limit=100
                )
                db.session.add(settings)
                db.session.commit()
                
            return settings
        except Exception as e:
            db.session.rollback()
            return None
    
    @classmethod
    def get_by_id(cls, id):
        """
        Récupère les paramètres par leur ID
        
        Args:
            id (int): ID des paramètres
            
        Returns:
            Settings: Instance des paramètres, ou None si non trouvé
        """
        return db.session.get(cls, id)
    
@classmethod
def update(cls, data):
    """
    Met à jour les paramètres de l'application
    
    Args:
        data (dict): Dictionnaire des champs à mettre à jour
    
    Returns:
        Settings: Instance mise à jour, ou None en cas d'erreur
    """
    try:
        settings = cls.get_settings()
        if not settings:
            return None
        
        # Mise à jour des champs
        for key, value in data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        # Valider les paramètres
        is_valid, _ = settings.validate()
        if not is_valid:
            db.session.rollback()
            return None
        
        db.session.commit()
        return settings
    except Exception as e:
        db.session.rollback()
        return None