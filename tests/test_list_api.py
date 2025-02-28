import unittest
import json
import os
import sys

# Ajout du chemin parent au PYTHONPATH pour pouvoir importer l'application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import List


class ListAPITestCase(unittest.TestCase):
    """Tests pour l'API des listes"""
    
    def setUp(self):
        """Préparation avant chaque test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_lists_empty(self):
        """Test de récupération d'une liste vide"""
        response = self.client.get('/api/lists/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])
    
    def test_create_and_get_list(self):
        """Test de création et récupération d'une liste"""
        # Création d'une liste
        response = self.client.post(
            '/api/lists/',
            data=json.dumps({'name': 'Liste Test'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # Vérification des données retournées
        list_data = json.loads(response.data)
        self.assertEqual(list_data['name'], 'Liste Test')
        self.assertEqual(list_data['color_code'], '#3C91E6')  # Couleur par défaut
        
        # Récupération de la liste par ID
        list_id = list_data['id']
        response = self.client.get(f'/api/lists/{list_id}')
        self.assertEqual(response.status_code, 200)
        
        # Vérification des données de la liste
        list_data = json.loads(response.data)
        self.assertEqual(list_data['name'], 'Liste Test')
        
        # Récupération de toutes les listes
        response = self.client.get('/api/lists/')
        self.assertEqual(response.status_code, 200)
        lists = json.loads(response.data)
        self.assertEqual(len(lists), 1)
    
    def test_create_list_with_custom_color(self):
        """Test de création d'une liste avec une couleur personnalisée"""
        response = self.client.post(
            '/api/lists/',
            data=json.dumps({
                'name': 'Liste Colorée',
                'color_code': '#FF5733'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        list_data = json.loads(response.data)
        self.assertEqual(list_data['color_code'], '#FF5733')
    
    def test_create_list_missing_name(self):
        """Test de création d'une liste sans nom (doit échouer)"""
        response = self.client.post(
            '/api/lists/',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_create_duplicate_list(self):
        """Test de création d'une liste avec un nom qui existe déjà (doit échouer)"""
        # Première liste
        self.client.post(
            '/api/lists/',
            data=json.dumps({'name': 'Liste Unique'}),
            content_type='application/json'
        )
        
        # Tentative de création d'une liste avec le même nom
        response = self.client.post(
            '/api/lists/',
            data=json.dumps({'name': 'Liste Unique'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_update_list(self):
        """Test de mise à jour d'une liste"""
        # Création d'une liste
        response = self.client.post(
            '/api/lists/',
            data=json.dumps({'name': 'Liste Original'}),
            content_type='application/json'
        )
        list_id = json.loads(response.data)['id']
        
        # Mise à jour de la liste
        response = self.client.put(
            f'/api/lists/{list_id}',
            data=json.dumps({
                'name': 'Liste Modifiée',
                'color_code': '#00FF00'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Vérification des modifications
        list_data = json.loads(response.data)
        self.assertEqual(list_data['name'], 'Liste Modifiée')
        self.assertEqual(list_data['color_code'], '#00FF00')
        
        # Vérification via une requête GET
        response = self.client.get(f'/api/lists/{list_id}')
        list_data = json.loads(response.data)
        self.assertEqual(list_data['name'], 'Liste Modifiée')
    
    def test_delete_list(self):
        """Test de suppression d'une liste"""
        # Création d'une liste
        response = self.client.post(
            '/api/lists/',
            data=json.dumps({'name': 'Liste à Supprimer'}),
            content_type='application/json'
        )
        list_id = json.loads(response.data)['id']
        
        # Suppression de la liste
        response = self.client.delete(f'/api/lists/{list_id}')
        self.assertEqual(response.status_code, 200)
        
        # Vérification que la liste n'existe plus
        response = self.client.get(f'/api/lists/{list_id}')
        self.assertEqual(response.status_code, 404)
        
        # Vérification que la liste n'apparaît plus dans la liste complète
        response = self.client.get('/api/lists/')
        lists = json.loads(response.data)
        self.assertEqual(len(lists), 0)


if __name__ == '__main__':
    unittest.main()
