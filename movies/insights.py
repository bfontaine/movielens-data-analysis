# -*- coding: UTF-8 -*-

def minimal_movies_coverage(rg, t=0):
    """
    Return a minimal movies list such as all users in the dataset have seen at
    least one of them. ``t`` is the ratio to exclude. That is, if t=0.01, the
    returned coverage is for 99% of all users. t=0.5 returns a coverage for 50%
    of all users.

    This takes ~11 minutes to run.
    """
    movies = rg.movies()
    movies.sort(key=lambda m: len(rg.movie_fans(m)), reverse=True)
    users = set(rg.users())

    p = int(len(users) * t)

    def coverage(movies, users, cov):
        if len(users) <= p: #not users:
            return cov

        if not movies:
            # just to be sure we don't get this possibility
            return [0]*100

        m = movies[0]
        diff_users = users.difference(rg.movie_fans(m))

        made_a_diff = len(diff_users) != len(users)

        cov2 = cov + [m]

        without_m = coverage(movies[1:], diff_users, cov2)

        if not made_a_diff:
            return without_m

        with_m = coverage(movies[1:], diff_users, cov2)

        if len(with_m) < len(without_m):
            return with_m
        return without_m

    return coverage(movies, users, [])


def minimal_users_coverage(rg, t=0):
    """
    Return a minimal users list such as each movie from the dataset has been
    seen by at least one user from the list.
    """
    # TODO factor this code with the minimal_movies_coverage above
    users = rg.users()
    users.sort(key=lambda m: len(rg.user_movies(m)), reverse=True)
    movies = set(rg.movies())

    p = int(len(movies) * t)

    def coverage(users, movies, cov):
        if len(movies) <= p: #not movies:
            return cov

        if not users:
            # just to be sure we don't get this possibility
            return [0]*100

        m = users[0]
        diff_movies = movies.difference(rg.user_movies(m))

        made_a_diff = len(diff_movies) != len(movies)

        cov2 = cov + [m]

        without_m = coverage(users[1:], diff_movies, cov2)

        if not made_a_diff:
            return without_m

        with_m = coverage(users[1:], diff_movies, cov2)

        if len(with_m) < len(without_m):
            return with_m
        return without_m

    return coverage(users, movies, [])

def common_movies_fans(rg, t=0.1, min_fans=2):
    """
    Compute the common movie fans between each pair of movies. The result is a
    ratio of intersection/union, returned as a dict of dicts:
        movie -> movie -> ratio
    Ratios under ``t`` and movies with less than ``min_fans`` are removed.
    """
    movies = rg.movies()
    fans = {m: set(rg.movie_fans(m)) for m in movies}
    ratios = {}

    for i, m1 in enumerate(movies):
        f1 = fans[m1]
        if len(f1) < min_fans:
            continue

        rs = {}
        for m2 in movies[i+1:]:
            f2 = fans[m2]
            if len(f2) < min_fans:
                continue
            r = len(f1.intersection(f2))/float(len(f1.union(f2)))
            if r > t:
                rs[m2] = r

        if rs:
            ratios[m1] = rs

    return ratios
