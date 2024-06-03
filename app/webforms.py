# Create a Form Class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms.fields.simple import StringField, SubmitField, PasswordField, EmailField, TextAreaField
from wtforms.validators import DataRequired, EqualTo
from flask_ckeditor import CKEditorField


class NamerForm(FlaskForm):
    name = StringField('What\'s Your Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create a Password Form Class
class PasswordForm(FlaskForm):
    email = StringField('What\'s Your Email', validators=[DataRequired()])
    password_hash = PasswordField('What\'s Your Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create a User Form Class
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    favorite_color = StringField('Favorite Color')
    about_author = TextAreaField('About Author')
    password_hash = PasswordField('Password', validators=[DataRequired(),
                                                          EqualTo('password_hash2',
                                                                  message='Password must Match!')])
    profile_pic = FileField('Profile Pic')
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create a Posts Form
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    # content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Content', validators=[DataRequired()])
    author = StringField('Author')
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create a Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create a Search Form
class SearchForm(FlaskForm):
    searched = StringField('Searched', validators=[DataRequired()])
    submit = SubmitField('Submit')
