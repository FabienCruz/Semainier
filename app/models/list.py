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
