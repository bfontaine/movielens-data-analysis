# -*- coding: UTF-8 -*-

def user(u):
    d = {
        "id": u.user_id,
        "age": u.age,
        "ratings_count": u.ratings_count,
        "genres_json": u.genres_json,
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

def movie(m):
    d = {"id": m.movie_id}
    return d
