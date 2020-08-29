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
    pages = Page.query.all()
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


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    nav_label = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    published = db.Column(db.Boolean, nullable=False, default=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def get_json_for(self, *args):
        '''
        :*args fields to be included in the json return
        Method that returns its fields into a JSON formatted object
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
    posts = Post.query.all()
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


@app.route('/admin/pages')
@login_required
def admin_pages():
    pages = Page.query.all()
    return render_template('admin-pages.html', pages=pages)


@app.route('/admin/posts')
@login_required
def admin_posts():
    posts = Post.query.all()
    return render_template('admin-posts.html', posts=posts)



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


if __name__ == "__main__":
    app.run()
