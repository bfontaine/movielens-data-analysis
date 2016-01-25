# -*- coding: UTF-8 -*-

from datetime import datetime
from .db import User, Movie, Rating, init_db, db

def log(s, verbose):
    if verbose:
        print "--> %s" % s

def import_data(directory, verbose=False):
    log("Initializing...", verbose)
    init_db()
    log("Importing movies...", verbose)
    import_movies("%s/u.item" % directory)
    log("Importing users...", verbose)
    import_users("%s/u.user" % directory)
    log("Importing ratings...", verbose)
    import_ratings("%s/u.data" % directory)
    log("Running post-import tasks...", verbose)
    post_import()

def fix_encoding(s):
    return s.decode("iso-8859-1").encode("utf8")

def import_movies(filename):
    with db.atomic():
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
    items = []
    with open(filename) as f:
        for line in f:
            u_id, age, gender, occupation, zip_code = \
                    fix_encoding(line).strip().split("|")
            items.append(dict(user_id=u_id, age=int(age), gender=gender,
                    occupation=occupation, zip_code=zip_code))

    chunked_insert(User, items)

def import_ratings(filename):
    """
    Import ratings from a file. Note that this can take a few minutes if the
    file is large (e.g. >40k lines)
    """
    items = []
    with open(filename) as f:
        for line in f:
            u_id, m_id, rating, ts = fix_encoding(line).strip().split("\t")
            items.append(dict(user=int(u_id), movie=int(m_id),
                    rating=int(rating), date=parse_ts(ts)))

    chunked_insert(Rating, items)

def post_import():
    for coll in [User, Movie]: #, Rating]:
        for el in coll.select():
            el.post_import()
            el.save()

def chunked_insert(model, items, chunk_size=150):
    # https://www.sqlite.org/limits.html#max_compound_select
    with db.atomic():
        for idx in range(0, len(items), chunk_size):
            model.insert_many(items[idx:idx+chunk_size]).execute()

def parse_date(s):
    # format: 01-Jan-1995
    return datetime.strptime(s, "%d-%b-%Y") if s else None

def parse_ts(s):
    # timestamp in secs
    return datetime.utcfromtimestamp(int(s))
