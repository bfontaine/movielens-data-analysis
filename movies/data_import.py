# -*- coding: UTF-8 -*-

from collections import defaultdict
from datetime import datetime
from pyzipcode import ZipCodeDatabase

from .analysis import global_ratings_graph
from .db import User, Movie, Rating, UserLink, init_db, db

zcdb = ZipCodeDatabase()

def fix_encoding(s):
    return s.decode("iso-8859-1").encode("utf8")

def chunked_insert(model, items, chunk_size=150):
    """
    Insert a bunch of items in chunks to be faster than one-by-one.
    """
    # https://www.sqlite.org/limits.html#max_compound_select
    with db.atomic():
        for idx in range(0, len(items), chunk_size):
            model.insert_many(items[idx:idx+chunk_size]).execute()

def parse_ts(s):
    # timestamp in secs
    return datetime.utcfromtimestamp(int(s))

def create_user_links():
    """
    Store user links in the DB so that loading the graph can be fast. In
    practice loading all these users is not tremendously faster than
    re-computing the whole graph.
    """
    rg = global_ratings_graph()
    uids = rg.users()
    links = []
    for user in User.select():
        uid1 = "u%s" % user.user_id
        m1 = set(rg.user_movies(uid1))

        buddies = {}

        for uid2 in uids:
            if uid1 == uid2:
                continue

            m2 = set(rg.user_movies(uid2))

            intersection = m1.intersection(m2)
            if not intersection:
                continue

            union = m1.union(m2)

            buddies[uid2] = dict(
                # Jaccard index
                j=len(intersection)/float(len(union)),
                # Common movies count
                c=len(intersection),
            )

        links.append(dict(user=user, buddies=buddies))

    chunked_insert(UserLink, links)

class Importer(object):
    """
    A basic importer than doesn't do anything. Subclasses should implement the
    ``import_movies``, ``import_users``, ``import_ratings``, and
    ``post_import`` methods.
    """

    def __init__(self, directory, verbose=False):
        self.directory = directory
        self.verbose = verbose

    def log(self, s):
        if self.verbose:
            print "--> %s" % s

    def run(self):
        self.log("Initializing...")
        self.start()
        self.log("Importing movies...")
        self.import_movies()
        self.log("Importing users...")
        self.import_users()
        self.log("Importing ratings...")
        self.import_ratings()
        self.log("Running post-import tasks...")
        self.post_import()
        self.log("Creating user links...")
        create_user_links()

    def start(self):
        init_db()

    def import_movies(self): pass
    def import_users(self): pass
    def import_ratings(self): pass
    def post_import(self): pass

class Ml100kImporter(Importer):
    def parse_date(self, s):
        # format: 01-Jan-1995
        return datetime.strptime(s, "%d-%b-%Y") if s else None

    def import_movies(self):
        with db.atomic():
            with open("%s/u.item" % self.directory) as f:
                for line in f:
                    fields = fix_encoding(line).strip().split("|")
                    m_id, title, release, video, imdb = fields[:5]
                    genres = fields[5:]

                    m = Movie(movie_id=int(m_id), title=title,
                            release_date=self.parse_date(release),
                            video_date=self.parse_date(video), imdb_url=imdb)
                    m.set_genres(genres)
                    m.save(force_insert=True)

    def import_users(self):
        items = []
        with open("%s/u.user" % self.directory) as f:
            for line in f:
                u_id, age, gender, occupation, zip_code = \
                        fix_encoding(line).strip().split("|")

                item = dict(user_id=u_id, age=int(age), gender=gender,
                        occupation=occupation, zip_code=zip_code)

                try:
                    zipcode = zcdb[zip_code]
                    item["city"] = zipcode.city
                    item["state"] = zipcode.state
                except IndexError:
                    # bad zipcodes
                    item["city"] = None
                    item["state"] = None

                items.append(item)

        chunked_insert(User, items, 100)

    def import_ratings(self):
        """
        Note that this can take a few minutes if the
        file is large (e.g. >40k lines)
        """
        items = []
        with open("%s/u.data" % self.directory) as f:
            for line in f:
                u_id, m_id, rating, ts = fix_encoding(line).strip().split("\t")
                items.append(dict(user=int(u_id), movie=int(m_id),
                        rating=int(rating), date=parse_ts(ts)))

        chunked_insert(Rating, items)

    def post_import(self):
        for u in User.select():
            self.user_post_import(u)

        for m in Movie.select():
            self.movie_post_import(m)

    def movie_post_import(self, movie):
        count = 0
        ratings_sum = 0
        for r in movie.ratings:
            count += 1
            ratings_sum += r.rating

        movie.ratings_count = count
        movie.average_rating = ratings_sum/float(count)
        movie.save()

    def user_post_import(self, user):
        count = 0
        first_rating_date = datetime.now()
        genres = defaultdict(float)
        for r in user.ratings:
            count += 1
            if r.date < first_rating_date:
                first_rating_date = r.date

            gs = r.movie.genres()
            if not gs:
                continue
            gs_count = float(len(gs))
            for g in gs:
                genres[g] += 1/gs_count

        user.genres = dict(genres)
        user.ratings_count = count
        user.first_rating_date = first_rating_date
        user.save()


def import_data(directory, dataset_format, verbose=False):
    """
    Import data from a movielens dataset located in ``directory``.

    Supported formats:
        * ``ml-100k``: MovieLens 100k dataset
    """
    fmts = {
        "ml-100k": Ml100kImporter,
    }

    if dataset_format in fmts:
        fmts[dataset_format](directory, verbose=verbose).run()
    else:
        raise NotImplementedError("format '%s'" % dataset_format)
