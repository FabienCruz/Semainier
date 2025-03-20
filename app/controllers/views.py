# app/controllers/views.py

from flask import Blueprint, render_template, jsonify
from app.models.list import List
from app.models.sublist import Sublist
from app.models.activity import Activity

views = Blueprint('views', __name__)

@views.route('/')
def dashboard():
    """Affiche le tableau de bord principal avec les trois colonnes."""
    return render_template('pages/dashboard.html')

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
        'components/list_item.html', 
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

@views.route('/settings')
def settings():
    """Affiche la page des paramètres."""
    return render_template('pages/settings.html')