# Create venv:
 python -m venv .env
 or:
 python3 -m venv .env


# Active venv:
source ./.env/bin/activate

# install 
pip install django djangorestframework django-cors-headers requests

or: 


pip install -r requirements.txt


# run our program:
python manage.py runserver
or:
python3 manage.py runserver
 



# linux
Redis	redis-server (if not already running)
Django backend	python manage.py runserver
Celery worker	celery -A api worker --loglevel=info
Celery beat (periodic)	celery -A api beat --loglevel=info
