from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from wtforms.widgets import TextArea

# create a name form class
class NamerForm(FlaskForm):
    name = StringField("What is your name", validators=[DataRequired()])
    submit = SubmitField("Submit")

# create a login form class
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

# create a user form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    mobile = StringField("Mobile")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Password must match!!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

# create a password form class
class PasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

# create a post form class
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")

# create a search form class
class SearchForm(FlaskForm):
    search_input = StringField("Search Input", validators=[DataRequired()])
    submit = SubmitField("Submit")