import logging
import re
import time
import unicodedata

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import sqlalchemy
from sqlalchemy import exc, sql


class NoDoiException(Exception):
    pass


def clean_html(raw_html):
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext


def safe_commit(db):
    try:
        db.session.commit()
        return True
    except (KeyboardInterrupt, SystemExit):
        # let these ones through, don't save anything to db
        raise
    except sqlalchemy.exc.DataError:
        db.session.rollback()
        print("sqlalchemy.exc.DataError on commit.  rolling back.")
    except Exception:
        db.session.rollback()
        print("generic exception in commit.  rolling back.")
        logging.exception("commit error")
    return False


def is_doi_url(url):
    # test urls at https://regex101.com/r/yX5cK0/2
    p = re.compile(r"https?:\/\/(?:dx.)?doi.org\/(.*)")
    matches = re.findall(p, url.lower())
    if len(matches) > 0:
        return True
    return False


def clean_doi(dirty_doi):
    if not dirty_doi:
        raise NoDoiException("There's no DOI at all.")

    dirty_doi = remove_nonprinting_characters(dirty_doi)
    dirty_doi = dirty_doi.strip()
    dirty_doi = dirty_doi.lower()

    # test cases for this regex are at https://regex101.com/r/zS4hA0/1
    p = re.compile(r".*?(10.+)")

    matches = re.findall(p, dirty_doi)
    if len(matches) == 0:
        raise NoDoiException("There's no valid DOI.")

    match = matches[0]

    try:
        resp = str(match, "utf-8")  # unicode is valid in dois
    except (TypeError, UnicodeDecodeError):
        resp = match

    # remove any url fragments
    if "#" in resp:
        resp = resp.split("#")[0]

    return resp


def elapsed(since, round_places=2):
    return round(time.time() - since, round_places)


# from http://farmdev.com/talks/unicode/
def to_unicode_or_bust(obj, encoding="utf-8"):
    if isinstance(obj, str):
        if not isinstance(obj, str):
            obj = str(obj, encoding)
    return obj


def remove_nonprinting_characters(input, encoding="utf-8"):
    input_was_unicode = True
    if isinstance(input, str):
        if not isinstance(input, str):
            input_was_unicode = False

    unicode_input = to_unicode_or_bust(input)

    # see http://www.fileformat.info/info/unicode/category/index.htm
    char_classes_to_remove = ["C", "M", "Z"]

    response = "".join(
        c
        for c in unicode_input
        if unicodedata.category(c)[0] not in char_classes_to_remove
    )

    if not input_was_unicode:
        response = response.encode(encoding)

    return response


# getting a "decoding Unicode is not supported" error in this function?
# might need to reinstall libaries as per
# http://stackoverflow.com/questions/17092849/flask-login-typeerror-decoding-unicode-is-not-supported
class HTTPMethodOverrideMiddleware(object):
    allowed_methods = frozenset(
        ["GET", "HEAD", "POST", "DELETE", "PUT", "PATCH", "OPTIONS"]
    )
    bodyless_methods = frozenset(["GET", "HEAD", "OPTIONS", "DELETE"])

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        method = environ.get("HTTP_X_HTTP_METHOD_OVERRIDE", "").upper()
        if method in self.allowed_methods:
            method = method.encode("ascii", "replace")
            environ["REQUEST_METHOD"] = method
        if method in self.bodyless_methods:
            environ["CONTENT_LENGTH"] = "0"
        return self.app(environ, start_response)


def run_sql(db, q):
    q = q.strip()
    if not q:
        return
    print("running {}".format(q))
    start = time.time()
    try:
        con = db.engine.connect()
        trans = con.begin()
        con.execute(q)
        trans.commit()
    except exc.ProgrammingError as e:
        print("error {} in run_sql, continuting".format(e))
    finally:
        con.close()
    print("{} done in {} seconds".format(q, elapsed(start, 1)))


def get_sql_answer(db, q):
    row = db.engine.execute(sql.text(q)).first()
    return row[0]


def get_sql_answers(db, q):
    rows = db.engine.execute(sql.text(q)).fetchall()
    if not rows:
        return []
    return [row[0] for row in rows]


def get_multiple_authors(authors):
    parsed_authors = [author["name"] for author in authors]
    return ", ".join(set(parsed_authors))


def validate_author_url(author_url):
    if author_url and author_url.startswith("twitter://"):
        screen_name = re.findall("screen_name=([A-Za-z0-9_]{1,15}$)", author_url)[0]
        return "http://www.twitter.com/{}".format(screen_name)
    else:
        return author_url


def validate_subject_url(author_url, subject_url):
    if subject_url.startswith("twitter://"):
        screen_name = re.findall(r"twitter.com\/([A-Za-z0-9_]{1,15}$)", author_url)[0]
        status_id = re.findall(r"status\?id=(\d+$)", subject_url)[0]
        return "http://twitter.com/{}/statuses/{}".format(screen_name, status_id)
    else:
        return subject_url


def requests_retry_session(
    retries=3,
    backoff_factor=0.1,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
