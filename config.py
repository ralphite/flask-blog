import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'OHJWE*&@GBkHASDI823u8ehkdfi#YE0=23'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'pop.163.com'
    MAIL_PORT = 995
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'flask_blog@163.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '1qaz2wsx'
    FLASK_BLOG_MAIL_SUBJECT_PREFIX = '[Flask Blog]'
    FLASK_BLOG_MAIL_SENDER = 'Flask Blog <flask_blog@163.com>'
    FLASK_BLOG_ADMIN = os.environ.get('FLASK_BLOG_ADMIN') or 'flask_blog@163.com'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') \
        or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') \
        or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') \
        or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}