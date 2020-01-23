import time
from typing import Union
import itsdangerous
import random
import redis
from flask_init import app, api, basic_auth
import models
from sqlalchemy import and_
import utils
import validations


class Auth():
    @staticmethod
    def start_registration(
            email: str,
            expiration: int = app.config['REDIS_REGISTRATION_KEY_EXPIRATION']):
        """
        First step of the registration process.
        Generation of the registration code.
        """
        # Validations
        if validations.Validation.is_existing_email(email):
            app.logger.info(f'E-mail {email} already exists in database!')
            return None
        if validations.Validation.is_pending_email(email):
            app.logger.info(
                f'E-mail {email} already exists in redis database!')
            return None

        registration_code = random.randint(99999, 999999)  # 6-digit code
        token_payload = {
            'email': email,
            'registration_code': registration_code
        }

        token = Auth.generate_registration_token(payload=token_payload)

        redis_db = utils.Redis.get_connection()
        redis_db.set(
            name=email,  # setting e-mail as key to make sure it's unique
            value=token,
            ex=expiration)

        return registration_code

    @staticmethod
    def cont_registration(
            email: str, registration_code: str,
            expiration: int = app.config['REDIS_REGISTRATION_KEY_EXPIRATION']):
        """
        Second step of the registration process.
        Validation of the registration code.
        """
        # Get token from redis
        redis_db = utils.Redis.get_connection()
        token_from_redis = redis_db.get(name=email)

        if token_from_redis is None:
            app.logger.error(
                'Could not retrive token from Redis for email '
                f'{email} on the second step of registration')
            return None

        payload = Auth.get_token_payload(token=token_from_redis)

        if payload is None:
            # No need for logging bc the only way for None is Exception from
            # extraction method
            return None

        # Validate token payload and reset in redis
        registration_code = payload.get('registration_code')
        if registration_code is None or registration_code != registration_code:
            app.logger.info(
                f'Missing or incorrect registration code: {registration_code}')
            return None

        # delete old tokens
        redis_db.delete(email)

        # create and set new token
        token_payload = {
            'email': email
        }

        token = Auth.generate_registration_token(payload=token_payload)
        redis_db.set(
            name=email,
            value=token,
            ex=expiration)

        return token

    @staticmethod
    def end_registration(token: str, username: str, password: str):

        # Extract payload from token
        payload = Auth.get_token_payload(token=token)

        if payload is None:
            # No need for logging bc the only way for None is Exception from
            # extraction method
            return None

        # Get email from redis
        redis_db = utils.Redis.get_connection()
        token_from_redis = redis_db.get(name=payload['email'])

        token_from_redis = token_from_redis.decode('ascii') \
            if token_from_redis is not None else None

        if token_from_redis is None or token_from_redis != token:
            app.logger.error(
                f'Token from Redis error at '
                'registration\'s 3rd step. Token: {token_from_redis}')
            return None  # entry not found or missmatch

        # Checking if username is taken
        if models.User.query.filter_by(username=username).first() is not None:
            return None

        # Delete redis entry
        redis_db.delete(payload['email'])

        # Create new User
        new_user = models.User(
            username=username,
            email=payload['email']
        )
        new_user.hash_password(password)

        return new_user

    @staticmethod
    def start_password_recovery(
            email: str,
            expiration: int = app.config['REDIS_REGISTRATION_KEY_EXPIRATION']):
        """
        First step of the password recovery process.
        Generation of the password recovery code.
        """
        # Validations
        if not validations.Validation.is_existing_email(email):
            app.logger.info(f'E-mail {email} does not exist in the database!')
            return None
        if validations.Validation.is_pending_email(email):
            app.logger.info(
                f'E-mail {email} already exists in redis database!')
            return None

        confirmation_code = random.randint(99999, 999999)  # 6-digit code
        token_payload = {
            'email': email,
            'confirmation_code': confirmation_code
        }

        token = Auth.generate_registration_token(payload=token_payload)

        redis_db = utils.Redis.get_connection()
        redis_db.set(
            name=email,  # setting e-mail as key to make sure it's unique
            value=token,
            ex=expiration)

        return confirmation_code

    @staticmethod
    def cont_password_recovery(
            email: str, confirmation_code: str,
            expiration: int = app.config['REDIS_REGISTRATION_KEY_EXPIRATION']):
        """
        Second step of the registration process.
        Validation of the registration code.
        """
        # Get token from redis
        redis_db = utils.Redis.get_connection()
        token_from_redis = redis_db.get(name=email)

        if token_from_redis is None:
            app.logger.error(
                'Could not retrive token from Redis for email '
                f'{email} on the second step of password recovery')
            return None

        payload = Auth.get_token_payload(token=token_from_redis)

        if payload is None:
            # No need for logging bc the only way for None is Exception from
            # extraction method
            return None

        # Validate token payload and reset in redis
        confirmation_code = payload.get('confirmation_code')
        if confirmation_code is None or \
                confirmation_code != confirmation_code:
            app.logger.info(
                f'Missing or incorrect confirmation code: {confirmation_code}')
            return None

        # delete old tokens
        redis_db.delete(email)

        # create and set new token
        token_payload = {
            'email': email
        }

        token = Auth.generate_registration_token(payload=token_payload)
        redis_db.set(
            name=email,
            value=token,
            ex=expiration)

        return token

    @staticmethod
    def end_password_recovery(token: str, username: str, password: str):

        # Extract payload from token
        payload = Auth.get_token_payload(token=token)

        if payload is None:
            # No need for logging bc the only way for None is Exception from
            # extraction method
            return None

        # Get email from redis
        redis_db = utils.Redis.get_connection()
        token_from_redis = redis_db.get(name=payload['email'])

        token_from_redis = token_from_redis.decode('ascii') \
            if token_from_redis is not None else None

        if token_from_redis is None or \
                token_from_redis != token:
            app.logger.error(
                f'Token from Redis error at '
                'registration\'s 3rd step. Token: {token_from_redis}')
            return None  # entry not found or missmatch

        # Find User
        user = models.User.query.filter(
            and_(
                models.User.username == username,
                models.User.email == payload['email'])) \
            .first()

        if user is None:
            return None

        # Delete redis entry
        redis_db.delete(payload['email'])

        # Set new password
        user.hash_password(password)

        return user

    @staticmethod
    def _get_token_serializer(secret_key: str):
        return itsdangerous.JSONWebSignatureSerializer(secret_key)

    @staticmethod
    def _get_timed_token_serializer(secret_key: str, expiration: int):
        return itsdangerous.TimedJSONWebSignatureSerializer(
            secret_key, expires_in=expiration)

    @staticmethod
    def generate_registration_token(payload: Union[str, dict]) -> bytes:
        token_serializer = Auth._get_token_serializer(
            secret_key=app.config['REGISTRATION_SECRET_KEY'])
        return token_serializer.dumps(payload)

    @staticmethod
    def get_token_payload(token: str):
        token_serializer = Auth._get_token_serializer(
            secret_key=app.config['REGISTRATION_SECRET_KEY'])
        try:
            return token_serializer.loads(token)
        except itsdangerous.BadSignature:
            app.logger.error(f'Ivalid signature of the following JWS: {token}')
            return None

    @staticmethod
    def _generate_token(payload: dict, expiration: int, secret_key: str):
        token_serializer = itsdangerous.TimedJSONWebSignatureSerializer(
            secret_key, expires_in=expiration)
        # breakpoint()
        return token_serializer.dumps(payload)

    @staticmethod
    def _get_token_payload(serializer, token):
        try:
            return serializer.loads(token)
        except itsdangerous.SignatureExpired:
            app.logger.warning(
                f'Signature of the following JWS expired: {token}')
            return None
        except itsdangerous.BadSignature:
            app.logger.error(f'Ivalid signature of the following JWS: {token}')
            return None

    @staticmethod
    def generate_access_token(
            refresh_token: str,
            expiration=app.config['ACCESS_KEY_EXPIRATION']):

        refresh_token_serializer = Auth._get_timed_token_serializer(
            secret_key=app.config['TOKEN_SECRET_KEY'],
            expiration=app.config['REFRESH_KEY_EXPIRATION']
        )

        refresh_token_payload = Auth._get_token_payload(
            serializer=refresh_token_serializer, token=refresh_token)

        if refresh_token_payload is None:
            return None

        timestamp_now = int(time.time())

        access_token_payload = {
            'type': 'access_token',
            'user_id': refresh_token_payload['user_id'],
            'iat': timestamp_now,
            'exp': timestamp_now + expiration
            }

        return Auth._generate_token(
            payload=access_token_payload,
            expiration=expiration,
            secret_key=app.config['TOKEN_SECRET_KEY']
        )

    @staticmethod
    def generate_refresh_token(
            user: models.User,
            expiration=app.config['REFRESH_KEY_EXPIRATION']):

        refresh_token_payload = {
            'type': 'refresh_token',
            'user_id': user.user_id
            }

        return Auth._generate_token(
            refresh_token_payload,
            expiration,
            app.config['TOKEN_SECRET_KEY']
        )

    @staticmethod
    def verify_auth_token(token):
        serializer = itsdangerous \
            .TimedJSONWebSignatureSerializer(app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token)
        except itsdangerous.SignatureExpired:
            return None  # valid token, but expired
        except itsdangerous.BadSignature:
            return None  # invalid token
        user = models.User.query.get(data['user_id'])
        return user


@basic_auth.verify_password
def verify_password(username: str, password: str) -> bool:
    if not username or not password:
        return False

    user = models.User.query.filter_by(username=username).first()

    if not user or not user.verify_password(password):
        return False

    return True
