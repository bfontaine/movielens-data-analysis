# -*- coding: UTF-8 -*-

import json
from collections import defaultdict, OrderedDict
from datetime import datetime

import peewee
from peewee import IntegerField, CharField, DateField, DateTimeField
from peewee import BooleanField, FixedCharField, ForeignKeyField, FloatField
from playhouse.sqlite_ext import SqliteExtDatabase
from pyzipcode import ZipCodeDatabase

# we need to keep them ordered so that they're in the same order as the
# MovieLens files, making imports easier.
GENRES = OrderedDict((
    ("unknown", "Unknown"),
    ("action", "Action"),
    ("adventure", "Adventure"),
    ("animation", "Animation"),
    ("children", "Children's"),
    ("comedy", "Comedy"),
    ("crime", "Crime"),
    ("documentary", "Documentary"),
    ("drama", "Drama"),
    ("fantasy", "Fantasy"),
    ("film_noir", "Film-Noir"),
    ("horror", "Horror"),
    ("musical", "Musical"),
    ("mystery", "Mystery"),
    ("romance", "Romance"),
    ("sci_fi", "Sci-Fi"),
    ("thriller", "Thriller"),
    ("war", "War"),
    ("western", "Western"),
))

db = SqliteExtDatabase("movies.db")
zcdb = ZipCodeDatabase()

class BaseModel(peewee.Model):
    class Meta:
        database = db

    def post_import(self):
        # should be redefined by child classes
        pass


class Movie(BaseModel):
    movie_id = IntegerField(unique=True, primary_key=True)
    title = CharField()
    # null=True because the dataset is not that clean
    release_date = DateField(null=True)
    video_release_date = DateField(null=True)
    imdb_url = CharField()

    # cached values
    ratings_count = IntegerField(null=True)
    inverse_popularity = FloatField(null=True)
    average_rating = IntegerField(null=True)

    @classmethod
    def get_by_id(self, m_id):
        if str(m_id) == m_id and m_id[0] == "m":
            m_id = m_id[1:]
        return Movie.get(Movie.movie_id == int(m_id))

    @classmethod
    def compute_inverse_popularity(cls, degree):
        return 1.0/(1 + degree)

    @classmethod
    def genre_attr(cls, attr):
        if not attr.startswith("genre_"):
            attr = "genre_%s" % attr
        return attr

    @classmethod
    def genre(cls, attr):
        """
        >>> Movie.genre("foo") == Movie.genre_foo
        True
        """
        return getattr(cls, cls.genre_attr(attr))

    def genres(self):
        return [g for g in GENRES if self.has_genre(g)]

    def has_genre(self, genre):
        return getattr(self, Movie.genre_attr(genre))

    def set_genres(self, genres):
        for g, v in zip(GENRES, genres):
            setattr(self, Movie.genre_attr(g), bool(int(v)))

    def post_import(self):
        count = 0
        ratings_sum = 0
        for r in self.ratings:
            count += 1
            ratings_sum += r.rating

        self.ratings_count = count
        self.inverse_popularity = Movie.compute_inverse_popularity(count)
        self.average_rating = ratings_sum/float(count)

    def raters(self):
        return (User.select()
                    .join(Rating, on=Rating.user)
                    .where(Rating.movie == self))

    def __eq__(self, other):
        return isinstance(other, Movie) and self.movie_id == other.movie_id

class User(BaseModel):
    user_id = IntegerField(unique=True, primary_key=True)
    age = IntegerField()
    gender = FixedCharField(max_length=1)
    occupation = CharField()
    zip_code = CharField()

    # cached/computed values
    ratings_count = IntegerField(null=True)
    city = CharField(null=True)
    state = CharField(null=True)
    first_rating_date = DateTimeField(null=True)
    # a JSON string associating each genre with the number of ratings
    # e.g. {"western": 42, ...}. Note that a movie can have multiple genres. In
    # that case we use a fraction (e.g. for two genres both get 0.5).
    genres_json = CharField(null=True)

    @classmethod
    def get_by_id(self, u_id):
        if str(u_id) == u_id and u_id[0] == "m":
            u_id = u_id[1:]
        return User.get(User.user_id == int(u_id))

    def post_import(self):
        count = 0
        first_rating_date = datetime.now()
        genres = defaultdict(float)
        for r in self.ratings:
            count += 1
            if r.date < first_rating_date:
                first_rating_date = r.date

            gs = r.movie.genres()
            if not gs:
                continue
            gs_count = float(len(gs))
            for g in gs:
                genres[g] += 1/gs_count

        self.genres_json = json.dumps(dict(genres))
        self.ratings_count = count
        self.first_rating_date = first_rating_date
        try:
            zipcode = zcdb[self.zip_code]
            self.city = zipcode.city
            self.state = zipcode.state
        except IndexError:
            # bad zipcodes
            pass

    def genres_ratings(self):
        return json.loads(self.genres_json)

    def movies(self):
        """
        Return all the movies rated by this user
        """
        return (Movie.select()
                    .join(Rating, on=Rating.movie)
                    .where(Rating.user == self))

    def __eq__(self, other):
        return isinstance(other, User) and self.user_id == other.user_id


class Rating(BaseModel):
    user = ForeignKeyField(User, related_name="ratings")
    movie = ForeignKeyField(Movie, related_name="ratings")
    rating = IntegerField()
    date = DateTimeField()

    def positive(self):
        return self.rating >= 3

    def negative(self):
        return self.rating < 3

    def __eq__(self, other):
        return self.user == other.user and \
                self.movie == other.movie and \
                self.date == other.date


class KeyValue(BaseModel):
    """
    KeyValue is a simple model to store key-value records in the database.
    Those are used to cache global stuff.
    """
    key = CharField(unique=True)
    value = CharField(null=True)


# Add genre_<genre> attributes on movies, e.g. genre_western
for g, name in GENRES.items():
    # http://stackoverflow.com/a/22365143/735926
    BooleanField(verbose_name=name).add_to_class(Movie, "genre_%s" % g)

def init_db():
    db.connect()
    db.create_tables([Movie, User, Rating, KeyValue], True)
