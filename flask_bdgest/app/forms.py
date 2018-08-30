from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class AuthorForm(FlaskForm):
    name = StringField('Name')
    country = StringField('Country')
    search = SubmitField('search')

class SeriesForm(FlaskForm):
    name = StringField('Name')
    author_name = StringField('Author')
    genre = StringField('Genre')
    lang = StringField('Language')
    origin = StringField('Origin')
    status = StringField('Status')
    search = SubmitField('search')

class ComicForm(FlaskForm):
    title = StringField('Title')
    editor = StringField('Editor')
    collection = StringField('Collection')
    format = StringField('Format')
    isbn = StringField('ISBN')
    search = SubmitField('search')
    author_name = StringField('Author')
    series_name = StringField('Series')
