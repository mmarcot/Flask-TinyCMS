from flask import Flask, render_template, request, url_for, redirect, flash, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, login_user, login_required, current_user, UserMixin, logout_user

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

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.context_processor
def inject_pages():
    pages = Page.query.filter_by(published=True)
    return {'site_pages': pages}



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
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False,  unique=True)
    abstract = db.Column(db.Text, nullable=False)
    abstract_image = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    published = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    tags = db.relationship('Tag', secondary=tags, lazy='subquery', backref=db.backref('posts', lazy=True))

    @property
    def tags_str(self):
        res = ""
        for tag in self.tags:
            res += tag.name + ', '
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

    def get_json_for(self, *args):
        '''
        Returns its fields into a JSON formatted object
        :*args fields to be included in the json return
        '''
        res = {}
        for arg in args:
            res[arg] = getattr(self, arg)
        return json.dumps(res)


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    nav_label = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    published = db.Column(db.Boolean, nullable=False, default=False)

    def get_json_for(self, *args):
        '''
        Returns its fields into a JSON formatted object
        :*args fields to be included in the json return
        '''
        res = {}
        for arg in args:
            res[arg] = getattr(self, arg)
        return json.dumps(res)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def get_json_for(self, *args):
        '''
        Returns its fields into a JSON formatted object
        :*args fields to be included in the json return
        '''
        res = {}
        for arg in args:
            res[arg] = getattr(self, arg)
        return json.dumps(res)
        

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)






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
    if user and user.password == request.form['password']:
        login_user(user, remember=True)
        return redirect(url_for('admin_posts'))
    flash('Bad login')
    return render_template('site-login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



################## ADMIN POSTS

@app.route('/admin/posts')
@login_required
def admin_posts():
    posts = Post.query.all()
    return render_template('admin-posts.html', posts=posts)


@app.route('/admin/posts/new', methods=['POST'])
@login_required
def admin_posts_new():
    published = request.form.get('published', False)  == 'on'
    new_post = Post(
        title=request.form['title'].strip(),
        slug=request.form['slug'].strip(),
        published=published,
        abstract=request.form['abstract'].strip(),
        abstract_image=request.form['abstract_image'].strip(),
        content=request.form['content'].strip(),
        user_id=current_user.id,
    )
    new_post.add_tags(request.form['tags'])
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('admin_posts'))


@app.route('/admin/posts/delete/<int:post_id>', methods=['POST'])
@login_required
def admin_posts_delete(post_id):
    db.session.delete(Post.query.get(post_id))
    db.session.commit()
    return redirect(url_for('admin_posts'))


@app.route('/admin/posts/edit', methods=['POST'])
@login_required
def admin_posts_edit():
    post_id = int(request.form['post_id'])
    post = Post.query.get(post_id)
    post.title = request.form['title'].strip()
    post.slug = request.form['slug'].strip()
    post.published = request.form.get('published', False)  == 'on'
    post.abstract_image = request.form['abstract_image'].strip()
    post.abstract = request.form['abstract'].strip()
    post.content = request.form['content'].strip()
    post.add_tags(request.form['tags'])
    db.session.commit()
    return redirect(url_for('admin_posts'))




################## ADMIN PAGES

@app.route('/admin/pages')
@login_required
def admin_pages():
    pages = Page.query.all()
    return render_template('admin-pages.html', pages=pages)


@app.route('/admin/pages/new', methods=['POST'])
@login_required
def admin_pages_new():
    published = request.form.get('published', False)  == 'on'
    new_page = Page(
        title=request.form['title'].strip(),
        nav_label=request.form['nav_label'].strip(),
        slug=request.form['slug'].strip(),
        content=request.form['content'].strip(),
        published=published,
    )
    db.session.add(new_page)
    db.session.commit()
    return redirect(url_for('admin_pages'))


@app.route('/admin/pages/delete/<int:page_id>', methods=['POST'])
@login_required
def admin_pages_delete(page_id):
    db.session.delete(Page.query.get(page_id))
    db.session.commit()
    return redirect(url_for('admin_pages'))


@app.route('/admin/pages/edit', methods=['POST'])
@login_required
def admin_pages_edit():
    page_id = int(request.form['page_id'])
    page = Page.query.get(page_id)
    page.title = request.form['title'].strip()
    page.nav_label = request.form['nav_label'].strip()
    page.slug = request.form['slug'].strip()
    page.published = request.form.get('published', False)  == 'on'
    page.content = request.form['content'].strip()
    db.session.commit()
    return redirect(url_for('admin_pages'))


############ ADMIN TAGS

@app.route('/admin/tags')
@login_required
def admin_tags():
    tags = Tag.query.all()
    return render_template('admin-tags.html', tags=tags)


@app.route('/admin/tags/new', methods=['POST'])
@login_required
def admin_tags_new():
    new_tag = Tag(name=request.form['name'].strip())
    db.session.add(new_tag)
    db.session.commit()
    return redirect(url_for('admin_tags'))


@app.route('/admin/tags/delete/<int:tag_id>', methods=['POST'])
@login_required
def admin_tags_delete(tag_id):
    db.session.delete(Tag.query.get(tag_id))
    db.session.commit()
    return redirect(url_for('admin_tags'))


@app.route('/admin/tags/edit', methods=['POST'])
@login_required
def admin_tags_edit():
    tag_id = int(request.form['tag_id'])
    tag = Tag.query.get(tag_id)
    tag_name = request.form['new_tag_name']
    tag.name = tag_name.strip()
    db.session.commit()
    return redirect(url_for('admin_tags'))




############# ADMIN USERS

@app.route('/admin/users')
@login_required
def admin_users():
    users = User.query.all()
    return render_template('admin-users.html', users=users)


@app.route('/admin/users/new', methods=['POST'])
@login_required
def admin_users_new():
    username = request.form['username'].strip()
    email = request.form['email'].strip()
    password = request.form['password'].strip()
    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('admin_users'))


@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_users_delete(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_users'))


@app.route('/admin/users/edit', methods=['POST'])
@login_required
def admin_users_edit():
    user_id = int(request.form['user_id'])
    user = User.query.get(user_id)
    user.username = request.form['new_username'].strip()
    user.email = request.form['new_email'].strip()
    db.session.commit()
    return redirect(url_for('admin_users'))

