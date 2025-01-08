import os
import redis

from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask_migrate import Migrate
# from flask_caching.backends import RedisCache
from flask_caching import Cache
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_modals import Modal
from flask_talisman import Talisman
from flask_wtf import CSRFProtect
from config import config
from urllib.parse import urlparse

url = urlparse(os.environ.get("REDIS_URL"))
r = redis.Redis(host=url.hostname, port=url.port, password=url.password, ssl=(url.scheme == "rediss"), ssl_cert_reqs=None)
print(r.ping())
bootstrap = Bootstrap5()
modal = Modal()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
cache = Cache()
"""
previous config arg for Cache() instance
config={
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL'),
    'CACHE_REDIS_TLS': True,
    'CACHE_OPTIONS':{"ssl_certs_reqs": None}}
"""
cache._cache = r

migrate = Migrate()
oauth = OAuth()
csrf = CSRFProtect()

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
    csrf.init_app(app)

    from iGame.models import db
    db.init_app(app)
    migrate.init_app(app, db)

    from .main import main as main_bp
    from .auth import auth as auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    if app.config['SSL_REDIRECT']:
        Talisman(app, content_security_policy=None)
    print(type(app))
    return app
