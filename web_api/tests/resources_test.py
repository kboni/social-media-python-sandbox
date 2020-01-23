import io
import json
import flask_init
import models
import resources
import utils


class TestUser():
    def setup(self):
        self.user = models.User(
            id = 1,
            email = 'test@email.com',
            username = 'test_username',
            first_name = 'Jimmy',
            last_name = 'Jensson',
            birthday = '1991-05-05',
            profile_image = 'img1.jpg',
            created = '2020-01-01')
        self.user.hash_password('test_password')

        self.app = flask_init.app.test_client()
        self.app.testing = True

    def test_get_OK(self, mocker):
        # GIVEN
        auth_user_mock = mocker.patch.object(utils, "Auth")
        auth_user_mock.verify_authorization.return_value = self.user
        
        # WHEN
        actual_response = self.app.get('/user')
        actual_response_dict = json.loads(actual_response.data.decode("utf-8"))

        # THEN
        auth_user_mock.verify_authorization.assert_called_once_with(request=mocker.ANY)

        assert actual_response.status_code == 200
        assert actual_response_dict.get('message') == 'Success'
        assert 'user' in actual_response_dict

    def test_patch_change_password_OK(self, mocker):
        # GIVEN
        auth_user_mock = mocker.patch.object(utils, "Auth")
        auth_user_mock.verify_authorization.return_value = self.user
        
        db_session_mock = mocker.patch.object(flask_init.db, "session")
        db_session_mock.commit.return_value = None
        
        # WHEN
        actual_response = self.app.patch(
            '/user',
            json={
                'old_password': 'test_password',
                'new_password': 'new_test_password'
            })
        actual_response_dict = json.loads(actual_response.data.decode("utf-8"))

        # THEN
        auth_user_mock.verify_authorization.assert_called_once_with(request=mocker.ANY)

        assert actual_response.status_code == 200
        assert actual_response_dict.get('username') == 'test_username'
        assert not self.user.verify_password('test_password')
        assert self.user.verify_password('new_test_password')

    def test_patch_update_OK(self, mocker):
        # GIVEN
        auth_user_mock = mocker.patch.object(utils, "Auth")
        auth_user_mock.verify_authorization.return_value = self.user
        
        file_upload_mock = mocker.patch.object(utils, "File")
        file_upload_mock.upload.return_value = True

        db_session_mock = mocker.patch.object(flask_init.db, "session")
        db_session_mock.commit.return_value = None
        
        request_form_mock = {
            'id': 15,
            'email': 'new_test@email.com',
            'username': 'new_test_username',
            'password_hash': 'new_password_that_shouldnt_be_set',
            'first_name': 'Jimmy Junior',
            'last_name': 'Ben-Jensson',
            'birthday': '1988-11-15',
            'profile_image': 'new_img1.jpg',
            'created': '1977-01-02',
            'file': (io.BytesIO(b"abcdef"), 'new_img1.jpg')
        }

        # WHEN
        actual_response = self.app.patch(
            '/user',
            data=request_form_mock,
            content_type='multipart/form-data')
        actual_response_dict = json.loads(actual_response.data.decode("utf-8"))

        # THEN
        auth_user_mock.verify_authorization.assert_called_once_with(request=mocker.ANY)
        file_upload_mock.upload.assert_called_once()

        assert actual_response.status_code == 200

        # Not changed
        assert actual_response_dict.get('email') == self.user.email
        assert actual_response_dict.get('email') != request_form_mock['email']
        assert actual_response_dict.get('created') == utils.DateTimeUtil.format(self.user.created)
        assert actual_response_dict.get('created') != utils.DateTimeUtil.format(request_form_mock['created'])
        assert not self.user.verify_password(request_form_mock['password_hash'])
        assert self.user.verify_password('test_password')
        # Changed
        assert actual_response_dict.get('username') == request_form_mock['username']
        assert actual_response_dict.get('first_name') == request_form_mock['first_name']
        assert actual_response_dict.get('last_name') == request_form_mock['last_name']
        assert actual_response_dict.get('birthday') == request_form_mock['birthday']
        assert actual_response_dict.get('profile_image') == \
            flask_init.app.config['MEDIA_BASE_URL'].format(
                file_name=request_form_mock['profile_image'])

    def test_delete_OK(self, mocker):
        # GIVEN
        auth_user_mock = mocker.patch.object(utils, "Auth")
        auth_user_mock.verify_authorization.return_value = self.user
        
        db_session_mock = mocker.patch.object(flask_init.db, "session")
        db_session_mock.delete.return_value = None
        db_session_mock.commit.return_value = None
        
        # WHEN
        actual_response = self.app.delete('/user')
        actual_response_dict = json.loads(actual_response.data.decode("utf-8"))

        # THEN
        auth_user_mock.verify_authorization.assert_called_once_with(request=mocker.ANY)

        assert actual_response.status_code == 200
        assert 'message' in actual_response_dict

class TestPost():
    def setup(self):
        self.user = models.User(
            id = 1,
            email = 'test@email.com',
            username = 'test_username',
            first_name = 'Jimmy',
            last_name = 'Jensson',
            birthday = '1991-05-05',
            profile_image = 'img1.jpg',
            created = '2020-01-01')
        self.user.hash_password('test_password')

        self.data = models.Post(
            id = 1,
            user_id = 1,
            resource = 'test_image.jpg',
            description = 'Test image',
            created = '2020-02-11'
        )
        self.data.user = self.user

        self.app = flask_init.app.test_client()
        self.app.testing = True

    def test_get_all_OK(self, mocker):
        # GIVEN
        auth_user_mock = mocker.patch.object(utils, "Auth")
        auth_user_mock.verify_authorization.return_value = self.user
        
        data_mock = mocker.patch.object(models, "Post")
        data_mock.query.join.return_value.all.return_value = [self.data]

        # WHEN
        actual_response = self.app.get('/post/all')
        actual_response_dict = json.loads(actual_response.data.decode("utf-8"))

        # THEN
        auth_user_mock.verify_authorization.assert_called_once_with(request=mocker.ANY)
        data_mock.query.join.return_value.all.assert_called_once_with()

        assert actual_response.status_code == 200
        assert actual_response_dict['message'] == 'Success'
        assert 'post' in actual_response_dict
        assert type(actual_response_dict['data']) == list
        assert 'user' in actual_response_dict['data'][0]
        assert 'comments' in actual_response_dict['data'][0]

    def test_get_single_data_by_id_OK(self, mocker):
        # GIVEN
        auth_user_mock = mocker.patch.object(utils, "Auth")
        auth_user_mock.verify_authorization.return_value = self.user
        
        data_mock = mocker.patch.object(models, "Post")
        data_mock.query.filter_by.return_value.first.return_value = self.data

        # WHEN
        actual_response = self.app.get('/post/1')
        actual_response_dict = json.loads(actual_response.data.decode("utf-8"))

        # THEN
        auth_user_mock.verify_authorization.assert_called_once_with(request=mocker.ANY)
        data_mock.query.filter_by.return_value.first.assert_called_once_with()

        assert actual_response.status_code == 200
        assert actual_response_dict['message'] == 'Success'
        assert 'post' in actual_response_dict
        assert isinstance(actual_response_dict['post'], (dict, models.Post))

    def test_get_single_data_by_user_id_OK(self, mocker):
        # GIVEN
        auth_user_mock = mocker.patch.object(utils, "Auth")
        auth_user_mock.verify_authorization.return_value = self.user
        
        data_mock = mocker.patch.object(models, "Post")
        data_mock.query.filter_by.return_value.all.return_value = [self.data]

        # WHEN
        actual_response = self.app.get('/post/user/1')
        actual_response_dict = json.loads(actual_response.data.decode("utf-8"))

        # THEN
        auth_user_mock.verify_authorization.assert_called_once_with(request=mocker.ANY)
        data_mock.query.filter_by.return_value.all.assert_called_once_with()

        assert actual_response.status_code == 200
        assert actual_response_dict['message'] == 'Success'
        assert 'post' in actual_response_dict
        assert type(actual_response_dict['post']) == list
        assert 'user' in actual_response_dict['post'][0]
        assert 'comments' in actual_response_dict['post'][0]

    def test_get_single_data_by_user_username_OK(self, mocker):
        # GIVEN
        auth_user_mock = mocker.patch.object(utils, "Auth")
        auth_user_mock.verify_authorization.return_value = self.user
        
        user_mock = mocker.patch.object(models, "User")
        user_mock.query.filter_by.return_value.first.return_value = self.user
        
        data_mock = mocker.patch.object(models, "Post")
        data_mock.query.filter_by.return_value.all.return_value = [self.data]

        # WHEN
        actual_response = self.app.get('/post/user/username/test_username')
        actual_response_dict = json.loads(actual_response.data.decode("utf-8"))

        # THEN
        auth_user_mock.verify_authorization.assert_called_once_with(request=mocker.ANY)
        user_mock.query.filter_by.return_value.first.assert_called_once_with()
        data_mock.query.filter_by.return_value.all.assert_called_once_with()

        assert actual_response.status_code == 200
        assert actual_response_dict['message'] == 'Success'
        assert 'post' in actual_response_dict
        assert type(actual_response_dict['post']) == list
        assert 'post' in actual_response_dict['post'][0]
        assert 'comments' in actual_response_dict['post'][0]

    def test_post_OK(self, mocker):
        # GIVEN
        auth_user_mock = mocker.patch.object(utils, "Auth")
        auth_user_mock.verify_authorization.return_value = self.user

        file_upload_mock = mocker.patch.object(utils, "File")
        file_upload_mock.upload.return_value = True

        db_session_mock = mocker.patch.object(flask_init.db, "session")
        db_session_mock.add.return_value = None
        db_session_mock.commit.return_value = None

        request_form_mock = {
            'id': 1,
            'user_id': 6,
            'resource': 'new_test_image.jpg',
            'description': 'New test image',
            'created': '2020-02-15',
            'file': (io.BytesIO(b"abcdef"), 'new_test_image.jpg')
        }

        # WHEN
        actual_response = self.app.post(
            '/post',
            data=request_form_mock,
            content_type='multipart/form-data')
        actual_response_dict = json.loads(actual_response.data.decode("utf-8"))

        # THEN
        auth_user_mock.verify_authorization.assert_called_once_with(request=mocker.ANY)
        file_upload_mock.upload.assert_called_once()

        assert actual_response.status_code == 201
        assert 'message' in actual_response_dict
        assert 'post' in actual_response_dict

        assert actual_response_dict['post']['created'] == None
        assert actual_response_dict['post']['description'] == request_form_mock['description']
        assert actual_response_dict['post']['resource'] == \
            flask_init.app.config['MEDIA_BASE_URL'].format(
                file_name=request_form_mock['resource'])

    def test_patch_OK(self, mocker):
        # GIVEN
        auth_user_mock = mocker.patch.object(utils, "Auth")
        auth_user_mock.verify_authorization.return_value = self.user

        file_upload_mock = mocker.patch.object(utils, "File")
        file_upload_mock.upload.return_value = True

        data_mock = mocker.patch.object(models, "Post")
        data_mock.query.filter_by.return_value.first.return_value = self.data

        db_session_mock = mocker.patch.object(flask_init.db, "session")
        db_session_mock.commit.return_value = None

        request_form_mock = {
            'id': 1,
            'user_id': 6,
            'resource': 'new_test_image.jpg',
            'description': 'New test image',
            'created': '2020-02-15',
            'file': (io.BytesIO(b"abcdef"), 'new_test_image.jpg')
        }

        # WHEN
        actual_response = self.app.patch(
            '/post/1',
            data=request_form_mock,
            content_type='multipart/form-data')
        actual_response_dict = json.loads(actual_response.data.decode("utf-8"))

        # THEN
        auth_user_mock.verify_authorization.assert_called_once_with(request=mocker.ANY)
        file_upload_mock.upload.assert_called_once()

        assert actual_response.status_code == 200
        assert 'message' in actual_response_dict
        assert 'post' in actual_response_dict
        # Not changed
        assert actual_response_dict['post']['created'] == self.data.created
        assert actual_response_dict['post']['created'] != request_form_mock['created']
        # Changed
        assert actual_response_dict['post']['description'] == request_form_mock['description']
        assert actual_response_dict['post']['resource'] == \
            flask_init.app.config['MEDIA_BASE_URL'].format(
                file_name=request_form_mock['resource'])

    def test_delete_OK(self, mocker):
        # GIVEN
        auth_user_mock = mocker.patch.object(utils, "Auth")
        auth_user_mock.verify_authorization.return_value = self.user
        
        db_session_mock = mocker.patch.object(flask_init.db, "session")
        db_session_mock.delete.return_value = None
        db_session_mock.commit.return_value = None

        data_mock = mocker.patch.object(models, "Post")
        data_mock.query.filter_by.return_value.first.return_value = self.data
        
        # WHEN
        actual_response = self.app.delete('/post/1')
        actual_response_dict = json.loads(actual_response.data.decode("utf-8"))

        # THEN
        auth_user_mock.verify_authorization.assert_called_once_with(request=mocker.ANY)

        assert actual_response.status_code == 200
        assert 'message' in actual_response_dict


class TestComment():
    def setup(self):
        self.user = models.User(id = 1, username = 'test_username')
        
        self.post = models.Post(id = 1, user_id = 1)
        self.post.user = self.user
        
        self.comment = models.Comment(
            post_id = 1,
            user_id = 1,
            text = 'Test text',
            created = '2020-01-02',
        )

        self.subcomment = models.SubComment(
            comment_id = 1,
            user_id = 1,
            text = 'Test text',
            created = '2020-01-02'
        )
        self.subcomment.user = self.user

        self.comment.user = self.user
        self.comment.post = self.post
        self.comment.subcomments = [self.subcomment]

        self.app = flask_init.app.test_client()
        self.app.testing = True

    def test_post_OK(self, mocker):
        auth_user_mock = mocker.patch.object(utils, "Auth")
        auth_user_mock.verify_authorization.return_value = self.user

        data_mock = mocker.patch.object(models, "Post")
        data_mock.query.filter_by.return_value.first.return_value = self.post

        db_session_mock = mocker.patch.object(flask_init.db, "session")
        db_session_mock.add.return_value = None
        db_session_mock.commit.return_value = None

        request_form_mock = {
            'text': 'New test text',
        }

        # WHEN
        actual_response = self.app.post(
            '/post/1/comment',
            data=request_form_mock,
            content_type='multipart/form-data')
        actual_response_dict = json.loads(actual_response.data.decode("utf-8"))

        # THEN
        auth_user_mock.verify_authorization.assert_called_once_with(request=mocker.ANY)
        data_mock.query.filter_by.return_value.first.assert_called_once_with()

        assert actual_response.status_code == 201
        assert 'message' in actual_response_dict
        assert 'comment' in actual_response_dict

        assert actual_response_dict['comment']['created'] == None
        assert actual_response_dict['comment']['text'] == request_form_mock['text']

    def test_delete_OK(self, mocker):
        # GIVEN
        auth_user_mock = mocker.patch.object(utils, "Auth")
        auth_user_mock.verify_authorization.return_value = self.user
        
        db_session_mock = mocker.patch.object(flask_init.db, "session")
        db_session_mock.delete.return_value = None
        db_session_mock.commit.return_value = None

        comment_mock = mocker.patch.object(models, "Comment")
        comment_mock.query.filter_by.return_value.first.return_value = self.comment
        
        # WHEN
        actual_response = self.app.delete('/post/comment/1')
        actual_response_dict = json.loads(actual_response.data.decode("utf-8"))

        # THEN
        auth_user_mock.verify_authorization.assert_called_once_with(request=mocker.ANY)

        assert actual_response.status_code == 200
        assert 'message' in actual_response_dict


class TestSubComment():
    def setup(self):
        self.user = models.User(id = 1, username = 'test_username')
        
        self.post = models.Post(id = 1, user_id = 1)
        self.post.user = self.user
        
        self.comment = models.Comment(
            post_id = 1,
            user_id = 1,
            text = 'Test text',
            created = '2020-01-02',
        )

        self.subcomment = models.SubComment(
            comment_id = 1,
            user_id = 1,
            text = 'Test text',
            created = '2020-01-02'
        )
        self.subcomment.user = self.user

        self.comment.user = self.user
        self.comment.post = self.post
        self.comment.subcomments = [self.subcomment]

        self.app = flask_init.app.test_client()
        self.app.testing = True

    def test_post_OK(self, mocker):
        auth_user_mock = mocker.patch.object(utils, "Auth")
        auth_user_mock.verify_authorization.return_value = self.user

        comment_mock = mocker.patch.object(models, "Comment")
        comment_mock.query.filter_by.return_value.first.return_value = self.comment

        db_session_mock = mocker.patch.object(flask_init.db, "session")
        db_session_mock.add.return_value = None
        db_session_mock.commit.return_value = None

        request_form_mock = {
            'text': 'New test text',
        }

        # WHEN
        actual_response = self.app.post(
            '/post/comment/1/subcomment',
            data=request_form_mock,
            content_type='multipart/form-data')
        actual_response_dict = json.loads(actual_response.data.decode("utf-8"))

        # THEN
        auth_user_mock.verify_authorization.assert_called_once_with(request=mocker.ANY)
        comment_mock.query.filter_by.return_value.first.assert_called_once_with()

        assert actual_response.status_code == 201
        assert 'message' in actual_response_dict
        assert 'subcomment' in actual_response_dict

        assert actual_response_dict['subcomment']['created'] == None
        assert actual_response_dict['subcomment']['text'] == request_form_mock['text']

    def test_delete_OK(self, mocker):
        # GIVEN
        auth_user_mock = mocker.patch.object(utils, "Auth")
        auth_user_mock.verify_authorization.return_value = self.user
        
        db_session_mock = mocker.patch.object(flask_init.db, "session")
        db_session_mock.delete.return_value = None
        db_session_mock.commit.return_value = None

        subcomment_mock = mocker.patch.object(models, "SubComment")
        subcomment_mock.query.filter_by.return_value.first.return_value = self.subcomment
        
        # WHEN
        actual_response = self.app.delete('/post/comment/subcomment/1')
        actual_response_dict = json.loads(actual_response.data.decode("utf-8"))

        # THEN
        auth_user_mock.verify_authorization.assert_called_once_with(request=mocker.ANY)

        assert actual_response.status_code == 200
        assert 'message' in actual_response_dict