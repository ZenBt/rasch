from datetime import date
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import DateField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from app import app


class LoginForm(FlaskForm):
    username = StringField(label='Логин', validators=[DataRequired()])
    pwd = PasswordField(label='Пароль', validators=[DataRequired()])


class RubricForm(FlaskForm):
    title = StringField('Rubric', validators=[DataRequired(), Length(min=1, max=40)])
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(min=1, max=40)])
    date = DateField('Дата', default=date.today())
    rubric = SelectField('Рубрика', coerce=int)
    content = CKEditorField('Содержание', validators=[DataRequired()])
    submit = SubmitField('Submit')

class MainPageForm(FlaskForm):
    article = SelectField('article', coerce=int)
    submit = SubmitField('Submit')
