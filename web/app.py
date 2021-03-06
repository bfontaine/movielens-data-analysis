# -*- coding: UTF-8 -*-

import os
import sys
import os.path
import sass
from flask import Flask, render_template, abort
from flask.ext.assets import Environment, Bundle
from webassets.filter import register_filter
from webassets_browserify import Browserify

here = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, '%s/..' % here)

from movies.db import Movie, User, GENRES

import display

sass_path = os.path.join(here, "static", "style")

os.environ["BROWSERIFY_BIN"] = "%s/node_modules/browserify/bin/cmd.js" % here

register_filter(Browserify)

def scss(_in, out, **kw):
    """sass compilation"""
    out.write(sass.compile(string=_in.read(), include_paths=(sass_path,)))

app = Flask(__name__)
app.debug=True

assets = Environment(app)
assets.register(
    "css_all",
    Bundle(
        "vendor/bootstrap.min.css",
        "style/main.scss",
        filters=(scss,),
        output="main.css",

        # this is necessary because we use @import statements in the SCSS. Note
        # that it disables caching.
        depends=('style/**/*.scss'),
    ))

# for each of these strings,
# 1. take js/<string>.js (replacing underscores with hyphens)
# 2. compile it in <string>.js (same)
# 3. register as "js_<string>"
#
# e.g. interview:
#     assets.register(
#         "js_interview",
#         Bundle(
#           "js/interview.js",
#           output="interview.js",
#           ...))
#
for js in ["home"]:
    target = "%s.js" % js.replace("_", "-")
    source = "js/%s" % target

    assets.register(
        "js_%s" % js,
        Bundle(
            source,
            filters="browserify",
            output=target,
            depends=('js/**/*.js')))

@app.route("/u/<uid>")
def user_page(uid):
    try:
        user = User.get_by_id(uid)
    except User.DoesNotExist:
        abort(404)
    return render_template("user.html",
            user=display.user(user),
            movies=display.movies(sorted(user.movies(), key=lambda m: m.movie_id)),
            genres=GENRES)

@app.route("/m/<mid>")
def movie_page(mid):
    try:
        movie = Movie.get_by_id(mid)
    except Movie.DoesNotExist:
        abort(404)
    return render_template("movie.html",
            movie=display.movie(movie),
            users=display.users(sorted(movie.raters(), key=lambda u: u.user_id)),
            genres=GENRES)

@app.route("/g/<genre>")
def genre_page(genre):
    genre = genre.lower()
    if genre not in GENRES:
        abort(404)

    movies = Movie.select().where(Movie.genre(genre) == True)
    return render_template("genre.html", genre=display.genre(genre, movies))

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == '__main__':
    app.run()
