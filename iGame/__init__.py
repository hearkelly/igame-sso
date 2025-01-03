import os

from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask_migrate import Migrate
from flask_caching import Cache
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_modals import Modal
from flask_talisman import Talisman

from config import config

bootstrap = Bootstrap5()
modal = Modal()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
cache = Cache(config={'CACHE_TYPE': 'RedisCache', 'CACHE_REDIS_URL': os.environ.get('REDIS_URL')})
migrate = Migrate()
oauth = OAuth()

def create_app(config_name: str):
    # create and configure the app
    app = Flask('igame', template_folder='iGame/templates')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    modal.init_app(app)
    cache.init_app(app)
    oauth.init_app(app)
    print(type(app))
    from iGame.models import db
    db.init_app(app)
    migrate.init_app(app, db)

    from .main import main as main_bp
    print(type(main_bp))
    try:
        from .auth import auth as auth_bp
    except Exception as e:
        print(e)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    if app.config['SSL_REDIRECT']:
        Talisman(app, content_security_policy=None)
    print(type(app))
    return app
