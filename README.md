# Backend Project for Kanban-App with Django REST Framework (DRF)

Dieses Projekt ist das **Backend** für die KanMind Webanwendung – ein einfaches, aber funktionsreiches Kanban-Board-System.  
Es basiert auf **Django** und dem **Django REST Framework** und bietet API-Endpunkte für Benutzerregistrierung, Login, Board- und Task-Verwaltung.

---

## Features

- Benutzerregistrierung und Login (Token-Authentifizierung)
- Boards erstellen, bearbeiten, löschen
- Mitglieder zu Boards hinzufügen
- Tasks erstellen, bearbeiten, löschen
- Aufgaben mit Assignee & Reviewer
- Aufgaben nach Status und Priorität filtern
- Kommentare zu Tasks hinzufügen/löschen

---

## Technologie-Stack

- [Django](https://www.djangoproject.com/) 5.x
- [Django REST Framework](https://www.django-rest-framework.org/)
- SQLite (Standard, leicht austauschbar gegen PostgreSQL/MySQL)
- Token Authentication

---

## Installation

### 1. Repository klonen
```bash
https://github.com/Ozinho78/KanMindBackend
cd KanMindBackend


2. Virtuelle Umgebung erstellen & aktivieren
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate


3. Abhängigkeiten installieren
pip install -r requirements.txt


4. Datenbankmigrationen ausführen
python manage.py migrate


5. Superuser anlegen (optional)
python manage.py createsuperuser


6. Server starten
python manage.py runserver