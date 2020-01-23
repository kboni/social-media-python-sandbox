from flask_init import app, api
import models
import utils


class Validation():
    @staticmethod
    def is_existing_email(email: str):
        """
        Does the e-mail already exist in the main database?
        """
        user = models.User.query.filter_by(email=email).first()
        if user is None:
            return False
        return True

    @staticmethod
    def is_existing_username(username: str):
        """
        Does the username already exist in the main database?
        """
        user = models.User.query.filter_by(username=username).first()
        if user is None:
            return False
        return True

    @staticmethod
    def is_pending_email(email: str):
        """
        Does the e-mail already exist in the redis database?
        """
        redis_db = utils.Redis.get_connection()
        redis_row = redis_db.get(email)
        if redis_row is None:
            return False
        return True
