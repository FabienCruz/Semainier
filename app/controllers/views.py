from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def dashboard():
    return render_template('pages/dashboard.html')

@views.route('/settings')
def settings():
    return render_template('pages/settings.html')