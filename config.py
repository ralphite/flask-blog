import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'OHW*&@GBkH8efi#YE3'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'ralph.wen@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASK_BLOG_MAIL_SUBJECT_PREFIX = '[Flask Blog]'
    FLASK_BLOG_MAIL_SENDER = 'Flask Blog <ralph.wen@gmail.com>'
    FLASK_BLOG_ADMIN = os.environ.get('FLASK_BLOG_ADMIN') or 'ralph.wen@gmail.com'
    FLASK_BLOG_POSTS_PER_PAGE = os.environ.get('FLASK_BLOG_POSTS_PER_PAGE') or 10
    USERS_PER_PAGE = os.environ.get('USERS_PER_PAGE') or 10
    COMMENTS_PER_PAGE = os.environ.get('COMMENTS_PER_PAGE') or 10
    SLOW_DB_QUERY_TIME = os.environ.get('SLOW_DB_QUERY_TIME') or 0.5
    SQLALCHEMY_RECORD_QUERIES = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') \
        or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') \
        or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') \
        or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        #email errors to the administrator
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
        if getattr(cls, 'MAIL_USER_TLS', None):
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASK_BLOG_MAIL_SENDER,
            toaddrs=[cls.FLASK_BLOG_ADMIN],
            subject=cls.FLASK_BLOG_MAIL_SUBJECT_PREFIX + 'Application Error',
            credentials=credentials,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}