from flask import Flask, render_template
from flask.ext.assets import Environment
from flask.ext.markdown import Markdown
from flask.ext.flatpages import FlatPages
from flask.ext.flatpages import pygments_style_defs
from flask_frozen import Freezer
from argh import *
import time

# Configuration
BASE_URL = "http://evenchick.com"
DEBUG = True                # enable debugging mode
FLATPAGES_AUTO_RELOAD = DEBUG   # prevent caching of pages
FLATPAGES_EXTENSION = ".md"
PAGE_DATE_FORMAT_STR = "%d-%m-%y"
DISPLAY_DATE_FORMAT_STR = "%d-%m-%y"
FREEZER_IGNORE_MIMETYPE_WARNINGS = True
FREEZER_DEFAULT_MIMETYPE = "text/html"

# Set up Flask
app = Flask(__name__)
app.config.from_object(__name__)

# Set up Flask extensions
assets = Environment(app)
markdown = Markdown(app)
pages = FlatPages(app)
freezer = Freezer(app)

# Helper functions
def get_pages_by_type(page_type):
    page_list = list(pages)
    matches = [p for p in page_list if p.meta.get('type') == page_type]
    return matches

# Flask Routing
@app.route("/")
def home():
    post_list = get_pages_by_type('post')
    latest = sorted(post_list, reverse=True, key=lambda p: p.meta['date'])
    return render_template("index.html", posts=latest[:5])

@app.route("/<path:path>/")
def page(path):
    page = pages.get_or_404(path)
    return render_template("page.html", page=page)

@app.route("/portfolio/")
def portfolio():
    portfolio_pages = get_pages_by_type('portfolio')
    date_sorted = sorted(portfolio_pages, reverse=True, key=lambda p: p.meta['date'])
    return render_template("portfolio.html", items=date_sorted)

@app.route('/pygments.css')
def pygments_css():
    return pygments_style_defs('tango'), 200, {'Content-Type': 'text/css'}


# URL Generators

@freezer.register_generator
def page_generator():
    for page in list(pages):
        yield "/" + str(page.path)

# CLI Commands
@command
def serve(server="127.0.0.1", port=8080, debug=DEBUG):
    """ Start a server to run the site
        default: 127.0.0.1:8080
    """
    app.run(host=server, port=port, debug=debug)


@command
def build():
    """ Generate a static version of the site
    """
    app.debug = False
    freezer.freeze()

if __name__ == "__main__":
    parser = ArghParser()
    parser.add_commands([serve, build])
    parser.dispatch()
