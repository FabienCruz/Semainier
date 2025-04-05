# Logique d'affichage des listes et activités

## Principes fondamentaux

### Passage de paramètres standardisé

- Utilisation de la directive {% with %} pour passer des paramètres
- Noms de variables cohérents avec le dictionnaire de données
- Documentation claire des paramètres attendus et fournis

### Concept de "sous-liste virtuelle par défaut"

- Les activités sans sous-liste sont regroupées dans une sous-liste virtuelle
- L'en-tête de la sous-liste virtuelle reste invisible
- Les activités s'affichent directement sous la liste parente

## Structure des Composants

### 1. list_column.html
**Rôle**: Conteneur principal affichant la colonne des listes.  
**Paramètres**: Aucun (composant racine)  
**Responsabilités**:
- Afficher l'en-tête de colonne avec titre et boutons d'action
- Charger dynamiquement le contenu des listes via HTMX
- Gérer l'état d'expansion/réduction de la colonne entière
- Intégrer le menu contextuel d'ajout (liste, sous-liste, activité)

### 2. lists.html
**Rôle**: Afficher toutes les listes disponibles.  
**Paramètres**: lists (collection des objets Liste)  
**Responsabilités**:
- Itérer sur la collection des listes
- Afficher chaque liste avec sa couleur personnalisée
- Gérer l'état d'ouverture/fermeture des listes (via Alpine.js)
- Intégrer les menus contextuels pour chaque liste
- Charger dynamiquement le contenu d'une liste (via HTMX)
- Afficher un état vide avec appel à l'action si aucune liste n'existe

### 3. list_content.html
**Rôle**: Afficher le contenu d'une liste spécifique.  
**Paramètres**: 
- list_item: La liste à afficher
- sublists: Les sous-listes associées
- activities: Les activités directement attachées à la liste (sans sous-liste)  
**Responsabilités**:
- Afficher les activités sans sous-liste en premier
- Organiser et afficher les sous-listes avec leurs en-têtes
- Gérer l'état d'ouverture/fermeture de chaque sous-liste
- Inclure directement les cartes d'activité pour chaque activité
- Maintenir un alignement visuel cohérent via une structure de grille

### 4. contextual_menu.html
**Rôle**: Composant réutilisable pour afficher un menu contextuel.  
**Paramètres**:
- menu_id: Identifiant unique du menu
- button_class: Classes CSS pour le bouton (optionnel)
- button_icon: Classe d'icône FontAwesome
- button_title: Texte alternatif pour l'accessibilité
- items: Liste des actions disponibles dans le menu  
**Responsabilités**:
- Afficher un bouton d'ouverture du menu
- Créer une liste déroulante avec les actions disponibles
- Gérer l'affichage/masquage du menu (via Alpine.js)
- Intégrer les attributs HTMX pour les actions dynamiques

### 5. activity_card.html
**Rôle**: Afficher une carte d'activité individuelle.  
**Paramètres**:
- activity: L'objet activité à afficher
- list_color: La couleur de la liste parente  
**Responsabilités**:
- Afficher le titre et les détails de l'activité
- Appliquer la couleur de la liste pour la bordure
- Afficher les indicateurs visuels (priorité, échéance, état, durée - SML)
- Intégrer les interactions utilisateur (double clic pour modifier, menu contextuel)

## Flux de données et interactions

1. **Chargement initial**
   - Dashboard.html inclut list_column.html
   - list_column.html charge lists.html via HTMX
   - lists.html affiche toutes les listes disponibles

2. **Ouverture d'une liste**
   - L'utilisateur ouvre une liste (ou elle s'ouvre par défaut)
   - HTMX charge list_content.html pour la liste sélectionnée
   - list_content.html structure et affiche le contenu de la liste

3. **Affichage hiérarchique**
   - Les activités sans sous-liste s'affichent directement dans la sous-liste par défaut
   - Les sous-listes s'affichent avec leurs en-têtes et actions
   - Les activités de chaque sous-liste s'affichent sous leur en-tête respectif

4. **Interactions contextuelles**
   - Chaque élément (liste, sous-liste, activité) dispose d'un menu contextuel
   - Les menus contextuels déclenchent des actions via HTMX (ajouter, modifier, supprimer)
   - Les actions ouvrent généralement des modales pour la saisie utilisateur

## Gestion des états visuels

1. **États d'ouverture/fermeture**
   - Les listes: Gérées via Alpine.js avec état persistant dans openLists[id]
   - Les sous-listes: Gérées via Alpine.js avec état isOpen local

2. **États d'activité**
   - Activité complétée: Libellé atténué et barré, fond grisé
   - Activité prioritaire: Indicateur visuel de priorité (pastille rouge)
   - Activité modèle: Indicateur visuel spécifique (pastille violette)

3. **Retours visuels**
   - Survol des éléments: Changement de couleur/ombre pour indiquer l'interactivité
   - Actions en cours: Spinners de chargement pendant les requêtes HTMX
   - États vides: Messages explicites avec appels à l'action

## Technologies utilisées

- **Alpine.js**: Gestion des états locaux et comportements interactifs
- **HTMX**: Chargement dynamique du contenu et interactions asynchrones
- **Tailwind CSS**: Styles cohérents et responsive
- **Font Awesome**: Iconographie riche et expressive
- **Flask Jinja2**: Templating côté serveur pour la composition des composants