import copy
import models


class TestUser():
    def setup(self):
        self.user = models.User(
            user_id = 1,
            email = 'test@email.com',
            username = 'test_username',
            first_name = 'Jimmy',
            last_name = 'Jensson',
            birthday = '1991-05-05',
            profile_image = 'https://cdn-test.com/img1.jpg',
            created = '2020-01-01')
        self.user.hash_password('test_password')

    def test_new_user(self):
        test_password = 'test_password'
        user = models.User(
            id = 1,
            email = 'test@email.com',
            username = 'test_username',
            first_name = 'Jimmy',
            last_name = 'Jensson',
            birthday = '1991-05-05',
            profile_image = 'https://cdn-test.com/img1.jpg',
            created = '2020-01-01')
        user.hash_password(test_password)
        
        assert user.id == 1
        assert user.email == 'test@email.com'
        assert user.username == 'test_username'
        assert user.first_name == 'Jimmy'
        assert user.last_name == 'Jensson'
        assert user.birthday == '1991-05-05'
        assert user.profile_image == 'https://cdn-test.com/img1.jpg'
        assert user.created == '2020-01-01'
        
        assert user.password_hash != test_password
        
        assert user.verify_password(test_password)

    def test_output(self):
        # GIVEN
        expected = copy.copy(self.user).as_dict()
        del expected['id']
        del expected['password_hash']

        # WHEN
        actual = self.user.output()

        # THEN
        assert len(expected) == len(actual)
        assert 'id' not in expected
        assert 'password_hash' not in expected


    def test_expired_token(self):
        expired_token = ('eyJhbGciOiJIUzUxMiIsImlhdCI6MTU3MTQ4MDM5MywiZXhwIjox'
            'NTcxNDgwOTkzfQ.eyJ1c2VyX2lkIjo3fQ.qyERTeTkdFyY4Ib-rLhpRdXRAGF8BBM'
            'ruJ1_AhwQNYCdel7no0zIV4l1t3o9Ut46YdfPrlLO2yGNA8TgcPm8kA')
        
        assert models.User.verify_auth_token(expired_token) == None


class TestPost():
    def setup(self):
        user = models.User(
            id = 1,
            email = 'test@email.com',
            username = 'test_username',
            fist_name = 'Jimmy',
            last_name = 'Jensson',
            birthday = '1991-05-05',
            profile_image = 'https://cdn-test.com/img1.jpg',
            created = '2020-01-01')
        user.hash_password('test_password')

        self.data = models.Post()
        self.data.user_id = user.id
        self.data.user = user