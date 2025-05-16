"""
File: app/models/weekly_goal.py
Role: Modèle de données pour les objectifs hebdomadaires
Description: Définit le modèle WeeklyGoal qui stocke les objectifs textuels de la semaine
Input data: Date de début de semaine (lundi) et contenu textuel des objectifs
Output data: Objet WeeklyGoal avec propriété calculée pour la date de fin de semaine
Business constraints:
- La date de début doit toujours être un lundi (ajustée automatiquement si nécessaire)
- Le contenu textuel est limité à 500 caractères maximum
- Une seule entrée par semaine est autorisée (week_start est unique)
"""

from app import db
from datetime import datetime, timezone, date, timedelta

class WeeklyGoal(db.Model):
    __tablename__ = 'weekly_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    week_start = db.Column(db.Date, nullable=False, unique=True)
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __init__(self, week_start, content):
        # S'assurer que week_start est un lundi (weekday == 0)
        if isinstance(week_start, str):
            week_start = date.fromisoformat(week_start)
            
        # Ajuster à la date du lundi si ce n'est pas déjà un lundi
        weekday = week_start.weekday()
        if weekday != 0:
            # Ajuster à la date du lundi de la même semaine
            week_start = week_start - timedelta(days=weekday)
            
        self.week_start = week_start
        self.content = content
    
    @property
    def week_end(self):
        """Retourne la date de fin de semaine (dimanche)"""
        return self.week_start + timedelta(days=6)
    
    def __repr__(self):
        return f'<WeeklyGoal {self.week_start}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'week_start': self.week_start.isoformat(),
            'week_end': self.week_end.isoformat(),
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    # Méthodes d'accès aux données
    @classmethod
    def get_by_week_start(cls, week_start):
        """
        Récupère l'objectif de la semaine par sa date de début.
        S'assure que la date est bien un lundi.
        
        Args:
            week_start (date): Date de début de semaine
            
        Returns:
            WeeklyGoal: L'objectif de la semaine, ou None si non trouvé
        """
        if isinstance(week_start, str):
            week_start = date.fromisoformat(week_start)
            
        # Ajuster à la date du lundi si ce n'est pas déjà un lundi
        weekday = week_start.weekday()
        if weekday != 0:
            # Ajuster à la date du lundi de la même semaine
            week_start = week_start - timedelta(days=weekday)
        
        return cls.query.filter_by(week_start=week_start).first()
    
    @classmethod
    def create_or_update(cls, week_start, content):
        """
        Crée ou met à jour l'objectif de la semaine.
        
        Args:
            week_start (date): Date de début de semaine
            content (str): Contenu textuel des objectifs (max 500 caractères)
            
        Returns:
            tuple: (succès, WeeklyGoal/message d'erreur)
        """
        try:
            if len(content) > 500:
                return False, "Le contenu est limité à 500 caractères"
            
            # Chercher si un objectif existe déjà pour cette semaine
            weekly_goal = cls.get_by_week_start(week_start)
            
            if weekly_goal:
                # Mettre à jour l'objectif existant
                weekly_goal.content = content
            else:
                # Créer un nouvel objectif
                weekly_goal = cls(week_start=week_start, content=content)
                db.session.add(weekly_goal)
            
            db.session.commit()
            return True, weekly_goal
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erreur lors de la création/mise à jour de l'objectif: {str(e)}"
    
    @classmethod
    def get_current_week_goal(cls, current_date=None):
        """
        Récupère l'objectif de la semaine en cours.
        
        Args:
            current_date (date, optional): Date de référence (par défaut: aujourd'hui)
            
        Returns:
            WeeklyGoal: L'objectif de la semaine en cours, ou None si non trouvé
        """
        if current_date is None:
            current_date = date.today()
            
        # Calculer la date du lundi de la semaine en cours
        weekday = current_date.weekday()
        week_start = current_date - timedelta(days=weekday)
        
        return cls.get_by_week_start(week_start)