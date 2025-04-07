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
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }