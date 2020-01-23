import os


def get_env_variable(name):
        try:
            return os.environ[name]
        except KeyError:
            message = \
                "Expected environment variable '{}' not set.".format(name)
            raise Exception(message)


class BaseConfig(object):
    ENV = get_env_variable('ENV')
    SECRET_KEY = get_env_variable('SECRET_KEY')
    TOKEN_SECRET_KEY = get_env_variable('TOKEN_SECRET_KEY')
    ACCESS_KEY_EXPIRATION = 10800  # 10800 s = 3 h
    REFRESH_KEY_EXPIRATION = 2592000  # 2592000 s = 30 days
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # silence the deprecation warning
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}' \
        .format(
            user=get_env_variable("POSTGRES_USER"),
            pw=get_env_variable("POSTGRES_PW"),
            url=get_env_variable("POSTGRES_DOMAIN"),
            db=get_env_variable("POSTGRES_DB")
        )
    REGISTRATION_SECRET_KEY = get_env_variable('REGISTRATION_SECRET_KEY')
    REDIS_REGISTRATION_KEY_EXPIRATION = 1800  # 1800 s = 1/2 h
    DEFAULT_MAIL_FROM = 'no-reply@kboni.com'
    REGISTRATION_MAIL_SUBJECT = 'Registration confirmation'
    REGISTRATION_MAIL_CONTENT = \
        'Welcome! Your registration code is: {registration_code}'
    PASSWORD_RECOVERY_MAIL_SUBJECT = 'Forgotten password'
    PASSWORD_RECOVERY_MAIL_CONTENT = (
        'Welcome back! Your confirmation code is: {confirmation_code}')
    REDIS_HOST = get_env_variable("REDIS_HOST")
    REDIS_PORT = get_env_variable("REDIS_PORT")
    SMTP_HOST = get_env_variable("SMTP_HOST")
    SMTP_PORT = get_env_variable("SMTP_PORT")


class DevConfig(BaseConfig):
    DEBUG = True
    TESTING = True


class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True


class StageConfig(BaseConfig):
    DEBUG = False
    TESTING = False


class ProdConfig(BaseConfig):
    DEBUG = False
    TESTING = False
