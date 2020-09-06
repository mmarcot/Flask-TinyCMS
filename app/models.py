from flask import request
from sqlalchemy.orm import validates
from flask_login import login_required, current_user, UserMixin
from flask_babel import _

from datetime import datetime

from app import db
from .utils import LANGUAGES


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



class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    approved = db.Column(db.Boolean, nullable=False, default=False)
    author_name = db.Column(db.String(50), nullable=False)
    author_email = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))



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


