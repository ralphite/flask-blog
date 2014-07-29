__author__ = 'yawen'

from flask import request, current_app, url_for, jsonify
from .import api
from ..models import User, Post


@api.route('/users/<int:user_id>')
def get_user(user_id):
    u = User.query.get_or_404(user_id)
    return jsonify(u.to_json())


@api.route('/users/<int:user_id>/posts/')
def get_user_posts(user_id):
    u = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    pagination = u.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_BLOG_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_posts', page=page-1, user_id=user_id,
                       _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_posts', page=page+1, user_id=user_id,
                       _external=True)
    return jsonify({
        'posts': [p.to_json() for p in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/users/<int:user_id>/posts/following')
def get_user_following_posts(user_id):
    u = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    pagination = u.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_BLOG_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_following_posts', page=page-1, user_id=user_id,
                       _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_following_posts', page=page-1, user_id=user_id,
                       _external=True)
    return jsonify({
        'post': [p.to_json() for p in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })