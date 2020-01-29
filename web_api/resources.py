from flask_restful import Resource
from flask import abort, request, jsonify, url_for, make_response

from flask_init import api, db
import models
import utils


class User(Resource):
    URL_RULE_USER = '/user'
    URL_RULE_USER_BY_ID = '/user/<int:user_id>'

    def get(self):
        user = utils.Auth.verify_authorization(request=request)

        if user is None:
            abort(400)

        message = {
            'message': 'Success',
            'user': user.output()
        }

        return make_response(jsonify(message), 200)

    def patch(self):
        user = utils.Auth.verify_authorization(request=request)

        if not user:
            abort(400)

        request_json = request.json

        if request_json and (
                'old_password' in request_json and
                'new_password' in request_json):
            # Update password only
            user = user.update_password(
                old_password=request_json['old_password'],
                new_password=request_json['new_password']
                )

            if user is None:
                return make_response({
                    'message': 'Incorrect old password'
                }, 400)

        else:
            user = user.update(
                data=request.form, file=request.files.get('file'))

        return make_response(user.output(), 200)

    def delete(self):
        user = utils.Auth.verify_authorization(request=request)

        if user is None:
            abort(400)

        user.delete()

        response_message = {
            'message': f'User {user.username} successfully deleted!'
        }

        return make_response(jsonify(response_message), 200)


class Post(Resource):
    URL_RULE_POST_ROOT = '/post'
    URL_RULE_ALL_POSTS = '/post/all'
    URL_RULE_SINGLE_POST_BY_ID = '/post/<int:post_id>'
    URL_RULE_POSTS_BY_USER_ID = '/post/user/<int:user_id>'
    URL_RULE_POSTS_BY_USERNAME = '/post/user/username/<string:username>'

    def get(
            self, username: str = None, user_id: int = None,
            post_id: int = None, comment_id: int = None,
            subcomment_id: int = None):

        self._auth_user = utils.Auth.verify_authorization(request=request)

        if self._auth_user is None:
            abort(400)

        if str(request.url_rule) == self.URL_RULE_ALL_POSTS:
            # TODO; Move to models
            data_list = models.Post.query.join(
                models.User, models.Post.user_id == models.User.id).all()
            return self._return_data_list(data_list)

        elif str(request.url_rule) == self.URL_RULE_SINGLE_POST_BY_ID:
            # TODO; Move to models
            data = models.Post.query.filter_by(id=post_id).first()
            return self._return_single_post(data)

        elif str(request.url_rule) == self.URL_RULE_POSTS_BY_USER_ID:
            # TODO; Move to models
            data_list = models.Post.query.filter_by(user_id=user_id).all()
            return self._return_data_list(data_list)

        elif str(request.url_rule) == self.URL_RULE_POSTS_BY_USERNAME:
            # TODO; Move to models
            user = models.User.query.filter_by(username=username).first()
            if user is None:
                abort(400)
            data_list = models.Post.query.filter_by(user_id=user.id).all()
            return self._return_data_list(data_list)

        response_message = {
            'message': 'Invalid or not existing parameter'
        }
        return make_response(jsonify(response_message), 400)

    def _return_data_list(self, post_list):
        if post_list is None:
            abort(400)

        response_message = {
            'message': 'Success',
            'post': [
                post.output_with_permissions_and_users(self._auth_user)
                for post in post_list
            ]
        }

        return make_response(jsonify(response_message), 200)

    def _return_single_post(self, post):
        if post is None:
            abort(400)

        response_message = {
            'message': 'Success',
            'post': post.output_with_permissions(self._auth_user)
        }
        return make_response(jsonify(response_message), 200)

    def post(self):
        user = utils.Auth.verify_authorization(request=request)

        if user is None:
            abort(400)

        # Check request file
        if 'file' not in request.files:
            abort(400)

        file = request.files['file']

        if not file:
            abort(400)

        if file.filename == '':
            abort(400)

        # Check form data
        form_data = request.form

        if not form_data:
            abort(400)

        post = models.Post()
        post = post.save(form_data=form_data, file=file, user=user)

        if post is None:
            abort(400)

        response_message = {
            'message': f'New post successfuly created!',
            'post': post.output()
        }

        return make_response(jsonify(response_message), 201)

    def patch(self, post_id: int):
        # TODO: Test wether is this check necessary or not
        if str(request.url_rule) != self.URL_RULE_SINGLE_POST_BY_ID:
            abort(404)

        user = utils.Auth.verify_authorization(request=request)

        if user is None:
            abort(400)

        file = request.files.get('file')
        form_data = request.form

        if (not form_data and not file) or not post_id:
            abort(400)

        post = models.Post.query.filter_by(id=post_id).first()

        if post is None:
            abort(400)

        post = post.update(form_data=form_data, file=file, user=user)

        if post is None:
            abort(400)

        response_message = {
            'message': f'Post successfuly updated!',
            'post': post.output()
        }

        return make_response(jsonify(response_message), 200)

    def delete(self, post_id: int):
        if str(request.url_rule) != self.URL_RULE_SINGLE_POST_BY_ID:
            abort(404)

        user = utils.Auth.verify_authorization(request=request)

        if user is None:
            abort(400)

        if not post_id:
            abort(400)
        
        post = models.Post.query.filter_by(id=post_id).first()

        if post is None:
            abort(400)

        post.delete()

        response_message = {
            'message': f'Post successfully deleted!'
        }

        return make_response(jsonify(response_message), 200)


class Comment(Resource):
    URL_RULE_SINGLE_COMMENT = '/post/comment/<int:comment_id>'
    URL_RULE_POST_COMMENTS = '/post/<int:post_id>/comment'

    def post(self, post_id: int):
        if str(request.url_rule) != self.URL_RULE_POST_COMMENTS:
            abort(404)

        user = utils.Auth.verify_authorization(request=request)

        if user is None:
            abort(400)

        form_data = request.form
        if not form_data:
            abort(400)

        post = models.Post.query.filter_by(id=post_id).first()
        if post is None:
            abort(400)

        comment = models.Comment()
        comment.save(form_data=form_data, post=post, user=user)

        response_message = {
            'message': 'Comment successfully inserted!',
            'comment': comment.output_with_permissions(user)
        }

        return make_response(jsonify(response_message), 201)

    def delete(self, comment_id: int):
        user = utils.Auth.verify_authorization(request=request)

        if user is None:
            abort(400)

        comment = models.Comment.query.filter_by(id=comment_id).first()
        comment.delete()

        response_message = {
            'message': f'Comment successfully deleted!'
        }

        return make_response(jsonify(response_message), 200)


class SubComment(Resource):
    URL_RULE_SUBCOMMENTS = '/post/comment/subcomment/<int:subcomment_id>'
    URL_RULE_COMMENT_SUBCOMMENTS = \
        '/post/comment/<int:comment_id>/subcomment'

    def post(self, comment_id: int):
        if str(request.url_rule) != self.URL_RULE_COMMENT_SUBCOMMENTS:
            abort(404)

        user = utils.Auth.verify_authorization(request=request)

        if user is None:
            abort(400)

        form_data = request.form

        if not form_data:
            abort(400)

        comment = models.Comment.query.filter_by(id=comment_id).first()
        if comment is None:
            abort(400)

        subcomment = models.SubComment()
        subcomment.save(form_data=form_data, comment=comment, user=user)

        response_message = {
            'message': f'Subcomment successfully inserted!',
            'subcomment': subcomment.output_with_permissions(user)
        }

        return make_response(jsonify(response_message), 201)

    def delete(self, subcomment_id: int):
        user = utils.Auth.verify_authorization(request=request)

        if user is None:
            abort(400)

        subcomment = models.SubComment.query.filter_by(
            id=subcomment_id).first()
        subcomment.delete()

        response_message = {
            'message': f'Subcomment successfully deleted!'
        }

        return make_response(jsonify(response_message), 200)

user_routes = [
    User.URL_RULE_USER,
    User.URL_RULE_USER_BY_ID
]

post_routes = [
    Post.URL_RULE_POST_ROOT,
    Post.URL_RULE_ALL_POSTS,
    Post.URL_RULE_SINGLE_POST_BY_ID,
    Post.URL_RULE_POSTS_BY_USER_ID,
    Post.URL_RULE_POSTS_BY_USERNAME
]

comment_routes = [
    Comment.URL_RULE_SINGLE_COMMENT,
    Comment.URL_RULE_POST_COMMENTS
]

subcomment_routes = [
    SubComment.URL_RULE_SUBCOMMENTS,
    SubComment.URL_RULE_COMMENT_SUBCOMMENTS
]
api.add_resource(User, *user_routes)
api.add_resource(Post, *post_routes)
api.add_resource(Comment, *comment_routes)
api.add_resource(SubComment, *subcomment_routes)
