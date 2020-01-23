import os


def get_env_variable(name):
        try:
            return os.environ[name]
        except KeyError:
            message = "Expected environment variable '{}' not set." \
                .format(name)
            raise Exception(message)


class BaseConfig(object):
    DEBUG = True
    TESTING = False
    ENV = get_env_variable('ENV')
    SECRET_KEY = get_env_variable('SECRET_KEY')
    SECRET_KEY_EXPIRATION = 604800  # Expiration in seconds - 1 week
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Silence the deprecation warning
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}' \
        .format(
            user=get_env_variable("POSTGRES_USER"),
            pw=get_env_variable("POSTGRES_PW"),
            url=get_env_variable("POSTGRES_DOMAIN"),
            db=get_env_variable("POSTGRES_DB"))
    MEDIA_ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'
    }


class DevConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    MEDIA_UPLOAD_FOLDER = '../static-file-server/static-files/media'
    MEDIA_BASE_URL = (
        'http://192.168.43.73:25478/files/'
        '{file_name}?token=f9403fc5f537b4ab332d'
    )

class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    MEDIA_UPLOAD_FOLDER = '../static-file-server/static-files/media'
    MEDIA_BASE_URL = (
        'http://192.168.43.73:25478/files/'
        '{file_name}?token=f9403fc5f537b4ab332d'
    )


class StageConfig(BaseConfig):
    DEBUG = False
    TESTING = False


class ProdConfig(BaseConfig):
    DEBUG = False
    TESTING = False
