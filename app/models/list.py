"""
File: app/models/list.py
Role: Modèle de données pour les listes
Description: Définit le modèle List qui représente les catégories principales pour organiser les activités
Input data: Nom de la liste et code couleur optionnel
Output data: Objet List avec relations vers les sous-listes et activités associées
Business constraints:
- Le nom de la liste doit être unique
- Une liste peut contenir plusieurs sous-listes et activités
- La suppression d'une liste entraîne la suppression cascade de toutes ses sous-listes et activités
- Le code couleur par défaut est #3C91E6 (bleu)
"""

from app import db
from datetime import datetime, timezone

class List(db.Model):
    __tablename__ = 'lists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    color_code = db.Column(db.String(7), default='#3C91E6')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relations
    sublists = db.relationship('Sublist', backref='parent_list', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='list', lazy=True, 
                                cascade='all, delete-orphan', 
                                primaryjoin="List.id == Activity.list_id")
    
    def __init__(self, name, color_code=None):
        self.name = name
        self.color_code = color_code or '#3C91E6'
    
    def __repr__(self):
        return f'<List {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color_code': self.color_code,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    # Méthodes d'accès aux données
    @classmethod
    def get_by_id(cls, id):
        """Récupère une liste par son ID."""
        return db.session.get(cls, id)
    
    @classmethod
    def get_all(cls):
        """Récupère toutes les listes triées par nom."""
        return cls.query.order_by(cls.name).all()
    
    @classmethod
    def create(cls, data):
        """
        Crée une nouvelle liste avec les données fournies.
        
        Args:
            data (dict): Dictionnaire contenant au moins 'name' et optionnellement 'color_code'
            
        Returns:
            List: L'objet liste créé
            
        Raises:
            ValueError: Si le nom est déjà utilisé
        """
        # Vérification que le nom n'existe pas déjà
        if cls.query.filter_by(name=data['name']).first():
            raise ValueError("Une liste avec ce nom existe déjà")
            
        list_obj = cls(
            name=data['name'],
            color_code=data.get('color_code')
        )
        
        db.session.add(list_obj)
        db.session.commit()
        
        return list_obj
    
    def update(self, data):
        """
        Met à jour cette liste avec les données fournies.
        
        Args:
            data (dict): Dictionnaire contenant les données à mettre à jour
            
        Returns:
            List: L'objet liste mis à jour (self)
            
        Raises:
            ValueError: Si le nouveau nom est déjà utilisé par une autre liste
        """
        if 'name' in data and data['name'] != self.name:
            existing = List.query.filter_by(name=data['name']).first()
            if existing and existing.id != self.id:
                raise ValueError("Une liste avec ce nom existe déjà")
            
            self.name = data['name']
            
        if 'color_code' in data:
            self.color_code = data['color_code']
            
        db.session.commit()
        
        return self
    
    def delete(self):
        """
        Supprime cette liste de la base de données.
        Supprime également toutes les sous-listes et activités associées (cascade).
        
        Returns:
            str: Message de confirmation
        """
        name = self.name
        db.session.delete(self)
        db.session.commit()
        
        return f"Liste '{name}' supprimée avec succès"
