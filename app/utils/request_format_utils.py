# app/utils/request_format_utils.py

from flask import request
from functools import wraps

def parse_request_data(f):
    """
    Décorateur qui analyse les données de la requête et les rend disponibles
    dans la fonction décorée, quel que soit le format d'envoi.
    
    Les données sont accessibles via `request.parsed_data`.
    
    Formats pris en charge:
    - application/json
    - application/x-www-form-urlencoded
    - multipart/form-data
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Initialiser un dictionnaire vide pour les données analysées
        request.parsed_data = {}
        
        # Détecter le type de contenu de la requête
        content_type = request.headers.get('Content-Type', '')
        
        # Traitement selon le type de contenu
        if request.is_json:
            # Format JSON
            request.parsed_data = request.get_json() or {}
        
        elif 'application/x-www-form-urlencoded' in content_type:
            # Format formulaire standard
            request.parsed_data = request.form.to_dict(flat=True)
        
        elif 'multipart/form-data' in content_type:
            # Format multipart (formulaires avec fichiers)
            # Récupérer les champs de formulaire standard
            request.parsed_data = request.form.to_dict(flat=True)
            
            # Ajouter une référence aux fichiers
            if request.files:
                request.parsed_files = request.files
        
        # Conversion des types pour les champs communs
        _convert_common_types(request.parsed_data)
            
        return f(*args, **kwargs)
    
    return decorated_function

def _convert_common_types(data):
    """
    Convertit les types de données courants.
    Par exemple, convertit les IDs de chaîne en entiers.
    """
    # Liste des champs qui doivent être convertis en entiers
    int_fields = ['id', 'list_id', 'sublist_id', 'position']
    
    for field in int_fields:
        if field in data and isinstance(data[field], str) and data[field].isdigit():
            data[field] = int(data[field])
    
    # Liste des champs qui doivent être convertis en booléens
    bool_fields = ['is_priority', 'is_model', 'is_completed']
    
    for field in bool_fields:
        if field in data:
            if isinstance(data[field], str):
                # Conversion des chaînes en booléens
                data[field] = data[field].lower() in ('true', 'yes', 'y', '1', 'on')
