export FLASK_APP=futuresboard/wsgi.py
flask db init
flask db stamp head
flask db migrate
flask db upgrade
