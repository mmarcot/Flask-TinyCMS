from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, HiddenField, SelectField
from wtforms.validators import InputRequired, Email, Length, Optional
from flask_babel import lazy_gettext

from .utils import LANGUAGES



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



class CommentForm(FlaskForm):
    author_name = StringField(lazy_gettext('Name'), validators=[Length(1,49, lazy_gettext("The name should contain between 1 and 50 characters"))])
    author_email = StringField(lazy_gettext('Email'), validators=[InputRequired(lazy_gettext("Email cannot be empty")), Email(lazy_gettext("The given e-mail is not valid"))])
    content = TextAreaField(lazy_gettext('Content'))
    submit = SubmitField(lazy_gettext('Create'))



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
