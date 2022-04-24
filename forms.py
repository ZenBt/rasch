from datetime import date
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import DateField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired

from app import app


class LoginForm(FlaskForm):
    username = StringField(label='Логин', validators=[DataRequired()])
    pwd = PasswordField(label='Пароль', validators=[DataRequired()])


class RubricForm(FlaskForm):
    title = StringField('Rubric', validators=[DataRequired()])
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    date = DateField('Дата', default=date.today())
    rubric = SelectField('Рубрика', coerce=int)
    content = CKEditorField('Содержание', validators=[DataRequired()])
    submit = SubmitField('Submit')
