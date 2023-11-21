from flask import Flask
from flask_migrate import Migrate
from flask_caching import Cache
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_modals import Modal
from config import config

bootstrap = Bootstrap5()
modal = Modal()
login_manager = LoginManager()
login_manager.login_view = 'main.index'
cache = Cache(config={'CACHE_TYPE': 'RedisCache'})
migrate = Migrate()

def create_app(config_name):
    # create and configure the app
    app = Flask('igame', template_folder='iGame/templates')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    login_manager.init_app(app)
    modal.init_app(app)
    cache.init_app(app)

    from iGame.models import db
    db.init_app(app)
    migrate.init_app(app, db)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    return app
