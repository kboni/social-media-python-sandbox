import flask
import utils
import models
import sqlalchemy


class TestAuth():
    def test_verify_authorization_OK(self, mocker):
        # GIVEN
        expected = models.User()
        expected.user_id = 1

        request_mock = mocker.patch.object(flask, "request")
        request_mock.headers.get.return_value = 'token'

        auth_payload_mock = mocker.patch.object(
            models.User, "verify_auth_token")
        auth_payload_mock.verify_auth_token.return_value = {'user_id': 1}
        
        query_mock = mocker.patch.object(sqlalchemy.orm.query, "Query")
        query_mock.first.return_value = expected
        
        user_mock = mocker.patch.object(models, "User")
        user_mock.query.filter_by.return_value = query_mock

        # WHEN
        actual = utils.Auth.verify_authorization(request_mock)

        # THEN
        request_mock.headers.get.assert_called_once_with('Authorization')
        
        assert actual == expected

        