from flask import render_template, request, url_for, redirect, flash, abort
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_babel import _

from .forms import *
from .models import User, Configuration, Tag, Post, Page, Comment

from app import app, db
from .utils import flash_form_errors


@app.route('/')
def index():
    return render_template('site-index.html')


@app.route('/blog')
def blog():
    posts = Post.query.filter_by(published=True)
    return render_template('site-blog.html', posts=posts)


@app.route('/post/<slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        abort(404)
    comments = Comment.query.filter_by(post_id=post.id, approved=True)
    return render_template('site-post-detail.html', post=post, comments=comments)


@app.route('/page/<slug>')
def page_detail(slug):
    page = Page.query.filter_by(slug=slug).first()
    if not page:
        abort(404)
    return render_template('site-page-detail.html', page=page)


@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'GET':
        return render_template('site-login.html')
    user = User.query.filter_by(email=request.form['mail_or_username']).first()
    if not user:
        user = User.query.filter_by(username=request.form['mail_or_username']).first()
    if user and check_password_hash(user.password, request.form['password']):
        login_user(user, remember=True)
        return redirect(url_for('admin_posts'))
    flash(_("Username and password doesn't match"), 'danger')
    return render_template('site-login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/admin/configuration', methods=['GET', 'POST'])
@login_required
def admin_configuration():
    form = AdminConfigurationForm()
    config = Configuration.get_current_config()
    if form.validate_on_submit():
        config.language = form.language.data
        db.session.commit()
        flash(_('Configuration saved'), 'info')
        return redirect(url_for('admin_configuration'))
    form.language.data = config.language
    return render_template('admin-configuration.html', form=form)



################## ADMIN POSTS

@app.route('/admin/posts')
@login_required
def admin_posts():
    posts = Post.query.all()
    return render_template('admin-posts.html', posts=posts)


@app.route('/admin/posts/create', methods=['GET','POST'])
@login_required
def admin_posts_create():
    form = PostCreateForm()
    if form.validate_on_submit():
        new_post = Post(
            title = form.title.data,
            slug = form.slug.data,
            published = form.published.data,
            abstract = form.abstract.data,
            abstract_image = form.abstract_image.data,
            content = form.content.data,
            user_id = current_user.id,
        )
        new_post.add_tags(form.tags.data)
        db.session.add(new_post)
        db.session.commit()
        flash(_("The post '%s' has been created successfully") % new_post.title, 'info')
        return redirect(url_for('admin_posts'))
    flash_form_errors(form)
    return render_template('admin-posts-create.html', form=form)


@app.route('/admin/posts/delete/<int:post_id>', methods=['POST'])
@login_required
def admin_posts_delete(post_id):
    post = Post.query.get(post_id)
    flash(_("Post '%s' deleted") % post.title, 'info')
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('admin_posts'))


@app.route('/admin/posts/edit/<int:post_id>', methods=['GET','POST'])
@login_required
def admin_posts_edit(post_id):
    post = Post.query.get(post_id)
    form = PostEditForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.slug = form.slug.data
        post.published = form.published.data
        post.abstract_image = form.abstract_image.data
        post.abstract = form.abstract.data
        post.content = form.content.data
        post.tags.clear()
        post.add_tags(request.form['tags'])
        db.session.commit()
        return redirect(url_for('admin_posts'))
    flash_form_errors(form)
    form.title.data = post.title
    form.slug.data = post.slug
    form.published.data = post.published
    form.abstract_image.data = post.abstract_image
    form.abstract.data = post.abstract
    form.content.data = post.content
    form.tags.data = post.tags_str
    return render_template('admin-posts-edit.html', post=post, form=form)




################## ADMIN PAGES

@app.route('/admin/pages')
@login_required
def admin_pages():
    pages = Page.query.all()
    return render_template('admin-pages.html', pages=pages)


@app.route('/admin/pages/create', methods=['GET','POST'])
@login_required
def admin_pages_create():
    form = PageCreateForm()
    if form.validate_on_submit():
        new_page = Page(
            title = form.title.data,
            nav_label = form.nav_label.data,
            slug = form.slug.data,
            content = form.content.data,
            published = form.published.data,
        )
        db.session.add(new_page)
        db.session.commit()
        flash(_("The page '%s' has been created successfully") % new_page.nav_label, 'info')
        return redirect(url_for('admin_pages'))
    flash_form_errors(form)
    return render_template('admin-pages-create.html', form=form)


@app.route('/admin/pages/delete/<int:page_id>', methods=['POST'])
@login_required
def admin_pages_delete(page_id):
    page = Page.query.get(page_id)
    db.session.delete(page)
    db.session.commit()
    flash(_("The page '%s' has been deleted") % page.nav_label, 'info')
    return redirect(url_for('admin_pages'))


@app.route('/admin/pages/edit/<int:page_id>', methods=['GET','POST'])
@login_required
def admin_pages_edit(page_id):
    page = Page.query.get(page_id)
    form = PageEditForm()
    if form.validate_on_submit():
        page.title = form.title.data
        page.nav_label = form.nav_label.data
        page.slug = form.slug.data
        page.published = form.published.data
        page.content = form.content.data
        db.session.commit()
        return redirect(url_for('admin_pages'))
    flash_form_errors(form)
    form.title.data = page.title
    form.nav_label.data = page.nav_label
    form.slug.data = page.slug
    form.published.data = page.published
    form.content.data = page.content
    return render_template('admin-pages-edit.html', page=page, form=form)
        



############ ADMIN TAGS

@app.route('/admin/tags')
@login_required
def admin_tags():
    tags = Tag.query.all()
    return render_template('admin-tags.html', tags=tags)


@app.route('/admin/tags/create', methods=['POST', 'GET'])
@login_required
def admin_tags_create():
    form = TagCreateForm()
    if form.validate_on_submit():
        new_tag = Tag(name=form.name.data)
        db.session.add(new_tag)
        db.session.commit()
        flash(_("The tag '%s' has been created") % new_tag.name, 'info')
        return redirect(url_for('admin_tags'))
    flash_form_errors(form)
    return render_template('admin-tags-create.html', form=form)


@app.route('/admin/tags/delete/<int:tag_id>', methods=['POST'])
@login_required
def admin_tags_delete(tag_id):
    tag = Tag.query.get(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash(_("The tag '%s' has been deleted") % tag.name, 'info')
    return redirect(url_for('admin_tags'))


@app.route('/admin/tags/edit/<int:tag_id>', methods=['GET','POST'])
@login_required
def admin_tags_edit(tag_id):
    tag = Tag.query.get(tag_id)
    form = TagEditForm()
    if form.validate_on_submit():
        tag.name = form.name.data
        db.session.commit()
        return redirect(url_for('admin_tags'))
    flash_form_errors(form)
    form.name.data = tag.name
    return render_template('admin-tags-edit.html', tag=tag, form=form)




############# ADMIN USERS

@app.route('/admin/users')
@login_required
def admin_users():
    users = User.query.all()
    return render_template('admin-users.html', users=users)


@app.route('/admin/users/create', methods=['GET','POST'])
@login_required
def admin_users_create():
    form = UserCreateForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data, 
            email=form.email.data, 
            password=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash(_("The user '%s' has been created") % form.username.data, 'info')
        return redirect(url_for('admin_users'))
    flash_form_errors(form)
    return render_template('admin-users-create.html', form=form)


@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_users_delete(user_id):
    user = User.query.get(user_id)
    flash(_("The user '%s' has been deleted") % user.username, 'info')
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_users'))


@app.route('/admin/users/edit/<int:user_id>', methods=['GET','POST'])
@login_required
def admin_users_edit(user_id):
    form = UserEditForm()
    user = User.query.get(user_id)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.password = generate_password_hash(form.password.data)
        db.session.commit()
        return redirect(url_for('admin_users'))
    flash_form_errors(form)
    form.username.data = user.username
    form.email.data = user.email
    return render_template('admin-users-edit.html', user=user, form=form)

