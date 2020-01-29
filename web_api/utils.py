import datetime
import requests
import werkzeug
import models


class File():

    @staticmethod
    def upload(file: werkzeug.datastructures.FileStorage, filename: str):
        files = {
            'file': (filename, file.read(), file.content_type)
        }
        url = (
            'http://static-file-server:25478/'
            'upload?token=f9403fc5f537b4ab332d'
        )
        return requests.post(url, files=files)


class Auth():
    @staticmethod
    def verify_authorization(request):
        auth_header = request.headers.get('Authorization')

        if auth_header is None:
            return None

        auth_payload = models.User.verify_auth_token(auth_header)

        if not auth_payload or not auth_payload.get('user_id'):
            return None

        return models.User.query.filter_by(
            id=auth_payload['user_id']).first()

class DateTimeUtil():
    @staticmethod
    def format(input_datetime: str,
            input_format='%Y-%m-%d',
            output_format='%Y-%m-%d %H:%M:%S.%f'):
        return datetime.datetime.strptime(input_datetime, input_format) \
            .strftime(output_format)
