from flask import render_template, session, redirect, url_for, current_app, \
    abort, flash, request, make_response

from flask_login import login_required, current_user

from .. import db
from ..models import User, Role, Permission, Post, Comment
from ..email import send_email
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from ..decorators import admin_required, permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated():
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_BLOG_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           pagination=pagination, show_followed=show_followed)


@main.route('/post/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/post/following')
@login_required
def show_following():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', 'True', max_age=30*24*60*60)
    return resp


@main.route('/user/<username>')
def user(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        abort(404)
    posts = u.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=u, posts=posts)


@main.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Profile updated')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/profile/<int:id>/admin-edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    u = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=u)
    if form.validate_on_submit():
        u.email = form.email.data
        u.username = form.username.data
        u.confirmed = form.confirmed.data
        u.role = Role.query.get(form.role.data)
        u.name = form.name.data
        u.location = form.location.data
        u.about_me = form.about_me.data
        db.session.add(u)
        flash('Profile updated')
        return redirect(url_for('.user', username=u.username))
    form.email.data = u.email
    form.username.data = u.username
    form.confirmed.data = u.confirmed
    form.role.data = u.role_id
    form.name.data = u.name
    form.location.data = u.location
    form.about_me.data = u.about_me
    return render_template('edit_profile.html', form=form, user=u)


@main.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    p = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=p,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Comment published')
        return redirect(url_for('.post', post_id=p.id, page=1))
    page = request.args.get('page', 1, type=int)
    pagination = p.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    return render_template('post.html', posts=[p], form=form,
                           comments=comments, pagination=pagination)


@main.route('/post/<int:post_id>/edit', methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    p = Post.query.get_or_404(post_id)
    if current_user != p.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        p.body = form.body.data
        db.session.add(p)
        flash('The post has been updated.')
        return redirect('/post/'+str(p.id))
    form.body.data = p.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        flash('Invalid user')
        return redirect(url_for('.index'))
    if current_user.is_following(u):
        flash('Already following')
        return redirect(url_for('.user', username=username))
    current_user.follow(u)
    flash('You are following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        flash('Invalid user')
        return redirect(url_for('.index'))
    if not current_user.is_following(u):
        flash('Not following already')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(u)
    flash('You are now not following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/<username>/followers')
def followers(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        flash('Invalid user')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = u.followers.paginate(page, per_page=current_app.config['USERS_PER_PAGE'],
                                      error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('follows.html', user=u, title='Followers of',
                           endpoint='.followers', pagination=pagination,
                           follows=follows)

@main.route('/<username>/following')
def following(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        flash('Invalid user')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = u.followed.paginate(page, per_page=current_app.config['USERS_PER_PAGE'],
                                     error_out=False)
    follows = [{'user': i.followed, 'timestamp': i.timestamp} for i in pagination.items]
    return render_template('follows.html', user=u, title='Following of',
                           endpoint='.following', pagination=pagination,
                           follows=follows)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))