import unittest
import json
import os
import sys

# Ajout du chemin parent au PYTHONPATH pour pouvoir importer l'application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import List, Sublist


class SublistAPITestCase(unittest.TestCase):
    """Tests pour l'API des sous-listes"""
    
    def setUp(self):
        """Préparation avant chaque test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Création d'une liste parente pour les tests
        list_obj = List(name="Liste Parent")
        db.session.add(list_obj)
        db.session.commit()
        self.parent_list_id = list_obj.id
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_sublists_empty(self):
        """Test de récupération d'une liste vide de sous-listes"""
        response = self.client.get('/api/sublists/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])
    
    def test_create_and_get_sublist(self):
        """Test de création et récupération d'une sous-liste"""
        # Création d'une sous-liste
        response = self.client.post(
            '/api/sublists/',
            data=json.dumps({
                'name': 'Sous-liste Test',
                'list_id': self.parent_list_id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # Vérification des données retournées
        sublist_data = json.loads(response.data)
        self.assertEqual(sublist_data['name'], 'Sous-liste Test')
        self.assertEqual(sublist_data['list_id'], self.parent_list_id)
        
        # Récupération de la sous-liste par ID
        sublist_id = sublist_data['id']
        response = self.client.get(f'/api/sublists/{sublist_id}')
        self.assertEqual(response.status_code, 200)
        
        # Vérification des données de la sous-liste
        sublist_data = json.loads(response.data)
        self.assertEqual(sublist_data['name'], 'Sous-liste Test')
        
        # Récupération de toutes les sous-listes
        response = self.client.get('/api/sublists/')
        self.assertEqual(response.status_code, 200)
        sublists = json.loads(response.data)
        self.assertEqual(len(sublists), 1)
        
        # Récupération des sous-listes filtrées par liste parente
        response = self.client.get(f'/api/sublists/?list_id={self.parent_list_id}')
        self.assertEqual(response.status_code, 200)
        sublists = json.loads(response.data)
        self.assertEqual(len(sublists), 1)
    
    def test_create_sublist_with_position(self):
        """Test de création d'une sous-liste avec position personnalisée"""
        response = self.client.post(
            '/api/sublists/',
            data=json.dumps({
                'name': 'Sous-liste Positionnée',
                'list_id': self.parent_list_id,
                'position': 5
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        sublist_data = json.loads(response.data)
        self.assertEqual(sublist_data['position'], 5)
    
    def test_create_sublist_missing_data(self):
        """Test de création d'une sous-liste avec données manquantes (doit échouer)"""
        # Sans nom
        response = self.client.post(
            '/api/sublists/',
            data=json.dumps({'list_id': self.parent_list_id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Sans liste parente
        response = self.client.post(
            '/api/sublists/',
            data=json.dumps({'name': 'Sous-liste Sans Parent'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_create_sublist_invalid_parent(self):
        """Test de création d'une sous-liste avec une liste parente inexistante"""
        response = self.client.post(
            '/api/sublists/',
            data=json.dumps({
                'name': 'Sous-liste Orpheline',
                'list_id': 9999  # ID inexistant
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
    
    def test_create_duplicate_sublist(self):
        """Test de création d'une sous-liste avec un nom dupliqué dans la même liste"""
        # Première sous-liste
        self.client.post(
            '/api/sublists/',
            data=json.dumps({
                'name': 'Sous-liste Unique',
                'list_id': self.parent_list_id
            }),
            content_type='application/json'
        )
        
        # Tentative de création d'une sous-liste avec le même nom
        response = self.client.post(
            '/api/sublists/',
            data=json.dumps({
                'name': 'Sous-liste Unique',
                'list_id': self.parent_list_id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Création d'une autre liste parente
        list_obj = List(name="Autre Liste")
        db.session.add(list_obj)
        db.session.commit()
        another_list_id = list_obj.id
        
        # Le même nom dans une liste différente devrait être accepté
        response = self.client.post(
            '/api/sublists/',
            data=json.dumps({
                'name': 'Sous-liste Unique',
                'list_id': another_list_id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
    
    def test_update_sublist(self):
        """Test de mise à jour d'une sous-liste"""
        # Création d'une sous-liste
        response = self.client.post(
            '/api/sublists/',
            data=json.dumps({
                'name': 'Sous-liste Originale',
                'list_id': self.parent_list_id
            }),
            content_type='application/json'
        )
        sublist_id = json.loads(response.data)['id']
        
        # Mise à jour de la sous-liste
        response = self.client.put(
            f'/api/sublists/{sublist_id}',
            data=json.dumps({
                'name': 'Sous-liste Modifiée',
                'position': 10
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Vérification des modifications
        sublist_data = json.loads(response.data)
        self.assertEqual(sublist_data['name'], 'Sous-liste Modifiée')
        self.assertEqual(sublist_data['position'], 10)
        
        # Vérification via une requête GET
        response = self.client.get(f'/api/sublists/{sublist_id}')
        sublist_data = json.loads(response.data)
        self.assertEqual(sublist_data['name'], 'Sous-liste Modifiée')
    
    def test_delete_sublist(self):
        """Test de suppression d'une sous-liste"""
        # Création d'une sous-liste
        response = self.client.post(
            '/api/sublists/',
            data=json.dumps({
                'name': 'Sous-liste à Supprimer',
                'list_id': self.parent_list_id
            }),
            content_type='application/json'
        )
        sublist_id = json.loads(response.data)['id']
        
        # Suppression de la sous-liste
        response = self.client.delete(f'/api/sublists/{sublist_id}')
        self.assertEqual(response.status_code, 200)
        
        # Vérification que la sous-liste n'existe plus
        response = self.client.get(f'/api/sublists/{sublist_id}')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
