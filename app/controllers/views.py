# app/controllers/views.py

from flask import Blueprint, render_template, url_for, abort, request
from app.models.list import List
from app.models.sublist import Sublist
from app.models.activity import Activity

views = Blueprint('views', __name__)

# ===== Routes Principales =====

@views.route('/')
def dashboard():
    """Affiche le tableau de bord principal avec les trois colonnes."""
    return render_template('pages/dashboard.html')

@views.route('/settings')
def settings():
    """Affiche la page des paramètres."""
    return render_template('pages/settings.html')

# ===== Routes pour les composants =====

@views.route('/lists')
def get_lists():
    """Récupère et affiche toutes les listes avec leurs sous-listes et activités."""
    lists = List.query.all()
    return render_template('components/lists.html', lists=lists)

@views.route('/list/<int:list_id>')
def get_list(list_id):
    """Récupère et affiche une liste spécifique avec ses sous-listes et activités."""
    list_item = List.query.get_or_404(list_id)
    sublists = Sublist.query.filter_by(list_id=list_id).all()
    activities = Activity.query.filter_by(list_id=list_id, sublist_id=None).all()
    
    return render_template(
        'components/list_container.html',  # Utilise le nouveau template
        list_item=list_item,
        sublists=sublists,
        activities=activities
    )

@views.route('/sublist/<int:sublist_id>')
def get_sublist(sublist_id):
    """Récupère et affiche une sous-liste spécifique avec ses activités."""
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
    """Affiche le formulaire de création de liste."""
    return render_template('modals/create_edit_list_modal.html', 
                          title="Créer une liste")

@views.route('/modals/edit-list/<int:list_id>')
def edit_list_form(list_id):
    """Affiche le formulaire d'édition de liste."""
    list_item = List.query.get_or_404(list_id)
    return render_template('modals/create_edit_list_modal.html', 
                          title="Modifier une liste",
                          list=list_item,
                          list_id=list_id)

# ===== Routes pour les modales de Sous-liste =====

@views.route('/modals/create-sublist', defaults={'list_id': None})
@views.route('/modals/create-sublist/<int:list_id>')
def get_sublist_form(list_id):
    """Affiche le formulaire de création de sous-liste."""
    # Récupérer toutes les listes pour le sélecteur
    lists = List.query.all()
    return render_template('modals/create_edit_sublist_modal.html', 
                          title="Créer une sous-liste",
                          lists=lists,
                          selected_list_id=list_id)

@views.route('/modals/edit-sublist/<int:sublist_id>')
def edit_sublist_form(sublist_id):
    """Affiche le formulaire d'édition de sous-liste."""
    sublist = Sublist.query.get_or_404(sublist_id)
    lists = List.query.all()
    return render_template('modals/create_edit_sublist_modal.html', 
                          title="Modifier une sous-liste",
                          sublist=sublist,
                          lists=lists,
                          sublist_id=sublist_id)

@views.route('/api/sublists-for-list')
def get_sublists_for_list():
    """Endpoint AJAX pour récupérer les sous-listes d'une liste spécifique."""
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
    """Affiche le formulaire de création d'activité."""
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

# ===== Routes pour les modales de confirmation =====

@views.route('/modals/confirm-delete/<string:type>/<int:id>')
def get_delete_confirmation(type, id):
    """Affiche la confirmation de suppression pour une liste ou sous-liste."""
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