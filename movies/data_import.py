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
            fields = fix_encoding(line).strip().split("|")
            m_id, title, release, video, imdb = fields[:5]
            genres = fields[5:]

            m = Movie(movie_id=int(m_id), title=title,
                    release_date=parse_date(release),
                    video_date=parse_date(video), imdb_url=imdb)
            m.set_genres(genres)
            m.save(force_insert=True)

def import_users(filename):
    with open(filename) as f:
        for line in f:
            u_id, age, gender, occupation, zip_code = \
                    fix_encoding(line).strip().split("|")
            User.create(user_id=u_id, age=int(age), gender=gender,
                    occupation=occupation, zip_code=zip_code)

def import_ratings(filename):
    """
    Import ratings from a file. Note that this can take a few minutes if the
    file is large (e.g. >40k lines)
    """
    with open(filename) as f:
        for line in f:
            u_id, m_id, rating, ts = fix_encoding(line).strip().split("\t")
            Rating.create(user=int(u_id), movie=int(m_id),
                    rating=int(rating), date=parse_ts(ts))

def parse_date(s):
    # format: 01-Jan-1995
    return datetime.strptime(s, "%d-%b-%Y") if s else None

def parse_ts(s):
    # timestamp in secs
    return datetime.utcfromtimestamp(int(s))
