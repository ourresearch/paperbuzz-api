from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_compress import Compress
from flask_debugtoolbar import DebugToolbarExtension

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sqlalchemy.pool import NullPool

import logging
import sys
import os
import requests

HEROKU_APP_NAME = "paperbuzz-api"

# set up logging
# see http://wiki.pylonshq.com/display/pylonscookbook/Alternative+logging+configuration
logging.basicConfig(
    stream=sys.stdout, level=logging.DEBUG, format="%(name)s - %(message)s"
)
logger = logging.getLogger("paperbuzz")

libraries_to_mum = [
    "requests.packages.urllib3",
    "requests_oauthlib",
    "stripe",
    "oauthlib",
    "boto",
    "newrelic",
    "RateLimiter",
]

for a_library in libraries_to_mum:
    the_logger = logging.getLogger(a_library)
    the_logger.setLevel(logging.WARNING)
    the_logger.propagate = True

requests.packages.urllib3.disable_warnings()

# error reporting with sentry
# sentry_sdk.init(dsn=os.environ.get("SENTRY_DSN"), integrations=[FlaskIntegration()])

app = Flask(__name__)


# database stuff
app.config[
    "SQLALCHEMY_TRACK_MODIFICATIONS"
] = True  # as instructed, to suppress warning
db_uri = os.getenv("DATABASE_URL")
if db_uri.startswith("postgres://"):
    db_uri = db_uri.replace(
        "postgres://", "postgresql://", 1
    )  # temp heroku sqlalchemy fix
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_ECHO"] = os.getenv("SQLALCHEMY_ECHO", False) == "True"


# from http://stackoverflow.com/a/12417346/596939
class NullPoolSQLAlchemy(SQLAlchemy):
    def apply_driver_hacks(self, app, info, options):
        options["poolclass"] = NullPool
        return super(NullPoolSQLAlchemy, self).apply_driver_hacks(app, info, options)


db = NullPoolSQLAlchemy(app)

# do compression.  has to be above flask debug toolbar so it can override this.
compress_json = os.getenv("COMPRESS_DEBUG", "False") == "True"


# set up Flask-DebugToolbar
if os.getenv("FLASK_DEBUG", False) == "True":
    logger.info("Setting app.debug=True; Flask-DebugToolbar will display")
    compress_json = False
    app.debug = True
    app.config["DEBUG"] = True
    app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
    app.config["SQLALCHEMY_RECORD_QUERIES"] = True
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    toolbar = DebugToolbarExtension(app)

# gzip responses
Compress(app)
app.config["COMPRESS_DEBUG"] = compress_json
