# -*- coding: UTF-8 -*-

import peewee
from peewee import IntegerField, CharField, DateTimeField, BooleanField
from peewee import FixedCharField, ForeignKeyField
from playhouse.sqlite_ext import SqliteExtDatabase

GENRES = [
    "Unknown", "Action", "Adventure", "Animation", "Children's", "Comedy",
    "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror",
    "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western",
]

db = SqliteExtDatabase("movies.db")

class BaseModel(peewee.Model):
    class Meta:
        database = db

class Movie(BaseModel):
    movie_id = IntegerField(unique=True, primary_key=True)
    title = CharField()
    release_date = DateTimeField()
    video_release_date = DateTimeField(null=True)
    imdb_url = CharField()

    def has_genre(self, genre):
        # TESTME
        return getattr(self, Movie.genre_attr(genre))

    def set_genres(self, genres):
        # TESTME
        for g, v in zip(GENRES, genres):
            attr = Movie.genre_attr(g)
            setattr(self, attr, bool(int(v)))

    @classmethod
    def genre_attr(cls, g):
        return "genre_%s" % g.lower().replace("-", "_").replace("'", "")

class User(BaseModel):
    user_id = IntegerField(unique=True, primary_key=True)
    age = IntegerField()
    gender = FixedCharField(max_length=1)
    occupation = CharField()
    zip_code = CharField()

class Rating(BaseModel):
    user = ForeignKeyField(User, related_name="ratings")
    movie = ForeignKeyField(Movie, related_name="ratings")
    rating = IntegerField()
    date = DateTimeField()

for g in GENRES:
    # http://stackoverflow.com/a/22365143/735926
    BooleanField(verbose_name=g).add_to_class(Movie, Movie.genre_attr(g))

def init_db():
    db.connect()
    db.create_tables([Movie, User, Rating], True)
