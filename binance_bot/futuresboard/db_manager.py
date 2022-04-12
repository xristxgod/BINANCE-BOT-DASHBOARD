
from flask import current_app
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from futuresboard.app import app
from flask_login import current_user
from flask_migrate import Migrate
from flask_mail import Mail

from addition.config import SENDER_EMAIL, SENDER_SERVER, SENDER_PASSWORD

# from addition.config import db_path

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///../DB/database.db'
# app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:mamedov00@localhost/binance'
# app.config["SQLALCHEMY_DATABASE_URI"] = db_path
app.config['SECRET_KEY'] = '324bef6c5985f7ad7c8527d2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["MAIL_SERVER"] = SENDER_SERVER
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = SENDER_EMAIL
app.config["MAIL_PASSWORD"] = SENDER_PASSWORD

mail = Mail(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


def db_setup():
    db.create_all()
    pass

def close_db(e=None):
    pass


def query(active_api_label, query, args=[], one=False):
    user_id = current_user.id
    # user_id = 2
    if query.find('WHERE') >= 0:
        query_form = query.replace('WHERE', 'WHERE api_label = "%s" AND user_id = "%d" AND').replace('?', '"%s"') % tuple([active_api_label, user_id] + args)
    else:
        query_form = (query + ' WHERE api_label = "%s" AND user_id = "%d"').replace('?', '%s') % tuple([active_api_label, user_id] + args)
    query_text = text(query_form)
    cur = db.session.execute(query_text)
    rv = cur.all()
    return (rv[0] if rv else None) if one else rv


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    db_setup()