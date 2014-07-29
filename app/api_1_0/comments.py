__author__ = 'yawen'

from flask import request, g, current_app, url_for, jsonify

from .import api
from ..import db
from ..models import Comment, Post, Permission
from .decorators import permission_required


@api.route('/comments/')
def get_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', page=page+1, _external=True)
    return jsonify({
        'comments': [c.to_json() for c in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/comments/<int:comment_id>')
def get_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return jsonify(comment.to_json())


@api.route('/posts/<int:post_id>/comments/')
def get_post_comments(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', page=page+1, _external=True)
    return jsonify({
        'comments': [c.to_json() for c in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/posts/<int:post_id>/comments/', methods=['POST'])
@permission_required(Permission.COMMENT)
def post_post_comment(post_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, {
        'Location': url_for('api.get_comment', comment_id=comment.id, _external=True)
    }