"""
app/controllers/views.py

Rôle fonctionnel: Contrôleur gérant l'affichage des vues principales et des composants HTMX

Description: Ce fichier contient toutes les routes de présentation du semainier,
incluant les 3 colonnes principales, les composants de liste/sous-liste/activité
et les modales de création/édition/suppression. Ces routes sont principalement appelées
via HTMX pour le rechargement partiel des éléments d'interface.

Données attendues:
- Paramètres d'URL (identifiants de liste, sous-liste, activité)
- Paramètres de requête pour les filtres et sélections

Données produites:
- Fragments HTML rendus par Jinja2 avec les modèles correspondants
- Structure complète (dashboard) ou partielle (composants) selon les appels

Contraintes:
- Les templates associés doivent être structurés pour un affichage correct
- Les composants doivent fonctionner indépendamment pour les mises à jour HTMX
- La navigation entre modales et composants est gérée côté client
"""

from flask import Blueprint, render_template, url_for, abort, request
from app.models.list import List
from app.models.sublist import Sublist
from app.models.activity import Activity
from app.models.settings import Settings

views = Blueprint('views', __name__)

# ===== Routes Principales =====

@views.route('/')
def dashboard():
    """
    Affiche le tableau de bord principal avec les trois colonnes.
    
    Cette route charge la page complète de l'application, incluant:
    - La colonne des listes/sous-listes
    - La colonne des objectifs de la semaine
    - La colonne de l'emploi du temps
    
    Retourne:
    - Page HTML complète du tableau de bord
    """
    return render_template('pages/dashboard.html')

@views.route('/settings')
def settings():
    """
    Affiche la page des paramètres de l'application.
    Cette page permet de configurer:
    - Les unités de temps
    - L'heure de début de journée
    - Le nombre d'unités par jour
    
    Retourne:
    - Page HTML des paramètres
    """
    
    # Récupérer les paramètres actuels
    settings_obj = Settings.query.first()
    
    return render_template('pages/settings.html', settings=settings_obj)

# ===== Routes pour les composants =====

@views.route('/lists')
def get_lists():
    """
    Récupère et affiche toutes les listes avec leurs sous-listes et activités.
    
    Cette route est appelée par HTMX pour charger la colonne de gauche.
    
    Retourne:
    - Rendu HTML du composant de liste complet
    """
    lists = List.query.all()
    return render_template('components/lists.html', lists=lists)

@views.route('/list/<int:list_id>')
def get_list(list_id):
    """
    Récupère et affiche une liste spécifique avec ses sous-listes et activités.
    
    Cette route est appelée par HTMX lors du clic sur une liste ou
    après la modification/création d'une liste.
    
    Paramètres:
    - list_id: Identifiant unique de la liste à afficher
    
    Retourne:
    - Rendu HTML du contenu de la liste spécifiée
    - Erreur 404 si la liste n'existe pas
    """
    list_item = List.query.get_or_404(list_id)
    sublists = Sublist.query.filter_by(list_id=list_id).all()
    activities = Activity.query.filter_by(list_id=list_id, sublist_id=None).all()
    
    return render_template(
        'components/list_content.html',
        list_item=list_item,
        sublists=sublists,
        activities=activities
    )

@views.route('/sublist/<int:sublist_id>')
def get_sublist(sublist_id):
    """
    Récupère et affiche une sous-liste spécifique avec ses activités.
    
    Cette route est appelée par HTMX lors du clic sur une sous-liste ou
    après la modification/création d'une sous-liste ou de ses activités.
    
    Paramètres:
    - sublist_id: Identifiant unique de la sous-liste à afficher
    
    Retourne:
    - Rendu HTML du contenu de la sous-liste spécifiée
    - Erreur 404 si la sous-liste n'existe pas
    """
    sublist = Sublist.query.get_or_404(sublist_id)
    activities = Activity.query.filter_by(sublist_id=sublist_id).all()
    
    return render_template(
        'components/sublist_item.html', 
        sublist=sublist, 
        activities=activities
    )

# ===== Routes pour les modales de Liste =====

@views.route('/modals/create-list')
def get_list_form():
    """
    Affiche le formulaire de création de liste.
    
    Cette route est appelée par HTMX pour ouvrir la modale de création.
    
    Retourne:
    - Rendu HTML du formulaire de création de liste
    """
    return render_template('modals/create_edit_list_modal.html', 
                          title="Créer une liste")

@views.route('/modals/edit-list/<int:list_id>')
def edit_list_form(list_id):
    """
    Affiche le formulaire d'édition de liste.
    
    Cette route est appelée par HTMX pour ouvrir la modale d'édition
    pré-remplie avec les données de la liste existante.
    
    Paramètres:
    - list_id: Identifiant unique de la liste à modifier
    
    Retourne:
    - Rendu HTML du formulaire d'édition de liste
    - Erreur 404 si la liste n'existe pas
    """
    list_item = List.query.get_or_404(list_id)
    return render_template('modals/create_edit_list_modal.html', 
                          title="Modifier une liste",
                          list=list_item,
                          list_id=list_id)

# ===== Routes pour les modales de Sous-liste =====

@views.route('/modals/create-sublist', defaults={'list_id': None})
@views.route('/modals/create-sublist/<int:list_id>')
def get_sublist_form(list_id):
    """
    Affiche le formulaire de création de sous-liste.
    
    Cette route est appelée par HTMX pour ouvrir la modale de création.
    Si list_id est fourni, le sélecteur de liste est pré-rempli.
    
    Paramètres:
    - list_id: Identifiant de la liste parente (optionnel)
    
    Retourne:
    - Rendu HTML du formulaire de création de sous-liste
    """
    # Récupérer toutes les listes pour le sélecteur
    lists = List.query.all()
    return render_template('modals/create_edit_sublist_modal.html', 
                          title="Créer une sous-liste",
                          lists=lists,
                          selected_list_id=list_id)

@views.route('/modals/edit-sublist/<int:sublist_id>')
def edit_sublist_form(sublist_id):
    """
    Affiche le formulaire d'édition de sous-liste.
    
    Cette route est appelée par HTMX pour ouvrir la modale d'édition
    pré-remplie avec les données de la sous-liste existante.
    
    Paramètres:
    - sublist_id: Identifiant unique de la sous-liste à modifier
    
    Retourne:
    - Rendu HTML du formulaire d'édition de sous-liste
    - Erreur 404 si la sous-liste n'existe pas
    """
    sublist = Sublist.query.get_or_404(sublist_id)
    lists = List.query.all()
    return render_template('modals/create_edit_sublist_modal.html', 
                          title="Modifier une sous-liste",
                          sublist=sublist,
                          lists=lists,
                          sublist_id=sublist_id)

@views.route('/api/sublists-for-list')
def get_sublists_for_list():
    """
    Endpoint AJAX pour récupérer les sous-listes d'une liste spécifique.
    
    Cette route est appelée dynamiquement lors du changement de sélection
    de liste dans les formulaires d'activité, pour mettre à jour les options
    de sous-listes disponibles.
    
    Paramètres de requête:
    - list_id: Identifiant de la liste pour filtrer les sous-listes
    - sublist_id: Identifiant de la sous-liste actuellement sélectionnée (optionnel)
    
    Retourne:
    - Rendu HTML des options de sous-liste pour la liste sélectionnée
    """
    list_id = request.args.get('list_id', type=int)
    if not list_id:
        return render_template('components/sublist_options.html', sublists=[])
    
    # Récupérer les sous-listes correspondant à la liste sélectionnée
    sublists = Sublist.query.filter_by(list_id=list_id).all()
    
    # Récupérer la sous-liste actuellement sélectionnée si présente dans la requête
    selected_sublist_id = request.args.get('sublist_id', type=int)
    
    return render_template(
        'components/sublist_options.html', 
        sublists=sublists,
        selected_sublist_id=selected_sublist_id
    )

# ===== Routes pour les modales d'Activité =====

@views.route('/modals/create-activity', defaults={'list_id': None})
@views.route('/modals/create-activity/<int:list_id>')
def get_activity_form(list_id):
    """
    Affiche le formulaire de création d'activité.
    
    Cette route est appelée par HTMX pour ouvrir la modale de création.
    Si list_id est fourni, le sélecteur de liste est pré-rempli et les
    sous-listes correspondantes sont chargées.
    
    Paramètres:
    - list_id: Identifiant de la liste parente (optionnel)
    
    Retourne:
    - Rendu HTML du formulaire de création d'activité
    """
    # Récupérer toutes les listes pour le sélecteur
    lists = List.query.all()
    sublists = []
    if list_id:
        sublists = Sublist.query.filter_by(list_id=list_id).all()
    
    return render_template('modals/create_edit_activity_modal.html', 
                          title="Créer une activité",
                          lists=lists,
                          sublists=sublists,
                          selected_list_id=list_id)

@views.route('/modals/edit-activity/<int:activity_id>')
def edit_activity_form(activity_id):
    """
    Affiche le formulaire d'édition d'activité.
    
    Cette route est appelée par HTMX pour ouvrir la modale d'édition
    pré-remplie avec les données de l'activité existante.
    
    Paramètres:
    - activity_id: Identifiant unique de l'activité à modifier
    
    Retourne:
    - Rendu HTML du formulaire d'édition d'activité
    - Erreur 404 si l'activité n'existe pas
    """
    activity = Activity.query.get_or_404(activity_id)
    lists = List.query.all()
    sublists = Sublist.query.filter_by(list_id=activity.list_id).all()
    
    return render_template('modals/create_edit_activity_modal.html', 
                          title="Modifier une activité",
                          activity=activity,
                          activity_id=activity_id,
                          lists=lists,
                          sublists=sublists)

# ===== Routes pour les modales de confirmation =====

@views.route('/modals/confirm-delete/<string:type>/<int:id>')
def get_delete_confirmation(type, id):
    """
    Affiche la confirmation de suppression pour une liste ou sous-liste.
    
    Cette route est appelée par HTMX pour ouvrir la modale de confirmation
    avant la suppression définitive d'un élément.
    
    Paramètres:
    - type: Type d'élément à supprimer ('list' ou 'sublist')
    - id: Identifiant unique de l'élément à supprimer
    
    Retourne:
    - Rendu HTML de la confirmation de suppression avec message approprié
    - Erreur 404 si l'élément n'existe pas
    - Erreur 400 si le type n'est pas valide
    """
    if type == 'list':
        item = List.query.get_or_404(id)
        name = item.name
        message = f"Êtes-vous sûr de vouloir supprimer la liste \"{name}\" ? Toutes les sous-listes et activités associées seront également supprimées."
        delete_url = url_for('list.delete_list', id=id)
    elif type == 'sublist':
        item = Sublist.query.get_or_404(id)
        name = item.name
        message = f"Êtes-vous sûr de vouloir supprimer la sous-liste \"{name}\" ? Toutes les activités associées seront également supprimées."
        delete_url = url_for('sublist.delete_sublist', id=id)
    else:
        abort(400)
        
    return render_template('modals/confirm_delete.html',
                          title="Confirmer la suppression",
                          message=message,
                          delete_url=delete_url)

# ===== Routes pour les modales d'objectif de la semaine =====

@views.route('/modals/weekly-goal')
def weekly_goal_form():
    """
    Affiche le formulaire d'édition des objectifs textuels de la semaine.
    
    Cette route est appelée par HTMX pour ouvrir la modale d'édition
    des objectifs hebdomadaires.
    
    Retourne:
    - Rendu HTML du formulaire d'édition des objectifs
    """
    from app.utils.date_utils import get_server_date_info
    from app.models.weekly_goals import WeeklyGoal
    from datetime import date
    
    # Récupérer les informations de la semaine courante
    week_info = get_server_date_info()
    start_date = date.fromisoformat(week_info['week_start'])
    
    # Rechercher l'objectif pour cette semaine
    weekly_goal = WeeklyGoal.query.filter_by(week_start=start_date).first()
    
    return render_template('modals/create_edit_weekly_goal_modal.html', 
                          title="Objectifs de la semaine",
                          week_display=week_info['display_range'],
                          content=weekly_goal.content if weekly_goal else "")