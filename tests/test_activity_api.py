import unittest
import json
import os
import sys
from datetime import date, timedelta

# Ajout du chemin parent au PYTHONPATH pour pouvoir importer l'application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import List, Sublist, Activity
from app.models.activity import DurationSize


class ActivityAPITestCase(unittest.TestCase):
    """Tests pour l'API des activités"""
    
    def setUp(self):
        """Préparation avant chaque test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Création d'une liste et d'une sous-liste pour les tests
        list_obj = List(name="Liste Test")
        db.session.add(list_obj)
        db.session.commit()
        self.list_id = list_obj.id
        
        sublist = Sublist(name="Sous-liste Test", list_id=self.list_id)
        db.session.add(sublist)
        db.session.commit()
        self.sublist_id = sublist.id
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_activities_empty(self):
        """Test de récupération d'une liste vide d'activités"""
        response = self.client.get('/api/activities/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])
    
    def test_create_and_get_activity(self):
        """Test de création et récupération d'une activité"""
        # Création d'une activité
        response = self.client.post(
            '/api/activities/',
            data=json.dumps({
                'title': 'Activité Test',
                'list_id': self.list_id,
                'duration': 'M'
            }),
            content_type='application/json'
        )
        # Accepter 200 ou 201 pour la création
        self.assertIn(response.status_code, [200, 201])
        
        # Vérification des données retournées
        activity_data = json.loads(response.data)
        self.assertEqual(activity_data['title'], 'Activité Test')
        self.assertEqual(activity_data['list_id'], self.list_id)
        self.assertEqual(activity_data['duration'], 'M')
        
        # Récupération de l'activité par ID
        activity_id = activity_data['id']
        response = self.client.get(f'/api/activities/{activity_id}')
        self.assertEqual(response.status_code, 200)
        
        # Vérification des données de l'activité
        activity_data = json.loads(response.data)
        self.assertEqual(activity_data['title'], 'Activité Test')
        
        # Récupération de toutes les activités
        response = self.client.get('/api/activities/')
        self.assertEqual(response.status_code, 200)
        activities = json.loads(response.data)
        self.assertEqual(len(activities), 1)
    
    def test_create_activity_with_sublist(self):
        """Test de création d'une activité avec sous-liste"""
        response = self.client.post(
            '/api/activities/',
            data=json.dumps({
                'title': 'Activité avec sous-liste',
                'list_id': self.list_id,
                'sublist_id': self.sublist_id,
                'duration': 'S'
            }),
            content_type='application/json'
        )
        # Accepter 200 ou 201 pour la création
        self.assertIn(response.status_code, [200, 201])
        
        activity_data = json.loads(response.data)
        self.assertEqual(activity_data['sublist_id'], self.sublist_id)
    
    def test_create_activity_with_invalid_sublist(self):
        """Test de création d'une activité avec une sous-liste invalide"""
        # Création d'une autre liste et sous-liste
        other_list = List(name="Autre Liste")
        db.session.add(other_list)
        db.session.commit()
        
        other_sublist = Sublist(name="Autre Sous-liste", list_id=other_list.id)
        db.session.add(other_sublist)
        db.session.commit()
        
        # Tentative de création d'une activité avec une sous-liste qui n'appartient pas à la liste
        response = self.client.post(
            '/api/activities/',
            data=json.dumps({
                'title': 'Activité avec sous-liste invalide',
                'list_id': self.list_id,
                'sublist_id': other_sublist.id,
                'duration': 'S'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_create_activity_with_invalid_duration(self):
        """Test de création d'une activité avec une durée invalide"""
        response = self.client.post(
            '/api/activities/',
            data=json.dumps({
                'title': 'Activité avec durée invalide',
                'list_id': self.list_id,
                'duration': 'X'  # Valeur invalide
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_update_activity(self):
        """Test de mise à jour d'une activité"""
        # Création d'une activité
        response = self.client.post(
            '/api/activities/',
            data=json.dumps({
                'title': 'Activité Originale',
                'list_id': self.list_id,
                'duration': 'S'
            }),
            content_type='application/json'
        )
        activity_id = json.loads(response.data)['id']
        
        # Mise à jour de l'activité
        response = self.client.put(
            f'/api/activities/{activity_id}',
            data=json.dumps({
                'title': 'Activité Modifiée',
                'duration': 'L',
                'is_priority': True
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Vérification des modifications
        activity_data = json.loads(response.data)
        self.assertEqual(activity_data['title'], 'Activité Modifiée')
        self.assertEqual(activity_data['duration'], 'L')
        self.assertTrue(activity_data['is_priority'])
    
    def test_mark_activity_as_completed(self):
        """Test pour marquer une activité comme terminée"""
        # Création d'une activité
        response = self.client.post(
            '/api/activities/',
            data=json.dumps({
                'title': 'Activité à terminer',
                'list_id': self.list_id,
                'duration': 'M'
            }),
            content_type='application/json'
        )
        activity_id = json.loads(response.data)['id']
        
        # Vérification que l'activité n'est pas terminée
        activity_data = json.loads(response.data)
        self.assertFalse(activity_data['is_completed'])
        
        # Marquer comme terminée
        response = self.client.post(f'/api/activities/{activity_id}/complete')
        self.assertIn(response.status_code, [200, 201])
        
        # Vérification que l'activité est maintenant terminée
        activity_data = json.loads(response.data)
        self.assertTrue(activity_data['is_completed'])
        self.assertIsNotNone(activity_data['completed_at'])
    
    def test_set_activity_due_date(self):
        """Test pour définir l'échéance à la semaine courante/prochaine"""
        # Création d'une activité
        response = self.client.post(
            '/api/activities/',
            data=json.dumps({
                'title': 'Activité échéance',
                'list_id': self.list_id,
                'duration': 'M'
            }),
            content_type='application/json'
        )
        activity_id = json.loads(response.data)['id']
        
        # Définir l'échéance à la semaine courante
        try:
            response = self.client.post(f'/api/activities/{activity_id}/set-current-week')
            self.assertIn(response.status_code, [200, 201])
            
            # Vérification de la date d'échéance
            activity_data = json.loads(response.data)
            today = date.today()
            days_until_sunday = 6 - today.weekday()
            expected_date = today + timedelta(days=days_until_sunday)
            
            # Convertir la date de réponse en objet date pour comparaison
            due_date_str = activity_data['due_date']  # Format ISO (YYYY-MM-DD)
            due_date = date.fromisoformat(due_date_str)
            
            self.assertEqual(due_date, expected_date)
        except Exception as e:
            print(f"Error in current week: {str(e)}")
            raise
        
        # Définir l'échéance à la semaine prochaine
        try:
            response = self.client.post(f'/api/activities/{activity_id}/set-next-week')
            self.assertIn(response.status_code, [200, 201])
            
            # Vérification de la date d'échéance
            activity_data = json.loads(response.data)
            expected_next_week = expected_date + timedelta(days=7)
            
            # Convertir la date de réponse
            due_date_str = activity_data['due_date']
            due_date = date.fromisoformat(due_date_str)
            
            self.assertEqual(due_date, expected_next_week)
        except Exception as e:
            print(f"Error in next week: {str(e)}")
            raise
    
    def test_delete_activity(self):
        """Test de suppression d'une activité"""
        # Création d'une activité
        response = self.client.post(
            '/api/activities/',
            data=json.dumps({
                'title': 'Activité à supprimer',
                'list_id': self.list_id,
                'duration': 'S'
            }),
            content_type='application/json'
        )
        activity_id = json.loads(response.data)['id']
        
        # Suppression de l'activité
        response = self.client.delete(f'/api/activities/{activity_id}')
        self.assertEqual(response.status_code, 200)
        
        # Vérification que l'activité n'existe plus
        response = self.client.get(f'/api/activities/{activity_id}')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
