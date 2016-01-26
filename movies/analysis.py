# -*- coding: UTF-8 -*-

from collections import defaultdict
import networkx as nx
from .db import Rating, init_db

class RatingsGraph(object):

    def __init__(self):
        init_db()
        self.g = nx.Graph()
        for r in Rating.select().where(Rating.rating>=3):
            u_id = "u%d" % r.user_id
            m_id = "m%d" % r.movie_id

            self.g.add_node(u_id, bipartite=1)
            self.g.add_node(m_id, bipartite=0)
            self.g.add_edge(u_id, m_id)

    def users(self):
        """Return all the users"""
        return [n for n in self.g.nodes() if n.startswith("u")]

    def movies(self):
        """Return all the movies"""
        return [n for n in self.g.nodes() if n.startswith("m")]

    def movie_fans(self, m_id):
        """Return the users who positively rated a movie"""
        return self._neighbours(m_id)

    def user_movies(self, u_id):
        """Return the movies positively rated by an user"""
        return self._neighbours(u_id)

    def users_buddies(self, movies_threshold=20):
        """
        Return a graph of all users where an edge between two users means they
        have at least 20 movies in common. Users that aren't connected to
        anyone are not present in the resulting graph.
        """
        # user1 -> user2 -> number of common movies
        buddies = defaultdict(lambda: defaultdict(int))

        # This implementation doesn't support dynamic filtering (e.g. add an
        # edge between two users only if they share X% of their movies) but
        # runs in N*M (N users, M movies).

        for m in self.movies():
            fans = self.movie_fans(m)
            for i, f1 in enumerate(fans):
                for f2 in fans[i+1:]:
                    buddies[f1][f2] += 1

        g = nx.Graph()

        for u1, cofans in buddies.items():
            for u2, n in cofans.items():
                # skip people with less than <movies_threshold> common rated
                # movies
                if n < movies_threshold:
                    continue
                g.add_edge(u1, u2)

        return g


    def _neighbours(self, n):
        return self.g.edge.get(n, {}).keys()
