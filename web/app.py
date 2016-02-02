# -*- coding: UTF-8 -*-

import os
import sys
import os.path
import sass
from flask import Flask, render_template
from flask.ext.assets import Environment, Bundle
from webassets.filter import register_filter
from webassets_browserify import Browserify

here = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, '%s/..' % here)

from movies.analysis import RatingsGraph

# construct this only once
print "Loading..."
ratings_graph = RatingsGraph()

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

@app.route("/")
def home():
    return render_template("home.html", ratings=ratings_graph)

if __name__ == '__main__':
    app.run()
