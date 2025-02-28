import unittest
import os
import sys
from datetime import datetime, timedelta

# Ajout du chemin parent au PYTHONPATH pour pouvoir importer l'application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import List, Sublist, Activity
from app.models.activity import DurationSize


class BaseTestCase(unittest.TestCase):
    """Base pour tous les tests utilisant la base de données"""
    
    def setUp(self):
        """Préparation avant chaque test"""
        self.app = create_app()
        # Configuration pour les tests
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class ListModelTestCase(BaseTestCase):
    """Tests pour le modèle List"""
    
    def test_create_list(self):
        """Test de création d'une liste"""
        list_obj = List(name="Test Liste")
        db.session.add(list_obj)
        db.session.commit()
        
        # Vérification que la liste a été créée avec un ID
        self.assertIsNotNone(list_obj.id)
        self.assertEqual(list_obj.name, "Test Liste")
        self.assertEqual(list_obj.color_code, "#3C91E6")  # Couleur par défaut
    
    def test_list_with_custom_color(self):
        """Test de création d'une liste avec une couleur personnalisée"""
        list_obj = List(name="Liste Colorée", color_code="#FF5733")
        db.session.add(list_obj)
        db.session.commit()
        
        self.assertEqual(list_obj.color_code, "#FF5733")
    
    def test_list_name_unique(self):
        """Test de l'unicité du nom de liste"""
        list1 = List(name="Liste Unique")
        db.session.add(list1)
        db.session.commit()
        
        # Tentative de création d'une liste avec le même nom
        list2 = List(name="Liste Unique")
        db.session.add(list2)
        
        # Doit lever une exception due à la contrainte d'unicité
        with self.assertRaises(Exception):
            db.session.commit()
        
        # Rollback pour nettoyer la session
        db.session.rollback()


class SublistModelTestCase(BaseTestCase):
    """Tests pour le modèle Sublist"""
    
    def setUp(self):
        super().setUp()
        # Création d'une liste pour les tests de sous-liste
        self.parent_list = List(name="Liste Parent")
        db.session.add(self.parent_list)
        db.session.commit()
    
    def test_create_sublist(self):
        """Test de création d'une sous-liste"""
        sublist = Sublist(name="Sous-liste Test", list_id=self.parent_list.id)
        db.session.add(sublist)
        db.session.commit()
        
        self.assertIsNotNone(sublist.id)
        self.assertEqual(sublist.name, "Sous-liste Test")
        self.assertEqual(sublist.list_id, self.parent_list.id)
    
    def test_sublist_list_relationship(self):
        """Test de la relation entre sous-liste et liste"""
        sublist = Sublist(name="Relation Test", list_id=self.parent_list.id)
        db.session.add(sublist)
        db.session.commit()
        
        # Vérification que la liste parent peut accéder à la sous-liste
        self.assertEqual(len(self.parent_list.sublists), 1)
        self.assertEqual(self.parent_list.sublists[0].name, "Relation Test")
        
        # Vérification que la sous-liste peut accéder à sa liste parent
        self.assertEqual(sublist.parent_list.name, "Liste Parent")
    
    def test_sublist_unique_name_per_list(self):
        """Test de l'unicité du nom de sous-liste dans une liste"""
        sublist1 = Sublist(name="Sous-liste Unique", list_id=self.parent_list.id)
        db.session.add(sublist1)
        db.session.commit()
        
        # Tentative de création d'une sous-liste avec le même nom dans la même liste
        sublist2 = Sublist(name="Sous-liste Unique", list_id=self.parent_list.id)
        db.session.add(sublist2)
        
        # Doit lever une exception due à la contrainte d'unicité
        with self.assertRaises(Exception):
            db.session.commit()
        
        db.session.rollback()
        
        # Création d'une nouvelle liste parent
        another_list = List(name="Autre Liste")
        db.session.add(another_list)
        db.session.commit()
        
        # Le même nom de sous-liste devrait être accepté dans une liste différente
        sublist3 = Sublist(name="Sous-liste Unique", list_id=another_list.id)
        db.session.add(sublist3)
        db.session.commit()
        
        self.assertIsNotNone(sublist3.id)


class ActivityModelTestCase(BaseTestCase):
    """Tests pour le modèle Activity"""
    
    def setUp(self):
        super().setUp()
        # Création des objets nécessaires pour les tests d'activité
        self.test_list = List(name="Liste Test")
        db.session.add(self.test_list)
        db.session.commit()
        
        self.test_sublist = Sublist(name="Sous-liste Test", list_id=self.test_list.id)
        db.session.add(self.test_sublist)
        db.session.commit()
    
    def test_create_activity(self):
        """Test de création d'une activité de base"""
        activity = Activity(
            title="Activité Test",
            list_id=self.test_list.id,
            duration=DurationSize.MEDIUM
        )
        db.session.add(activity)
        db.session.commit()
        
        self.assertIsNotNone(activity.id)
        self.assertEqual(activity.title, "Activité Test")
        self.assertEqual(activity.duration, DurationSize.MEDIUM)
        self.assertFalse(activity.is_completed)
        
        # Vérification des valeurs par défaut
        self.assertIsNotNone(activity.created_at)
        self.assertIsNotNone(activity.updated_at)
        self.assertIsNone(activity.completed_at)
        
        # La date d'échéance par défaut devrait être 31/12/2099
        default_date = datetime(2099, 12, 31).date()
        self.assertEqual(activity.due_date, default_date)
    
    def test_activity_with_sublist(self):
        """Test d'une activité associée à une sous-liste"""
        activity = Activity(
            title="Activité avec sous-liste",
            list_id=self.test_list.id,
            sublist_id=self.test_sublist.id,
            duration=DurationSize.SMALL
        )
        
        # Vérification de la validation
        self.assertTrue(Activity.validate_sublist_belongs_to_list(self.test_list.id, self.test_sublist.id))
        
        db.session.add(activity)
        db.session.commit()
        
        # Vérification des relations
        self.assertEqual(activity.list.name, "Liste Test")
        self.assertEqual(activity.sublist.name, "Sous-liste Test")
    
    def test_activity_sublist_validation(self):
        """Test de la validation de la relation sous-liste/liste"""
        # Création d'une autre liste et sous-liste
        another_list = List(name="Autre Liste")
        db.session.add(another_list)
        db.session.commit()
        
        another_sublist = Sublist(name="Autre Sous-liste", list_id=another_list.id)
        db.session.add(another_sublist)
        db.session.commit()
        
        # Tentative de création d'une activité avec une sous-liste qui n'appartient pas à la liste
        activity = Activity(
            title="Activité invalide",
            list_id=self.test_list.id,
            sublist_id=another_sublist.id,
            duration=DurationSize.LARGE
        )
        
        # La validation devrait échouer
        self.assertFalse(Activity.validate_sublist_belongs_to_list(self.test_list.id, another_sublist.id))
        
        # Tentative de sauvegarde qui devrait échouer
        with self.assertRaises(ValueError):
            activity.save()
    
    def test_complete_activity(self):
        """Test du marquage d'une activité comme terminée"""
        activity = Activity(
            title="Activité à terminer",
            list_id=self.test_list.id,
            duration=DurationSize.SMALL
        )
        db.session.add(activity)
        db.session.commit()
        
        # Vérification de l'état initial
        self.assertFalse(activity.is_completed)
        self.assertIsNone(activity.completed_at)
        
        # Marquer comme terminée
        activity.mark_as_completed()
        db.session.commit()
        
        # Vérifier le changement d'état
        self.assertTrue(activity.is_completed)
        self.assertIsNotNone(activity.completed_at)
    
    def test_set_due_date_current_week(self):
        """Test de définition de l'échéance à la semaine en cours"""
        activity = Activity(
            title="Activité semaine courante",
            list_id=self.test_list.id,
            duration=DurationSize.MEDIUM
        )
        
        # Date initiale (31/12/2099)
        initial_date = activity.due_date
        
        # Définir l'échéance à la semaine en cours
        activity.mark_as_current_week()
        
        # La nouvelle date devrait être différente
        self.assertNotEqual(activity.due_date, initial_date)
        
        # Calculer le dimanche de la semaine en cours
        today = datetime.now().date()
        days_until_sunday = 6 - today.weekday()
        expected_date = today + timedelta(days=days_until_sunday)
        
        # Vérifier que la date d'échéance est bien le dimanche 
        self.assertEqual(activity.due_date, expected_date)


if __name__ == '__main__':
    unittest.main()
