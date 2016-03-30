# -*- coding: UTF-8 -*-

from datetime import datetime
from pyzipcode import ZipCodeDatabase

from .analysis import global_ratings_graph
from .db import User, Movie, Rating, UserLink, init_db, db

zcdb = ZipCodeDatabase()

def set_user_dict_city(item):
    try:
        zipcode = zcdb[item["zip_code"]]
        item["city"] = zipcode.city
        item["state"] = zipcode.state
    except IndexError:
        # bad zipcodes
        item["city"] = None
        item["state"] = None

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

def create_user_links(verbose=False):
    """
    Store user links in the DB so that loading the graph can be fast.

    On the ml-100k dataset loading all these users is not tremendously faster
    than re-computing the whole graph.

    On the ml-1m dataset this adds a lot of data in the DB; growing it from
    ~130MB to >1.6GB. It also takes a lot of time (>30m) and uses a lot of RAM
    (>10GB); I never waited until it finishes.
    """
    rg = global_ratings_graph()
    if verbose:
        print "Ratings graph loaded."
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
        create_user_links(verbose=self.verbose)

    def start(self):
        init_db()

    def import_movies(self): pass
    def import_users(self): pass
    def import_ratings(self): pass

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
        if count > 0:
            movie.average_rating = ratings_sum/float(count)
        movie.save()

    def user_post_import(self, user):
        count = 0
        first_rating_date = datetime.now()
        for r in user.ratings:
            count += 1
            if r.date < first_rating_date:
                first_rating_date = r.date

        user.ratings_count = count
        user.first_rating_date = first_rating_date
        user.save()


class MlImporter(Importer):
    """Common parent class for MovieLens importers"""

    def movies_filename(self):
        """
        This should be overridden by children classes to return the filename
        to use to read movies.
        """
        pass

    def users_filename(self):
        """
        This should be overridden by children classes to return the filename
        to use to read users.
        """
        pass

    def ratings_filename(self):
        """
        This should be overridden by children classes to return the filename
        to use to read ratings.
        """
        pass

    def parse_movie(self, line):
        """
        This should be overridden by children classes to parse a movie from a
        line and return it.
        """
        pass

    def parse_user_dict(self, line):
        """
        This should be overridden by children classes to parse an user from a
        line and return it as a dict.
        """
        pass

    def parse_rating_dict(self, line):
        """
        This should be overridden by children classes to parse a rating from a
        line and return it as a dict.
        """
        pass

    def import_movies(self):
        with db.atomic():
            with open(self.movies_filename()) as f:
                for line in f:
                    line = fix_encoding(line).strip()
                    m = self.parse_movie(line)
                    m.save(force_insert=True)

    def import_users(self):
        items = []
        with open(self.users_filename()) as f:
            for line in f:
                line = fix_encoding(line).strip()
                item = self.parse_user_dict(line)

                if "zip_code" in item:
                    set_user_dict_city(item)
                items.append(item)

        chunked_insert(User, items, 100)

    def import_ratings(self):
        items = []
        with open(self.ratings_filename()) as f:
            for line in f:
                line = fix_encoding(line).strip()
                item = self.parse_rating_dict(line)
                items.append(item)

        chunked_insert(Rating, items)


class Ml100kImporter(MlImporter):
    """An importer for the ml-100k dataset"""

    def parse_date(self, s):
        # format: 01-Jan-1995
        return datetime.strptime(s, "%d-%b-%Y") if s else None

    def movies_filename(self): return "%s/u.item" % self.directory
    def users_filename(self): return "%s/u.user" % self.directory
    def ratings_filename(self): return "%s/u.data" % self.directory

    def parse_movie(self, line):
        fields = line.split("|")
        m_id, title, release, video, imdb = fields[:5]
        genres = fields[5:]

        m = Movie(movie_id=int(m_id), title=title,
                release_date=self.parse_date(release),
                video_date=self.parse_date(video), imdb_url=imdb)
        m.set_genres(genres)
        return m

    def parse_user_dict(self, line):
        u_id, age, gender, occupation, zip_code = line.split("|")
        return dict(user_id=u_id, age=int(age), gender=gender,
                occupation=occupation, zip_code=zip_code)

    def parse_rating_dict(self, line):
        u_id, m_id, rating, ts = line.split("\t")
        return dict(user=int(u_id), movie=int(m_id), rating=int(rating),
                date=parse_ts(ts))


class Ml1mImporter(MlImporter):
    """An importer for the ml-1m dataset"""

    # From the README (also included in the archive)
    # http://files.grouplens.org/datasets/movielens/ml-1m-README.txt
    occupations = {
        0:  "other",
        1:  "academic/educator",
        2:  "artist",
        3:  "clerical/admin",
        4:  "college/grad student",
        5:  "customer service",
        6:  "doctor/health care",
        7:  "executive/managerial",
        8:  "farmer",
        9:  "homemaker",
        10:  "K-12 student",
        11:  "lawyer",
        12:  "programmer",
        13:  "retired",
        14:  "sales/marketing",
        15:  "scientist",
        16:  "self-employed",
        17:  "technician/engineer",
        18:  "tradesman/craftsman",
        19:  "unemployed",
        20:  "writer",
    }

    def movies_filename(self): return "%s/movies.dat" % self.directory
    def users_filename(self): return "%s/users.dat" % self.directory
    def ratings_filename(self): return "%s/ratings.dat" % self.directory

    def parse_movie(self, line):
        fields = line.split("::")
        m_id, title, genres = fields[:3]
        genres = genres.split("|")

        m = Movie(movie_id=int(m_id), title=title)
        m.set_genres(genres)
        return m

    def parse_user_dict(self, line):
        u_id, gender, age, occupation, zip_code = \
                fix_encoding(line).strip().split("::")

        return dict(user_id=u_id, age=int(age), gender=gender,
                occupation=Ml1mImporter.occupations.get(occupation,
                    "other"), zip_code=zip_code)

    def parse_rating_dict(self, line):
        u_id, m_id, rating, ts = line.split("::")
        return dict(user=int(u_id), movie=int(m_id), rating=float(rating),
                date=parse_ts(ts))

class Ml10mImporter(Ml1mImporter):
    """An importer for the ml-10m dataset"""

    # There are no user info in this dataset, so we extract the user ids from
    # the ratings file
    def import_users(self):
        users = {}

        with open(self.ratings_filename()) as f:
            for line in f:
                u_id, _ = fix_encoding(line).strip().split("::", 1)
                users[u_id] = dict(user_id=u_id)

        chunked_insert(User, users.values(), 100)
