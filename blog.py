from flask import Flask, render_template
from flask.ext.assets import Environment
from flask.ext.markdown import Markdown
from flask.ext.flatpages import FlatPages
from flask.ext.flatpages import pygments_style_defs
from flask_frozen import Freezer
from argh import *


# Configuration
BASE_URL = "http://wwww.gorysko.com"
DEBUG = True                # enable debugging mode
FLATPAGES_AUTO_RELOAD = DEBUG   # prevent caching of pages
FLATPAGES_EXTENSION = ".md"
PAGE_DATE_FORMAT_STR = "%d-%m-%y"
DISPLAY_DATE_FORMAT_STR = "%d-%m-%y"
FREEZER_IGNORE_MIMETYPE_WARNINGS = True
FREEZER_DEFAULT_MIMETYPE = "text/html"

# Set up Flask
APP = Flask(__name__)
APP.config.from_object(__name__)

# Set up Flask extensions
ASSETS = Environment(APP)
MARKDOWN = Markdown(APP)
PAGES = FlatPages(APP)
FREEZER = Freezer(APP)

# Helper functions
def get_pages_by_type(page_type):
    """Gets page path."""
    page_list = list(PAGES)
    matches = [source for source in page_list \
                if source.meta.get('type') == page_type]
    return matches

# Flask Routing
@APP.route("/")
def home():
    """Renders home page."""
    post_list = get_pages_by_type('post')
    latest = sorted(post_list, reverse=True, key=lambda p: p.meta['date'])
    return render_template("index.html", posts=latest[:5])

@APP.route("/<path:path>/")
def page(path):
    """Renders page."""
    source = PAGES.get_or_404(path)
    return render_template("page.html", page=source)

@APP.route("/portfolio/")
def portfolio():
    """Renders portfolio page"""
    portfolio_pages = get_pages_by_type('portfolio')
    date_sorted = sorted(portfolio_pages, reverse=True,
                         key=lambda p: p.meta['date'])
    return render_template("portfolio.html", items=date_sorted)

@APP.route('/pygments.css')
def pygments_css():
    """Renders css."""
    return pygments_style_defs('tango'), 200, {'Content-Type': 'text/css'}


# URL Generators

@FREEZER.register_generator
def page_generator():
    """Generaes page."""
    for source in list(PAGES):
        yield ("/%s" % str(source.path))

# CLI Commands
@command
def serve(server="127.0.0.1", port=8080, debug=DEBUG):
    """ Start a server to run the site
        default: 127.0.0.1:8080
    """
    APP.run(host=server, port=port, debug=debug)


@command
def build():
    """ Generate a static version of the site
    """
    APP.debug = False
    FREEZER.freeze()

if __name__ == "__main__":
    parser = ArghParser()
    parser.add_commands([serve, build])
    parser.dispatch()
