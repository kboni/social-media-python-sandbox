from flask import abort, request, jsonify, url_for, make_response
from flask_restful import Resource
from flask_init import app, api, db, basic_auth
import auth
import models
import utils


class Register(Resource):
    def post(self):
        email = request.json.get('email')
        registration_code = request.json.get('registration_code')

        token = request.json.get('token')
        username = request.json.get('username')
        password = request.json.get('password')

        if email and registration_code:
            response_message, response_code = \
                Register.second_step_registration(
                    email=email, registration_code=registration_code)
            return make_response(response_message, response_code)

        if email:
            response_message, response_code = Register.first_step_registration(
                email=email)
            return make_response(response_message, response_code)

        if token and username and password:
            response_message, response_code = Register.third_step_registration(
                token=token, username=username, password=password)
            return make_response(response_message, response_code)

        abort(400)  # missing arguments

    @staticmethod
    def first_step_registration(email):
        registration_code = auth.Auth.start_registration(email)

        # Validate
        if registration_code is None:
            abort(400)  # generation failed

        # compose e-mail
        email_message = utils.Mail.build_message(
            subject=app.config['REGISTRATION_MAIL_SUBJECT'],
            message_content=app.config['REGISTRATION_MAIL_CONTENT'].format(
                registration_code=registration_code
            ),
            send_to=email
        )

        # send e-mail
        is_email_sent = utils.Mail.send(message=email_message)

        if is_email_sent:
            return jsonify({'message': 'E-mail successfully sent'}), 201
        else:
            return jsonify({'message': 'Error while sending e-mail'}), 500

    @staticmethod
    def second_step_registration(email: str, registration_code: str):
        # Validate input
        if not email or not registration_code:
            app.logger.warning('Missing request JSON argument')
            abort(400)  # missing arguments

        token = auth.Auth.cont_registration(email, registration_code)

        if token is None:
            abort(400)  # mail not found

        return jsonify({'token': token.decode('ascii')}), 200

    @staticmethod
    def third_step_registration(token: str, username: str, password: str):
        user = auth.Auth.end_registration(token, username, password)

        if user is None:
            app.logger.error('User to be registered is None')
            return jsonify(
                {'message': f'User couldn\'t be registered!'}
            ), 400

        # Save user
        db.session.add(user)
        db.session.commit()

        return jsonify(
                {'message': f'User {user.username} successfully registered!'}
            ), 201


class Login(Resource):
    @basic_auth.login_required
    def get(self):
        username = basic_auth.username()
        user = models.User.query.filter_by(username=username).first()

        refresh_token = auth.Auth.generate_refresh_token(user) \
            .decode('ascii')

        access_token = auth.Auth.generate_access_token(refresh_token) \
            .decode('ascii')

        return make_response(
            jsonify({
                'message': f'User {user.username} successfully logged in!',
                'refresh_token': refresh_token,
                'access_token': access_token
            }),
            200)


class Token(Resource):
    def get(self):
        refresh_token = request.headers.get('Authorization')

        access_token = auth.Auth.generate_access_token(refresh_token)

        if access_token is None:
            abort(400)

        access_token = access_token.decode('ascii')

        return make_response(
            jsonify({
                'message': 'Access token succesfully refreshed!',
                'access_token': access_token
            }),
            200)


class Password(Resource):
    def patch(self):
        email = request.json.get('email')
        registration_code = request.json.get('registration_code')

        token = request.json.get('token')
        username = request.json.get('username')
        password = request.json.get('password')

        if email and registration_code:
            response_message, response_code = Password.second_step_recovery(
                    email=email, registration_code=registration_code)
            return make_response(response_message, response_code)

        if email:
            response_message, response_code = Password.first_step_recovery(
                email=email)
            return make_response(response_message, response_code)

        if token and username and password:
            response_message, response_code = Password.third_step_recovery(
                token=token, username=username, password=password)
            return make_response(response_message, response_code)

        abort(400)  # missing arguments

    @staticmethod
    def first_step_recovery(email):
        confirmation_code = auth.Auth.start_password_recovery(email)

        # Validate
        if confirmation_code is None:
            abort(400)  # generation failed

        # compose e-mail
        email_message = utils.Mail.build_message(
            subject=app.config['PASSWORD_RECOVERY_MAIL_SUBJECT'],
            message_content=app.config['PASSWORD_RECOVERY_MAIL_CONTENT']
            .format(confirmation_code=confirmation_code),
            send_to=email
        )

        # send e-mail
        is_email_sent = utils.Mail.send(message=email_message)

        if is_email_sent:
            return jsonify({'message': 'E-mail successfully sent'}), 200
        else:
            return jsonify({'message': 'Error while sending e-mail'}), 500

    @staticmethod
    def second_step_recovery(email: str, registration_code: str):
        # Validate input
        if not email or not registration_code:
            app.logger.warning('Missing request JSON argument')
            abort(400)  # missing arguments

        token = auth.Auth.cont_password_recovery(email, registration_code)

        if token is None:
            abort(400)  # mail not found

        return jsonify({'token': token.decode('ascii')}), 200

    @staticmethod
    def third_step_recovery(token: str, username: str, password: str):
        user = auth.Auth.end_password_recovery(token, username, password)

        if user is None:
            app.logger.error('User is None')
            return jsonify(
                {'message': f'User\'s password couldn\'t be recovered!'}
            ), 400

        # Save user
        db.session.commit()

        return jsonify(
                {'message': f'User {user.username} successfully registered!'}
            ), 200

api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Token, '/token')
api.add_resource(Password, '/recover_password')
