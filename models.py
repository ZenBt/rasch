from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

from app import app

db = SQLAlchemy(app)


class Slug():

    def __init__(self, id: int, title: str) -> None:
        self._slug = f'{str(id)}-{self.slugify(title)}'

    @staticmethod
    def slugify(title: str) -> str:
        slug = ''
        slug_dict = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
                     'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'tch', 'ш': 'sh', 'щ': 'sh', 'ъ': 'u', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'}
        for el in title.lower():
            if el.isalpha() or el.isdigit():
                if el in slug_dict.keys():
                    slug += slug_dict[el]
                else:
                    slug += el

            else:
                slug += '-'

        while '--' in slug:
            slug = slug.replace('--', '-')
        return slug

    @property
    def slug(self):
        return self._slug

    @staticmethod
    def get_id(class_):
        item = class_.query.order_by(class_.id.desc()).first()
        if item is not None:
            return item.id + 1
        return 1


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40))
    content = db.Column(db.Text)
    slug = db.Column(db.String(125), nullable=True)
    date_id = db.Column(db.Integer, db.ForeignKey("archive.id"))
    rubric_id = db.Column(db.Integer, db.ForeignKey("rubrics.id"))
    dates = db.relationship('Archive', backref='posts')
    tags = db.relationship('Rubrics', backref='posts')

    def __init__(self, *args, **kwargs) -> None:
        super(Posts, self).__init__(*args, **kwargs)
        post_id = Slug.get_id(Posts)
        self.slug = Slug(id=post_id, title=self.title).slug

    def __repr__(self):
        return f'id = {self.id}, title = {self.title}'


class Rubrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40))
    slug = db.Column(db.String(125), nullable=True)

    def __init__(self, *args, **kwargs) -> None:
        super(Rubrics, self).__init__(*args, **kwargs)
        rubric_id = Slug.get_id(Rubrics)
        self.slug = Slug(id=rubric_id, title=self.title).slug

    def __repr__(self):
        return f'id = {self.id}, title = {self.title}'


class Archive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)

    def __repr__(self):
        return f'id = {self.id}, date = {self.date}'


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(30))

    def __repr__(self):
        return f'id = {self.id}, username={self.username}'
