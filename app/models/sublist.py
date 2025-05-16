"""
File: app/models/sublist.py
Role: Modèle de données pour les sous-listes
Description: Définit le modèle Sublist qui permet d'organiser les activités en sous-catégories au sein d'une liste
Input data: Nom de la sous-liste, liste parente et position optionnelle
Output data: Objet Sublist avec relations vers ses activités associées
Business constraints:
- Une sous-liste doit obligatoirement appartenir à une liste parente
- Le nom d'une sous-liste doit être unique au sein d'une même liste parente
- La suppression d'une sous-liste entraîne la suppression cascade de toutes ses activités
- La position permet d'ordonner les sous-listes au sein d'une même liste
"""
from app import db
from datetime import datetime, timezone

class Sublist(db.Model):
    __tablename__ = 'sublists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id', ondelete='CASCADE'), nullable=False)
    position = db.Column(db.Integer, default=0)  # Pour le tri/ordonnancement
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Relations
    activities = db.relationship('Activity', backref='sublist', lazy=True, 
                                cascade='all, delete-orphan',
                                primaryjoin="Sublist.id == Activity.sublist_id")
    
    __table_args__ = (
        db.UniqueConstraint('name', 'list_id', name='uix_sublist_name_list'),
    )
    
    def __init__(self, name, list_id, position=0):
        self.name = name
        self.list_id = list_id
        self.position = position
    
    def __repr__(self):
        return f'<Sublist {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'list_id': self.list_id,
            'position': self.position,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def get_by_list_id(list_id):
        return Sublist.query.filter_by(list_id=list_id).all()

