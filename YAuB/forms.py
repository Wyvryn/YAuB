"""Flask-WTF form definitions"""

import models
from flask_wtf import Form
from wtforms import (BooleanField, HiddenField, IntegerField, PasswordField,
                     SelectMultipleField, TextAreaField, TextField)
from wtforms.validators import DataRequired, EqualTo, NumberRange


class LoginForm(Form):
    username = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = models.Author.query.filter_by(username=self.username.data).first()
        if not self.user:
            self.username.errors.append('Unknown username')
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        return True


class ArticleForm(Form):
    title = TextField('Title:', validators=[DataRequired()])
    author = HiddenField()
    content = TextAreaField('Content:', validators=[DataRequired()])
    short = TextAreaField('Short:')
    published = TextField('Published:', validators=[DataRequired()])
    isvisible = BooleanField('Is Visible:')
    tags = SelectMultipleField('Tags:')

    def validate(self):
        return True


class AuthorForm(Form):
    displayname = TextField('Display Name:', validators=[DataRequired()])
    username = TextField('User Name:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[
        EqualTo('password_confirm', message='Passwords must match')
    ]
    )
    password_confirm = PasswordField('Confirm Password:')


class ConfigForm(Form):
    about = TextAreaField('About:')
    blogname = TextField('Blog Name:', validators=[DataRequired()])
    articlesperpage = IntegerField('Articles Per Page:', validators=[NumberRange(1, 100)])
