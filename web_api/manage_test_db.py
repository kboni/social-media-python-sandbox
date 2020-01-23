from flask_init import app, db
import models

def test_db_init():
    # TODO: Populate db for integration testing
    user = models.User()
    user.username = 'test_username'

    db.session.add(user)
    db.session.commit()


if __name__ == '__main__':
    test_db_init()
