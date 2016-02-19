# -*- coding: UTF-8 -*-

from collections import defaultdict
import json
import networkx as nx
from .db import Movie, Rating, init_db
from .cache import Cache

cache = Cache()

@cache.memoize0()
def global_ratings_graph():
    return RatingsGraph()

class RatingsGraph(object):

    def __init__(self, nxgraph=None):
        if nxgraph is None:
            init_db()
            nxgraph = nx.Graph()
            for r in Rating.select().where(Rating.rating>=3):
                u_id = "u%d" % r.user_id
                m_id = "m%d" % r.movie_id

                nxgraph.add_node(u_id, bipartite=1)
                nxgraph.add_node(m_id, bipartite=0)
                nxgraph.add_edge(u_id, m_id)
        self.g = nxgraph
        self._cache = {}

    def users(self):
        """Return all the users"""
        return [n for n in self.g.nodes() if n.startswith("u")]

    def movies(self):
        """Return all the movies"""
        return [n for n in self.g.nodes() if n.startswith("m")]

    def movie_fans(self, m_id):
        """Return the users who positively rated a movie"""
        return self._neighbours(m_id)

    def movies_fans(self, m_ids):
        """Return the union of the fans of the given movies."""
        fans = set()
        for m_id in m_ids:
            for u in self.movie_fans(m_id):
                fans.add(u)

        return list(fans)

    def user_movies(self, u_id):
        """Return the movies positively rated by an user"""
        return self._neighbours(u_id)

    def users_movies(self, u_ids):
        """
        Return the union of the movies positively rated by the given users
        """
        movies = set()
        for u_id in u_ids:
            movies.update(self.user_movies(u_id))
        return list(movies)

    def ego_graph(self, u_id, distance=1, inverse_popularity_threshold=0,
            cache=True):
        """
        Return an ego-centered graph of distance ``distance`` for the user
        ``u_id``. The default distance is 1, which means the resulting graph is
        the user and the film they recommended. A distance of 2 means the user,
        the film they recommended, and the fans of these films. A distance of 3
        means the user, their films, the fans of these films as well as all
        other films recommended by these fans.

        ``inverse_popularity_threshold`` is the minimum inverse popularity we
        use to filter films. If the threshold is high it’ll exclude the most
        popular films in our dataset.
        """
        # allow simple caching
        if cache:
            key = "uid:%s/d:%d/ipt:%d" % (u_id, distance,
                    inverse_popularity_threshold)

            if key not in self._cache:
                self._cache[key] = self.ego_graph(u_id,
                        distance=distance,
                        inverse_popularity_threshold=inverse_popularity_threshold,
                        cache=False)

            return self._cache[key]

        if inverse_popularity_threshold > 0:
            t = inverse_popularity_threshold
            filter_movies = lambda ms: [m for m in ms
                    if Movie.get_by_id(m).inverse_popularity >= t]
        else:
            # no-op
            filter_movies = lambda ms: ms

        def compute_fans_movies():
            fans = set([u_id])
            movies = set()
            curr_dist = 1

            while curr_dist <= distance:
                # Use the movies liked by all the current fans
                movies.update(filter_movies(self.users_movies(fans)))

                if distance == curr_dist:
                    break

                curr_dist += 1

                # Use the fans of all the current movies
                fans.update(self.movies_fans(movies))

                if distance == curr_dist:
                    break

            return fans, movies

        fans, movies = compute_fans_movies()
        nodes = fans.union(movies)
        return RatingsGraph(self.g.subgraph(nodes))

    def users_buddies(self, buddy_threshold=0.46):
        """
        Return a graph of all users where an edge between two users means they
        have at least 20 movies in common. Users that aren't connected to
        anyone are not present in the resulting graph.

        ``buddy_threshold`` is the minimal score a dyad must have to be kept.
        The score is computed as the sum of the inverse popularity of each
        of the common movies.
        """
        # user1 -> user2 -> sum of inverse popularities of common movies
        buddies = defaultdict(lambda: defaultdict(int))

        # This implementation doesn't support dynamic filtering (e.g. add an
        # edge between two users only if they share X% of their movies) but
        # runs in N*N*M (N users, M movies).

        for m in self.movies():
            fans = self.movie_fans(m)
            degree = len(fans)
            for i, f1 in enumerate(fans):
                for f2 in fans[i+1:]:
                    buddies[f1][f2] += Movie.compute_inverse_popularity(degree)

        g = nx.Graph()

        for u1, cofans in buddies.items():
            for u2, score in cofans.items():
                # skip people with less than <movies_popularity_threshold>
                # common score
                if score < buddy_threshold:
                    continue
                g.add_edge(u1, u2, {"score": score})

        return g


    def user_movies_gatekeepers(self, u_id,
            gatekeepers_count=1,
            buddy_threshold=0.46, buddies=None):
        """
        For a given user return a ``dict`` mapping each one of their buddies to
        the movies they're the only one capable of recommending.

        It is recommended to pass the user's buddies (as computed by
        ``users_buddies``) to this method, otherwise it'll take a lot more time
        to compute. ``buddy_threshold`` is used only if ``buddies`` is not
        provided.

        For example with the configuration below the result would be
        ``{"u1": ["m1", "m2"], "u2": ["m4"]}``: ::

            ego -> m0
            u1  -> m0, m1, m2, m3
            u2  -> m0, m3, m4
            u3  -> m3

        ``u1`` and ``u2`` are ``ego``'s buddies. ``u1`` is the only one who
        recommended ``m1`` and ``m2``. ``u2`` is the only one who recommended
        ``m4``.

        ``gatekeepers_count`` is the maximum number of gatekeepers one can have
        for a given movie. The default is one, meaning that if two of one's
        buddies have seen the same movie they're not considered as gatekeepers.
        If only one of them has seen it then it's a gatekeeper. You can
        increase this number to have a less strict definition and thus more
        gatekeepers.
        """
        if buddies is None:
            b = self.users_buddies(buddy_threshold)
            buddies = b.edge[u_id].keys()

        gatekeepers = defaultdict(list)

        movies = self.user_movies(u_id)
        cofans = self.movies_fans(movies)

        for m in self.users_movies(cofans):
            gts = []
            n = 0
            for fan in self.movie_fans(m):
                if fan == u_id:
                    continue
                if fan not in cofans:
                    continue

                n += 1
                if n > gatekeepers_count:
                    gts = []
                    break

                gts.append(fan)

            for g in gts:
                gatekeepers[g].append(m)

        return dict(gatekeepers)

    def users_movies_gatekeepers(self,
            gatekeepers_count=1, buddy_threshold=0.46, buddies=None):
        """
        Return a ``dict`` mapping each user to its gatekeepers, similarly to
        what :meth:`user_movies_gatekeepers` returns for one user.
        """
        if buddies is None:
            buddies = self.users_buddies(buddy_threshold)

        return {u: self.user_movies_gatekeepers(u,
            gatekeepers_count=gatekeepers_count, buddies=buddies.edge[u])
                for u in buddies.node}

    def dump(self, filename):
        g = {n: ns.keys() for n, ns in self.g.edge.items()}
        with open(filename, "w") as f:
            f.write(json.dumps(g))


    def _neighbours(self, n):
        return self.g.edge.get(n, {}).keys()
