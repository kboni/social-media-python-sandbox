import os
import json
import werkzeug
from passlib.apps import custom_app_context as pwd_context
import itsdangerous
import sqlalchemy
from flask_init import app, db
import utils


class Base(db.Model):
    __abstract__ = True

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update_attrs(self, data: dict, ignore_attrs: set) -> bool:
        changed_flag = False
        column_mapper = sqlalchemy.inspect(self)

        for column in column_mapper.attrs:
            if column.key in ignore_attrs:
                continue
            input_data = data.get(column.key)
            if input_data is not None:
                if input_data != getattr(self, column.key):
                    setattr(self, column.key, data[column.key])
                    changed_flag = True

        return changed_flag

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class User(Base):
    __tablename__ = 'USER'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(128))
    birthday = db.Column(db.Date)
    username = db.Column(db.String(32), index=True, unique=True)
    password_hash = db.Column(db.String(250))
    profile_image = db.Column(db.String(256))
    created = db.Column(
        db.DateTime(timezone=True),
        default=sqlalchemy.sql.func.now())

    post = db.relationship(
        'Post', cascade="all,delete", back_populates='user', lazy=True)
    comments = db.relationship('Comment', cascade="all,delete")
    subwcomments = db.relationship('SubComment', cascade="all,delete")

    _IGNORE_ATTRS_ON_UPDATE = {'id', 'password_hash', 'created', 'email'}
    _IGNORE_ATTRS_ON_OUTPUT = {'id', 'password_hash'}

    def output(self):
        output = self.as_dict()

        for field in self._IGNORE_ATTRS_ON_OUTPUT:
            del output[field]
        output['profile_image'] = app.config['MEDIA_BASE_URL'] \
            .format(file_name=output['profile_image'])
        return output

    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def update(self, data: dict, file: werkzeug.datastructures.FileStorage):

        self.update_attrs(data=data, ignore_attrs=self._IGNORE_ATTRS_ON_UPDATE)

        if file is not None:
            if not self._allowed_file(file.filename):
                return None
            # TODO: Create a util that generates unique (random) image names
            filename = werkzeug.utils.secure_filename(file.filename)

            response = utils.File.upload(file=file, filename=filename)
            self.profile_image = filename
            changed_flag = True

        if changed_flag is True:
            db.session.commit()

        return self

    def update_password(self, old_password: str, new_password: str):
        if not self.verify_password(old_password):
            return None

        self.hash_password(new_password)
        db.session.commit()

        return self

    @staticmethod
    def verify_auth_token(token):
        serializer = itsdangerous.TimedJSONWebSignatureSerializer(
            app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token)
        except itsdangerous.SignatureExpired:
            return None    # valid token, but expired
        except itsdangerous.BadSignature:
            return None    # invalid token

        return data

    @staticmethod
    def _allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() \
            in app.config['MEDIA_ALLOWED_EXTENSIONS']


class Post(Base):
    __tablename__ = 'POST'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('USER.id'), nullable=False)
    resource = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(500))
    created = db.Column(
        db.DateTime(timezone=True), default=sqlalchemy.sql.func.now())

    user = db.relationship('User', back_populates='post', lazy=True)
    comments = db.relationship(
        'Comment', cascade="all,delete", back_populates='post', lazy=True,
        order_by='Comment.created.desc()'
    )

    _IGNORE_ATTRS_ON_UPDATE = {'id', 'created', 'user_id'}

    def output(self):
        output = self.as_dict()
        output['resource'] = app.config['MEDIA_BASE_URL'] \
            .format(file_name=output['resource'])
        return output

    def output_with_permissions(self, auth_user: User):
        output = self.output()
        output['edit_allowed'] = True \
            if self.user_id == auth_user.id else False
        return output

    def output_with_permissions_and_users(self, auth_user: int):
        output = self.output_with_permissions(auth_user)
        output['user'] = self.user.output()
        output['comments'] = [
            comment.output_with_permissions(auth_user)
            for comment in self.comments
        ]
        return output

    def save(
            self, form_data: dict, file: werkzeug.datastructures.FileStorage,
            user: User):

        if not self._allowed_file(file.filename):
            return None

        # TODO: Create a util that generates unique (random) image names
        filename = werkzeug.utils.secure_filename(file.filename)

        response = utils.File.upload(file=file, filename=filename)

        # TODO: validate response

        self.user_id = user.id
        self.resource = filename
        self.description = form_data.get('description')

        db.session.add(self)
        db.session.commit()

        return self

    def update(
            self, form_data: dict, file: werkzeug.datastructures.FileStorage,
            user: User):
        
        self.update_attrs(
            data=form_data, ignore_attrs=self._IGNORE_ATTRS_ON_UPDATE)

        if file is not None:
            if not self._allowed_file(file.filename):
                return None
            # TODO: Create a util that generates unique (random) image names
            filename = werkzeug.utils.secure_filename(file.filename)

            response = utils.File.upload(file=file, filename=filename)
            self.resource = filename
            changed_flag = True

        if changed_flag is True:
            db.session.commit()

        return self

    @staticmethod
    def _allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() \
            in app.config['MEDIA_ALLOWED_EXTENSIONS']


class Comment(Base):
    __tablename__ = 'COMMENT'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(
        db.Integer, db.ForeignKey('POST.id'), nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey('USER.id'), nullable=False)
    text = db.Column(db.String(300), nullable=False)
    created = db.Column(
        db.DateTime(timezone=True), default=sqlalchemy.sql.func.now(),
        nullable=False)

    post = db.relationship('Post', back_populates='comments', lazy=True)
    user = db.relationship('User')
    subcomments = db.relationship(
        'SubComment', cascade="all,delete", back_populates='comments',
        lazy=True, order_by='SubComment.created.desc()')

    def output(self):
        output = self.as_dict()
        output['username'] = self.user.username
        return output

    def output_with_permissions(self, auth_user: User):
        output = self.output()
        output['subcomments'] = [
            subcomment.output_with_permissions(auth_user)
            for subcomment in self.subcomments]
        output['edit_allowed'] = True \
            if self.user_id == auth_user.id else False
        return output

    def save(self, form_data: dict, post: Post, user: User):
        self.post_id = post.id
        self.user_id = user.id
        self.text = form_data.get('text')
        self.user = user

        db.session.add(self)
        db.session.commit()

        return self


class SubComment(Base):
    __tablename__ = 'SUBCOMMENT'
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(
        db.Integer, db.ForeignKey('COMMENT.id'), nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey('USER.id'), nullable=False)
    text = db.Column(db.String(300), nullable=False)
    created = db.Column(
        db.DateTime(timezone=True), default=sqlalchemy.sql.func.now(),
        nullable=False)

    comments = db.relationship(
        'Comment', back_populates='subcomments', lazy=True)
    user = db.relationship('User')

    def output(self):
        output = self.as_dict()
        output['username'] = self.user.username
        return output

    def output_with_permissions(self, auth_user: User):
        output = self.output()
        output['edit_allowed'] = True \
            if self.user_id == auth_user.id else False
        return output
   
    def save(self, form_data: dict, comment: Comment, user: User):
        self.comment_id = comment.id
        self.user_id = user.id
        self.text = form_data.get('text')
        self.user = user

        db.session.add(self)
        db.session.commit()

        return self
