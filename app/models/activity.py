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
    
    # ==================================================================
    # Modèle de données
    # ==================================================================
    
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
    
    # ==================================================================
    # Constructeur
    # ==================================================================
    
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
    
    # ===================================================================
    # Méthodes
    # ===================================================================
    
    def set_completion(self, status):
        """
        Définit l'état de complétion de l'activité.
        
        Args:
            status (bool): Nouvel état de complétion (True pour terminé, False pour non terminé)
        """
        self.is_completed = status
        
        # Mise à jour de la date de complétion en fonction de l'état
        if status:
            self.completed_at = datetime.now(timezone.utc)
        else:
            self.completed_at = None
    
    def set_current_week(self):
        """Définit l'échéance à la fin de la semaine en cours"""
        today = date.today()
        # Calculer le nombre de jours jusqu'à dimanche (où lundi=0, dimanche=6)
        days_until_sunday = 6 - today.weekday()
        if days_until_sunday == 0:  # Si c'est dimanche
            self.due_date = today
        else:
            self.due_date = today + timedelta(days=days_until_sunday)

    def set_next_week(self):
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
            position=0,   # Positionner au début par défaut
            is_active=True
        )
        # La nouvelle activité n'est jamais complétée par défaut
        new_activity.is_completed = False
        new_activity.completed_at = None
            
        db.session.add(new_activity)
        db.session.commit()

        # Réinitialiser les positions après duplication
        Activity.reorder_positions(new_activity.list_id, new_activity.sublist_id)
        
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
    
    # Méthodes d'accès aux données enrichies

    @classmethod
    def get_by_id(cls, id):
        """Récupère une activité par son ID."""
        return db.session.get(cls, id)
    
    @classmethod
    def get_by_list_id(cls, list_id):
        """Récupère toutes les activités d'une liste."""
        return cls.query.filter_by(list_id=list_id).all()
    
    @classmethod
    def get_by_sublist_id(cls, sublist_id):
        """Récupère toutes les activités d'une sous-liste."""
        return cls.query.filter_by(sublist_id=sublist_id).all()
    
    @classmethod
    def get_filtered(cls, list_id=None, sublist_id=None, is_completed=None):
        """
        Récupère les activités avec des filtres.
        
        Args:
            list_id (int, optional): Filtre par liste
            sublist_id (int, optional): Filtre par sous-liste
            is_completed (bool, optional): Filtre par statut de complétion
        
        Returns:
            list: Liste des activités correspondant aux critères
        """
        query = cls.query
        
        if list_id is not None:
            query = query.filter_by(list_id=list_id)
        if sublist_id is not None:
            query = query.filter_by(sublist_id=sublist_id)
        if is_completed is not None:
            query = query.filter_by(is_completed=is_completed)
        
        return query.order_by(cls.due_date, cls.position).all()
    
    @classmethod
    def create(cls, data):
        """
        Crée une nouvelle activité.
        
        Args:
            data (dict): Dictionnaire contenant les données de l'activité
        
        Returns:
            Activity: L'activité créée, ou None en cas d'erreur
        """
        try:
            # Création avec les paramètres obligatoires
            activity = cls(
                title=data['title'],
                list_id=data['list_id']
            )
            
            # Paramètres optionnels
            if 'sublist_id' in data:
                activity.sublist_id = data['sublist_id']
            
            if 'duration' in data:
                activity.duration = data['duration']
            
            if 'due_date' in data:
                activity.due_date = data['due_date']
            
            if 'start_time' in data:
                activity.start_time = data['start_time']
            
            if 'is_priority' in data:
                activity.is_priority = data['is_priority']
            
            if 'position' in data:
                activity.position = data['position']
            
            if 'is_active' in data:
                activity.is_active = data['is_active']
            
            # Sauvegarde avec validation
            activity.save()
            # Réorganiser les positions après création
            cls.reorder_positions(activity.list_id, activity.sublist_id)
            
            return activity
        
        except Exception as e:
            db.session.rollback()
            return None
    
    @classmethod
    def update(cls, id, data):
        """
        Met à jour une activité existante.
        
        Args:
            id (int): ID de l'activité
            data (dict): Dictionnaire des champs à mettre à jour
        
        Returns:
            Activity: L'activité mise à jour, ou None en cas d'erreur
        """
        try:
            activity = cls.get_by_id(id)
            if not activity:
                return None
            
            # Mise à jour des champs
            for field in ['title', 'list_id', 'sublist_id', 'duration', 'due_date', 
                         'start_time', 'is_priority', 'position', 'is_active']:
                if field in data:
                    setattr(activity, field, data[field])
            
            # Sauvegarde avec validation
            return activity.save()
        except Exception as e:
            db.session.rollback()
            return None
    
    @classmethod
    def delete(cls, id):
        """
        Supprime une activité.
        
        Args:
            id (int): ID de l'activité à supprimer
        
        Returns:
            bool: True si succès, False sinon
        """
        try:
            activity = cls.get_by_id(id)
            if not activity:
                return False
            
            db.session.delete(activity)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    @classmethod
    def create_duplicate(cls, id):
        """
        Duplique une activité existante.
        
        Args:
            id (int): ID de l'activité à dupliquer
        
        Returns:
            Activity: La nouvelle activité créée, ou None en cas d'erreur
        """
        activity = cls.get_by_id(id)
        if not activity:
            return None
        
        return activity.duplicate()
    
    @classmethod
    def reorder_positions(cls, list_id, sublist_id=None):
        """
        Réorganise les positions des activités dans un conteneur (liste ou sous-liste).
        Assigne des positions séquentielles : 1, 2, 3, etc.
        
        Args:
            list_id (int): ID de la liste parente
            sublist_id (int, optional): ID de la sous-liste (None pour la liste racine)
        
        Returns:
            bool: True si succès, False sinon
        """
        try:
            # Récupérer toutes les activités du conteneur, triées par position
            activities = cls.query.filter_by(
                list_id=list_id, 
                sublist_id=sublist_id
            ).order_by(cls.position).all()
            
            # Réassigner les positions séquentiellement
            for index, activity in enumerate(activities, start=1):
                activity.position = index
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False