"""
File: app/models/activity.py
Role: Modèle de données pour les activités
Description: Définit le modèle Activity qui représente les tâches et activités dans le semainier
Input data: Titre, liste parente, sous-liste optionnelle, durée, date d'échéance, etc.
Output data: Objet Activity avec méthodes pour gérer les échéances et le statut
Business constraints:
- La durée peut être S (small), M (medium) ou L (large)
- Une activité doit toujours appartenir à une liste
- Si une sous-liste est spécifiée, elle doit appartenir à la liste parente
- La date d'échéance par défaut est fixée au 31/12/2099
- L'heure de début par défaut est fixée à 23:59
- Les activités peuvent être marquées comme prioritaires ou terminées
"""

from app import db
from datetime import datetime, timezone, date, timedelta, time
from enum import Enum

class DurationSize(Enum):
    SMALL = 'S'
    MEDIUM = 'M'
    LARGE = 'L'

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id', ondelete='CASCADE'), nullable=False)
    sublist_id = db.Column(db.Integer, db.ForeignKey('sublists.id', ondelete='SET NULL'), nullable=True)
    
    # Durée et échéance
    duration = db.Column(db.Enum(DurationSize), default=DurationSize.SMALL)
    due_date = db.Column(db.Date, default=lambda: date(2099, 12, 31))
    start_time = db.Column(db.Time, default=lambda: time(23, 59), nullable=False)  # Heure de démarrage, par défaut 23:59
    
    # Attributs spécifiques
    is_priority = db.Column(db.Boolean, default=False)  # Si c'est prioritaire
    position = db.Column(db.Integer, default=0)  # Position dans la liste
    is_active = db.Column(db.Boolean, default=True)  # Gestion de l'affichage
    
    # Suivi de statut
    is_completed = db.Column(db.Boolean, default=False)  # Si réalisée
    completed_at = db.Column(db.DateTime, nullable=True)  # Date de réalisation
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Contrainte pour vérifier que sublist_id appartient à list_id
    @staticmethod
    def validate_sublist_belongs_to_list(list_id, sublist_id):
        """Vérifie que la sous-liste appartient bien à la liste parente."""
        if sublist_id is None:
            return True
        
        from app.models.sublist import Sublist
        sublist = Sublist.query.filter_by(id=sublist_id).first()
        
        return sublist is not None and sublist.list_id == list_id

    def save(self):
        """Sauvegarde l'activité après validation."""
        if not self.validate_sublist_belongs_to_list(self.list_id, self.sublist_id):
            raise ValueError("La sous-liste sélectionnée n'appartient pas à la liste parente.")
        
        db.session.add(self)
        db.session.commit()
        return self
    
    def __init__(self, title, list_id, **kwargs):
        self.title = title
        self.list_id = list_id
        
        # Attributs optionnels
        self.sublist_id = kwargs.get('sublist_id')
        self.duration = kwargs.get('duration', DurationSize.SMALL)
        self.due_date = kwargs.get('due_date', date(2099, 12, 31))
        self.start_time = kwargs.get('start_time', time(23, 59))
        self.is_priority = kwargs.get('is_priority', False)
        self.position = kwargs.get('position', 0)
        self.is_active = kwargs.get('is_active', True)
    
    def __repr__(self):
        return f'<Activity {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'list_id': self.list_id,
            'sublist_id': self.sublist_id,
            'duration': self.duration.value,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'is_priority': self.is_priority,
            'position': self.position,
            'is_active': self.is_active,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def mark_as_completed(self):
        """Marque l'activité comme terminée et enregistre la date/heure"""
        self.is_completed = True
        self.completed_at = datetime.now(timezone.utc)
    
    def mark_as_current_week(self):
        """Définit l'échéance à la fin de la semaine en cours"""
        today = date.today()
        # Calculer le nombre de jours jusqu'à dimanche (où lundi=0, dimanche=6)
        days_until_sunday = 6 - today.weekday()
        if days_until_sunday == 0:  # Si c'est dimanche
            self.due_date = today
        else:
            self.due_date = today + timedelta(days=days_until_sunday)
    
    def mark_as_next_week(self):
        """Définit l'échéance à la fin de la semaine prochaine"""
        today = date.today()
        # Calculer le nombre de jours jusqu'au dimanche prochain
        days_until_sunday = 6 - today.weekday()
        self.due_date = today + timedelta(days=days_until_sunday + 7)
        
    def duplicate(self):
        """Crée une copie exacte de l'activité avec un nouvel ID"""
        new_activity = Activity(
            title=self.title,
            list_id=self.list_id,
            sublist_id=self.sublist_id,
            duration=self.duration,
            due_date=date(2099, 12, 31),  # Date par défaut pour la duplication
            start_time=time(23, 59),      # Heure par défaut pour la duplication
            is_priority=self.is_priority,
            position=self.position + 1,   # Positionner après l'activité originale
            is_active=True
        )
        # La nouvelle activité n'est jamais complétée
        new_activity.is_completed = False
        new_activity.completed_at = None
        
        # Décaler les positions des activités suivantes
        following_activities = Activity.query.filter(
            Activity.list_id == self.list_id,
            Activity.sublist_id == self.sublist_id,
            Activity.position > self.position
        ).all()
        
        for act in following_activities:
            act.position += 1
            
        db.session.add(new_activity)
        db.session.commit()
        
        return new_activity
    
    def get_duration_in_minutes(self, unit_time=30):
        """Calcule la durée en minutes selon la taille du bloc"""
        if self.duration == DurationSize.SMALL:
            return unit_time
        elif self.duration == DurationSize.MEDIUM:
            return unit_time * 3
        elif self.duration == DurationSize.LARGE:
            return unit_time * 6
        return 0
    
    @staticmethod
    def get_by_list_id(list_id):
        return Activity.query.filter_by(list_id=list_id).all()