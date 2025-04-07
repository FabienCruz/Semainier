# Import des modèles pour les rendre disponibles lorsque 'from app.models import *' est utilisé

from app.models.list import List
from app.models.sublist import Sublist
from app.models.activity import Activity
from app.models.settings import Settings 
from app.models.weekly_goals import WeeklyGoal

# Cette ligne permet de spécifier quels noms seront importés lors d'un 'from app.models import *'
__all__ = ['List', 'Sublist', 'Activity', 'Settings', 'WeeklyGoal']
