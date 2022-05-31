from __future__ import annotations

import json
import logging
import pathlib

from flask import Flask
from flask import redirect
from flask import request
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "main.login_page"
login_manager.login_message_category = "info"

def clear_trailing():
    rp = request.path
    if rp != "/" and rp.endswith("/"):
        return redirect(rp[:-1])

def init_app(config):
    from futuresboard import db_manager
    from futuresboard import blueprint
    from futuresboard import jobs
    import futuresboard.scraper
    from futuresboard.config import Config
    if config is None:
        config = Config.from_config_dir(pathlib.Path.cwd())

    
    app.config.from_mapping(**json.loads(config.json()))
    app.url_map.strict_slashes = False
    db_manager.init_app(app)
    jobs.register_scheduler(app)
    app.before_request(clear_trailing)
    app.register_blueprint(blueprint.app)

    if config.DISABLE_AUTO_SCRAPE is False:
        futuresboard.scraper.auto_scrape(app)

    app.logger.setLevel(logging.INFO)

    return app
