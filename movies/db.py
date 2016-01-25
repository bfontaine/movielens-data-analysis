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

    def post_import(self):
        # should be redefined by child classes
        pass


class Movie(BaseModel):
    movie_id = IntegerField(unique=True, primary_key=True)
    title = CharField()
    # TODO change these to DateFields
    release_date = DateTimeField(null=True) # should null really be allowed?
    video_release_date = DateTimeField(null=True)
    imdb_url = CharField()

    # cached values
    ratings_count = IntegerField(null=True)

    @classmethod
    def genre_attr(cls, g):
        return "genre_%s" % g.lower().replace("-", "_").replace("'", "")

    def genres(self):
        return [g for g in GENRES if self.has_genre(g)]

    def has_genre(self, genre):
        return getattr(self, Movie.genre_attr(genre))

    def set_genres(self, genres):
        for g, v in zip(GENRES, genres):
            attr = Movie.genre_attr(g)
            setattr(self, attr, bool(int(v)))

    def post_import(self):
        self.ratings_count = len(self.ratings)

    def __eq__(self, other):
        return isinstance(other, Movie) and self.movie_id == other.movie_id

class User(BaseModel):
    user_id = IntegerField(unique=True, primary_key=True)
    age = IntegerField()
    gender = FixedCharField(max_length=1)
    occupation = CharField()
    zip_code = CharField()

    # cached values
    ratings_count = IntegerField(null=True)

    def post_import(self):
        self.ratings_count = len(self.ratings)

    def __eq__(self, other):
        return isinstance(other, User) and self.user_id == other.user_id


class Rating(BaseModel):
    user = ForeignKeyField(User, related_name="ratings")
    movie = ForeignKeyField(Movie, related_name="ratings")
    rating = IntegerField()
    date = DateTimeField()

    def __eq__(self, other):
        return self.user == other.user and \
                self.movie == other.movie and \
                self.date == other.date

for g in GENRES:
    # http://stackoverflow.com/a/22365143/735926
    BooleanField(verbose_name=g).add_to_class(Movie, Movie.genre_attr(g))

def init_db():
    db.connect()
    db.create_tables([Movie, User, Rating], True)
