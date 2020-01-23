from sqlalchemy.sql import func
from passlib.apps import custom_app_context as pwd_context
from flask_init import app, db, basic_auth


class User(db.Model):
    __tablename__ = 'USER'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    email = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(250))
    creation_date = db.Column(db.DateTime(timezone=True), default=func.now())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def hash_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.password_hash)
