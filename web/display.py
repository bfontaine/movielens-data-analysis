# -*- coding: UTF-8 -*-

import os.path
import sys

here = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, '%s/..' % here)

from movies.db import GENRES

def user(u):
    d = {
        "id": u.user_id,
        "number": u.user_id,
        "age": u.age,
        "ratings_count": u.ratings_count,
    }

    if u.gender == "M":
        d["gender"] = "male"
    elif u.gender == "F":
        d["gender"] = "female"

    if u.city and u.state:
        d["location"] = "%s, %s, USA" % (u.city, u.state)
    elif u.state:
        d["location"] = "%s, USA" % u.state

    # we might want to handle "unknown" & "others" differently. Let's hide them
    # for now
    if u.occupation and u.occupation not in ["unknown", "other"]:
        d["occupation"] = u.occupation

    return d

def users(us):
    return map(user, us)

def movie(m):
    d = {
        "id": m.movie_id,
        "title": m.title,
        "release_date": m.release_date,
        "video_release_date": m.video_release_date,
        "average_rating": m.average_rating,
        "ratings_count": m.ratings_count,
    }

    genres = m.genres()
    if genres:
        if "unknown" in genres:
            genres.delete("unknown")
        d["genres"] = genres

    return d

def movies(ms):
    return map(movie, ms)

def genre(g, movies):
    d = {
        "slug": g,
        "title": GENRES[g],
    }

    d["movies"] = [{
        "id": m.movie_id,
        "title": m.title,
        } for m in movies]

    d["movies_count"] = len(d["movies"])

    return d
