# -*- coding: UTF-8 -*-

from datetime import datetime
from .db import User, Movie, Rating, init_db

def import_data(directory):
    init_db()
    import_movies("%s/u.item" % directory)
    import_users("%s/u.user" % directory)
    import_ratings("%s/u.data" % directory)

def fix_encoding(s):
    return s.decode("iso-8859-1").encode("utf8")

def import_movies(filename):
    with open(filename) as f:
        for line in f:
            fields = fix_encoding(line).split("|")
            m_id, title, release, video, imdb = fields[:5]
            genres = fields[5:]

            m = Movie(movie_id=int(m_id), title=title,
                    release_date=parse_date(release),
                    video_date=parse_date(video), imdb_url=imdb)
            m.set_genres(genres)
            m.save()

def import_users(filename):
    with open(filename) as f:
        for line in f:
            u_id, age, gender, occupation, zip_code = fix_encoding(line).split("|")
            u = User(user_id=u_id, age=int(age), gender=gender,
                    occupation=occupation, zip_code=zip_code)
            u.save()

def import_ratings(filename):
    with open(filename) as f:
        for line in f:
            u_id, m_id, rating, ts = fix_encoding(line).split("\t")
            # TODO

def parse_date(s):
    # format: 01-Jan-1995
    return datetime.now() # TODO
