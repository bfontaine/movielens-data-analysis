# -*- coding: UTF-8 -*-

import json
import pickle
from collections import defaultdict, OrderedDict

import peewee
from peewee import IntegerField, CharField, DateField, DateTimeField
from peewee import BooleanField, FixedCharField, ForeignKeyField, TextField
from playhouse.sqlite_ext import SqliteExtDatabase

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

class BaseModel(peewee.Model):
    class Meta:
        database = db

class JSONField(TextField):
    def db_value(self, value):
        return super(JSONField, self).db_value(json.dumps(value))

    def python_value(self, value):
        return json.loads(super(JSONField, self).python_value(value))

class OccupationField(CharField):
    """
    A text field that uniformize the occupation
    """

    # These are from the ml100k dataset
    _OCCUPATIONS = set((
        "administrator", "artist", "doctor", "educator", "engineer",
        "entertainment", "executive", "healthcare", "homemaker", "lawyer",
        "librarian", "marketing", "none", "other", "programmer", "retired",
        "salesman", "scientist", "student", "technician", "writer"))

    def _normalize(self, value):
        value = value.lower().strip()
        if value in OccupationField._OCCUPATIONS:
            return value

        for occupation in OccupationField._OCCUPATIONS:
            # e.g. "academic/educator" -> "educator"
            if (value.startswith(occupation + "/") or
                    value.endswith("/" + occupation)):
                return occupation

        # e.g. "k-12 student" -> "student"
        if value.endswith(" student"):
            return "student"

        # ml1m aliases
        aliases = {
            "doctor/health care": "healthcare",
            "administrator": "clerical/admin",
            "sales/marketing": "salesman",
            "unemployed": "none",
        }

        if value in aliases:
            return aliases[value]

        return "other"

    def db_value(self, value):
        return super(OccupationField, self).db_value(self._normalize(value))

class Movie(BaseModel):
    movie_id = IntegerField(unique=True, primary_key=True)
    title = CharField()
    # null=True because the dataset is not that clean
    release_date = DateField(null=True)
    video_release_date = DateField(null=True)
    # null=True because the IMDb URL is not included in some MovieLens datasets
    imdb_url = CharField(null=True)
    # null=True because the TMDb URL is available in the ml20m dataset only
    tmdb_url = CharField(null=True)

    # cached values
    ratings_count = IntegerField(null=True)
    average_rating = IntegerField(null=True)

    @classmethod
    def get_by_id(self, m_id):
        if str(m_id) == m_id and m_id[0] == "m":
            m_id = m_id[1:]
        return Movie.get(Movie.movie_id == int(m_id))

    # We use a `genre_xxx` boolean attribute for each genre and so have a bunch
    # of methods to access these attributes programmatically

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

    @classmethod
    def genres_distribution(cls):
        genres = defaultdict(int)
        total = 0.0
        for m in cls.select().execute():
            total += 1
            for g in m.genres():
                genres[g] += 1

        return {g: v/total for g, v in genres.items()}

    def genres(self):
        return [g for g in GENRES if self.has_genre(g)]

    def has_genre(self, genre):
        return getattr(self, Movie.genre_attr(genre))

    def set_genres(self, genres):
        for g, v in zip(GENRES, genres):
            setattr(self, Movie.genre_attr(g), bool(int(v)))

    def raters(self):
        return (User.select()
                    .join(Rating, on=Rating.user)
                    .where(Rating.movie == self))

    def __eq__(self, other):
        return isinstance(other, Movie) and self.movie_id == other.movie_id

class User(BaseModel):
    user_id = IntegerField(unique=True, primary_key=True)
    # Note that in the ml1m dataset (MovieLens 1M) the age denotes a range:
    #  1 = Under 18
    # 18 = 18-24
    # 25 = 25-34
    # 35 = 35-44
    # 45 = 45-49
    # 50 = 50-55
    # 56 = 56+
    age = IntegerField()
    gender = FixedCharField(max_length=1)
    occupation = OccupationField()
    zip_code = CharField(null=True)

    # cached/computed values
    ratings_count = IntegerField(null=True)
    city = CharField(null=True)
    state = CharField(null=True)
    first_rating_date = DateTimeField(null=True)
    # a JSON string associating each genre with the number of ratings
    # e.g. {"western": 42, ...}. Note that a movie can have multiple genres. In
    # that case we use a fraction (e.g. for two genres both get 0.5).
    genres = JSONField(default={})

    @classmethod
    def get_by_id(self, u_id):
        if str(u_id) == u_id and u_id[0] == "m":
            u_id = u_id[1:]
        return User.get(User.user_id == int(u_id))

    def genres_ratings(self):
        return json.loads(self.genres_json)

    def movies(self):
        """Return all the movies rated by this user"""
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

    class Meta:
        indexes = (
            # We have only one rating for each user/movie pair
            (("user", "movie"), True),
        )

    def __eq__(self, other):
        return self.user == other.user and \
                self.movie == other.movie and \
                self.date == other.date


class UserLink(BaseModel):
    """
    An user link to their "buddies" in the projected graph. This is used to
    cache the graph in the DB
    """
    user = ForeignKeyField(User, related_name="links")
    buddies = JSONField(default={})

class KeyValue(BaseModel):
    """
    KeyValue is a simple model to store key-value records in the database.
    Those are used by e.g. ``movies.cache.DBCache``.
    """
    key = CharField(unique=True)
    value = CharField(null=True)

    @classmethod
    def get_key(cls, key, default=None):
        """Retrieve a key, like the ``dict#get`` method."""
        try:
            return pickle.loads(cls.get(cls.key==key).value)
        except KeyValue.DoesNotExist:
            return default

    @classmethod
    def set_key(cls, key, value):
        """Set a key to an arbitrary value."""
        kv, _ = KeyValue.get_or_create(key=key)
        kv.value = pickle.dumps(value)
        kv.save()

    @classmethod
    def del_key(cls, key):
        """Permanently delete a key."""
        return cls.delete().where(cls.key==key).execute() > 0

    def del_key_prefix(cls, prefix):
        """
        Permanently delete all keys starting with the given prefix. An empty
        prefix deletes all the keys.
        """
        return cls.delete().where(cls.key.startswith(prefix)).execute() > 0


# Add genre_<genre> attributes on movies, e.g. genre_western
for g, name in GENRES.items():
    # http://stackoverflow.com/a/22365143/735926
    BooleanField(verbose_name=name).add_to_class(Movie, "genre_%s" % g)

def init_db():
    db.connect()
    db.create_tables([Movie, User, Rating, UserLink, KeyValue], True)
