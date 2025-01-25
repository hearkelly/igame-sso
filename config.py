import os
"""
https://flask.palletsprojects.com/en/stable/config/
"""
# basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SSL_REDIRECT = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql+psycopg2://')


class ProductionConfig(Config):
    DEBUG=False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql+psycopg2://')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class HerokuConfig(ProductionConfig):
    SSL_REDIRECT = True if os.environ.get('DYNO') else False

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # handle reverse proxy server headers
        try:
            from werkzeug.middleware.proxy_fix import ProxyFix
        except ImportError as e:
            print(e)
        app.wsgi_app = ProxyFix(app.wsgi_app,
                                x_for=1,
                                x_proto=1,
                                x_host=1,
                                x_port=1,
                                x_prefix=0)

        print(f"ProxyFix is applied: {isinstance(app.wsgi_app, ProxyFix)}")

        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


class DockerConfig(ProductionConfig):

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


config = {'development': DevelopmentConfig,
          'production': ProductionConfig,
          'heroku': HerokuConfig,
          'docker': DockerConfig,
          'default': DevelopmentConfig}
