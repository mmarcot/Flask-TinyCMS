from flask import Flask, render_template, request, url_for, redirect, flash, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, HiddenField, SelectField
from wtforms.validators import InputRequired, Email, Length, Optional
from flask_login import LoginManager, login_user, login_required, current_user, UserMixin, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_babel import _, Babel, lazy_gettext

from datetime import datetime
import json



#######################################################################################################
##                                                                                                   ##
##                                             CONFIG                                                ##
##                                                                                                   ##
#######################################################################################################

app = Flask(__name__)
app.config['SECRET_KEY'] = 'makes-me-oulououuua766d'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),
]
babel = Babel(app)

@babel.localeselector
def get_locale():
    return Configuration.get_current_language()


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.context_processor
def inject_templates():
    pages = Page.query.filter_by(published=True)
    config_language = Configuration.get_current_language()
    return {'site_pages': pages, 'config_language': config_language}


def flash_form_errors(form):
    for field_name, errors in form.errors.items():
        for error in errors:
            flash(error, 'danger')


#######################################################################################################
##                                                                                                   ##
##                                              FORMS                                                ##
##                                                                                                   ##
#######################################################################################################

class PostCreateForm(FlaskForm):
    title = StringField(lazy_gettext('Title'), validators=[Length(1,199,lazy_gettext("The title should contain between 1 and 200 characters"))])
    slug = StringField(lazy_gettext('Slug'), validators=[Length(1,199,lazy_gettext("The slug should contain between 1 and 200 characters"))])
    tags = StringField(lazy_gettext('Tags'), render_kw={"data-role":"tagsinput"})
    published = BooleanField(lazy_gettext('Published'), default=True)
    abstract_image = StringField(lazy_gettext('Abstract image'), validators=[Optional(),Length(1,199,lazy_gettext("The link to the image should contain between 1 and 200 characters"))])
    abstract = TextAreaField(lazy_gettext('Abstract'), validators=[Optional()])
    content = TextAreaField(lazy_gettext('Content'))
    form_type = HiddenField()
    submit = SubmitField(lazy_gettext('Create'))

class PostEditForm(PostCreateForm):
    submit = SubmitField(lazy_gettext('Save'))


class PageCreateForm(FlaskForm):
    title = StringField(lazy_gettext('Title'), validators=[Length(1,199,lazy_gettext("The title should contain between 1 and 200 characters"))])
    slug = StringField(lazy_gettext('Slug'), validators=[Length(1,199,lazy_gettext("The slug should contain between 1 and 200 characters"))])
    nav_label = StringField(lazy_gettext('Navigation label'), validators=[Length(1,49,lazy_gettext("The navigation label should contain between 1 and 50 characters"))])
    published = BooleanField(lazy_gettext('Published'), default=True)
    content = TextAreaField(lazy_gettext('Content'))
    form_type = HiddenField()
    submit = SubmitField(lazy_gettext('Create'))

class PageEditForm(PageCreateForm):
    submit = SubmitField(lazy_gettext('Save'))


class UserCreateForm(FlaskForm):
    username = StringField(lazy_gettext('Username'), validators=[InputRequired(lazy_gettext("Username cannot be empty")), Length(5,49,lazy_gettext("The username should contain between 5 and 50 characters"))])
    email = StringField(lazy_gettext('Email'), validators=[InputRequired(lazy_gettext("Email cannot be empty")), Email(lazy_gettext("The given e-mail is not valid"))])
    password = PasswordField(lazy_gettext('Password'), validators=[Length(5,49,lazy_gettext("The password should contain between 5 and 50 characters"))])
    submit = SubmitField(lazy_gettext('Create'))

class UserEditForm(UserCreateForm):
    password = PasswordField(lazy_gettext('Password'), validators=[Optional(), Length(5,49,lazy_gettext("The password should contain between 5 and 50 characters"))])
    submit = SubmitField(lazy_gettext('Save'))


class TagCreateForm(FlaskForm):
    name = StringField(lazy_gettext('Name'), validators=[Length(2,49, lazy_gettext("The tag name should contain between 2 and 50 characters"))])
    submit = SubmitField(lazy_gettext('Create'))

class TagEditForm(TagCreateForm):
    submit = SubmitField(lazy_gettext('Save'))


class AdminConfigurationForm(FlaskForm):
    language = SelectField(lazy_gettext('Language'), choices=LANGUAGES)
    submit = SubmitField(lazy_gettext('Save'))



#######################################################################################################
##                                                                                                   ##
##                                             MODELS                                                ##
##                                                                                                   ##
#######################################################################################################


tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False,  unique=True)
    abstract = db.Column(db.Text)
    abstract_image = db.Column(db.String(200))
    content = db.Column(db.Text)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    published = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    tags = db.relationship('Tag', secondary=tags, lazy='subquery', backref=db.backref('posts', lazy=True))

    @validates('slug')
    def validates_slug(self, key, value):
        assert len(value) >= 1, _("The slug should be at least 1 character")
        return value

    @property
    def tags_str(self):
        res = ""
        for tag in self.tags:
            res += tag.name + ','
        return res.strip(' ,')

    def add_tags(self, tags):
        '''
        Add given tags to the post
        :tags tags string separated with comma
        '''
        for tag_name in [t.strip() for t in tags.split(',') if t]:
            existing_tag = Tag.query.filter(Tag.name.ilike(tag_name)).first()
            if not existing_tag:
                new_tag = Tag(name=tag_name)
                db.session.add(new_tag)
                db.session.commit()
                existing_tag = new_tag
            self.tags.append(existing_tag)


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    nav_label = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    content = db.Column(db.Text)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    published = db.Column(db.Boolean, nullable=False, default=False)

    @validates('slug')
    def validates_slug(self, key, value):
        assert len(value) >= 1, _("The slug should be at least 1 character")
        return value

    @validates('nav_label')
    def validates_nav_label(self, key, value):
        assert len(value) >= 1, _("The navigation label should be at least 1 character")
        return value




class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    @validates('username')
    def validates_username(self, key, value):
        assert len(value) >= 1, _("Username should be at least 1 character")
        return value

    @validates('password')
    def validates_password(self, key, value):
        assert len(value) >= 1, _("Password should be at least 1 character")
        return value

        

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    @validates('name')
    def validates_name(self, key, value):
        assert len(value) >= 1, _("The tag name should be at least 1 character")
        return value


class Configuration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    user = db.relationship('User', backref=db.backref('config', lazy=True))
    language = db.Column(db.String(50), default='en')

    @classmethod
    @login_required
    def get_current_config(cls):
        '''
        /!\ Login required
        @return the current user config, if there is no configuration for the user, creates a new one
        '''
        config = cls.query.filter_by(user_id=current_user.id).first()
        if not config:
            config = Configuration(user_id=current_user.id)
            db.session.add(config)
            db.session.commit()
        return config

    @classmethod
    def get_current_language(cls):
        '''
        Get the prefered language either if the user is logged in or not.
        @return 'fr' or 'en' ...
        '''
        if current_user.is_authenticated:
            config = cls.get_current_config()
            return config.language
        else:
            return request.accept_languages.best_match([tu[0] for tu in LANGUAGES])

    

#######################################################################################################
##                                                                                                   ##
##                                              VIEWS                                                ##
##                                                                                                   ##
#######################################################################################################

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
    return render_template('site-post-detail.html', post=post)


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

