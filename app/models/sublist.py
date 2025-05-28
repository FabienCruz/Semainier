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
    
    # Méthodes d'accès aux données
    @classmethod
    def get_by_id(cls, id):
        """Récupère une sous-liste par son ID."""
        return db.session.get(cls, id)
    
    @classmethod
    def get_by_list_id(cls, list_id):
        """Récupère toutes les sous-listes d'une liste spécifique, y compris la sous-liste virtuelle."""
        sublists = cls.query.filter_by(list_id=list_id).order_by(cls.position).all()
        
        # Ajouter la sous-liste virtuelle au début de la liste
        sublists.insert(0, {
            'id': 0,
            'name': 'Aucune sous-liste',
            'list_id': list_id,
            'position': 0
        })
        
        return sublists
    
    @classmethod
    def exists_with_name_in_list(cls, name, list_id, exclude_id=None):
        """
        Vérifie si une sous-liste avec ce nom existe déjà dans la liste spécifiée.
        
        Args:
            name (str): Nom de la sous-liste à vérifier
            list_id (int): ID de la liste parente
            exclude_id (int, optional): ID d'une sous-liste à exclure de la vérification
                                       (utile pour les mises à jour)
        
        Returns:
            bool: True si une sous-liste avec ce nom existe déjà, False sinon
        """
        query = cls.query.filter_by(name=name, list_id=list_id)
        if exclude_id is not None:
            query = query.filter(cls.id != exclude_id)
        return query.first() is not None
    
    @classmethod
    def create(cls, name, list_id, position=0, is_default=False):
        """
        Crée une nouvelle sous-liste.
        
        Args:
            name (str): Nom de la sous-liste
            list_id (int): ID de la liste parente
            position (int, optional): Position d'affichage
            is_default (bool, optional): Indique si c'est la sous-liste par défaut
        
        Returns:
            Sublist: La sous-liste créée, ou None en cas d'erreur
        """
        try:
            sublist = cls(name=name, list_id=list_id, position=position)
            db.session.add(sublist)
            db.session.commit()
            return sublist
        except Exception as e:
            db.session.rollback()
            return None
    
    @classmethod
    def update(cls, id, data):
        """
        Met à jour une sous-liste existante.
        
        Args:
            id (int): ID de la sous-liste à mettre à jour
            data (dict): Dictionnaire des champs à mettre à jour
        
        Returns:
            Sublist: La sous-liste mise à jour, ou None en cas d'erreur
        """
        try:
            sublist = cls.get_by_id(id)
            if not sublist:
                return None
            
            for key, value in data.items():
                if hasattr(sublist, key):
                    setattr(sublist, key, value)
            
            db.session.commit()
            return sublist
        except Exception as e:
            db.session.rollback()
            return None
    
    @classmethod
    def delete(cls, id):
        """
        Supprime une sous-liste et toutes ses activités associées.
        
        Args:
            id (int): ID de la sous-liste à supprimer
        
        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        try:
            sublist = cls.get_by_id(id)
            if not sublist:
                return False
            
            db.session.delete(sublist)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False