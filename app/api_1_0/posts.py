__author__ = 'yawen'

from .import api
from ..import db
from ..auth import auth
from ..models import Post, Permission
from decorators import permission_required
from flask import jsonify, request, url_for, g

@api.route('/posts/')
@auth.login_required
def get_posts():
    posts = Post.query.all()
    return jsonify({'posts': [post.to_json() for post in posts]})


@api.route('/posts/<int:id>')
@auth.login__required
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, {
        'location': url_for('api.get_post', id=post.id, _external=True)
    }