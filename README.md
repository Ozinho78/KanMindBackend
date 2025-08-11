# Backend Project for Kanban-App with Django REST Framework (DRF)

This project is the backend for a Kanban-App, built with Django and Django REST Framework (DRF).
It offers endpoints for creating, reading, updating and deleting (CRUD) boards, lists, cards and comments.

-------------------------------------------------------------------------------------------------------------

## Features

- User authentication and authorization, using Django's built-in authentication system.
- Board creation, reading, updating and deletion.
- Adding members to a board.
- Task creation, reading, updating and deletion.
- Tasks contain assignee and reviewer.
- Filtering and sorting of tasks by assignee, reviewer, status and priority.
- Adding comments to tasks.

-------------------------------------------------------------------------------------------------------------

## Technology Stack

- [Django](https://www.djangoproject.com/) 5.x
- [Django REST Framework](https://www.django-rest-framework.org/)
- SQLite as the database.
- Token Authentication

-------------------------------------------------------------------------------------------------------------

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/Ozinho78/KanMindBackend
cd KanMindBackend
```


### 2. Create a virtual environment
```bash
python -m venv venv
```
###### Windows:
```bash
venv\Scripts\activate
```
###### macOS/Linux:
```bash
source venv/bin/activate
```


### 3. Install dependencies
```bash
pip install -r requirements.txt
```


### 4. Run database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```


### 5. Creating a superuser
```bash
python manage.py createsuperuser
```


### 6. Run the server
``` bash
python manage.py runserver
```