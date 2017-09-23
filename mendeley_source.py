from __future__ import absolute_import

# need to get system mendeley library
from mendeley.exception import MendeleyException
import mendeley as mendeley_lib
import os
import datetime
from sqlalchemy.dialects.postgresql import JSONB

from app import db
from util import remove_punctuation

class MendeleyData(db.Model):
    id = db.Column(db.Text, primary_key=True)
    updated = db.Column(db.DateTime)
    api_raw = db.Column(JSONB)

    def __init__(self, **kwargs):
        self.updated = datetime.datetime.utcnow()
        super(MendeleyData, self).__init__(**kwargs)

    def run(self):
        self.api_raw = set_mendeley_data(self.id)

    def __repr__(self):
        return u"<MendeleyData ({})>".format(self.id)


def get_mendeley_session():
    mendeley_client = mendeley_lib.Mendeley(
        client_id=os.getenv("MENDELEY_OAUTH2_CLIENT_ID"),
        client_secret=os.getenv("MENDELEY_OAUTH2_SECRET"))
    auth = mendeley_client.start_client_credentials_flow()
    session = auth.authenticate()
    return session

def set_mendeley_data(doi):

    resp = None
    doc = None

    try:
        mendeley_session = get_mendeley_session()
        method = "doi"
        try:
            doc = mendeley_session.catalog.by_identifier(
                    doi=doi,
                    view='stats')
        except (UnicodeEncodeError, IndexError):
            return None

        if not doc:
            return None

        # print u"\nMatch! got the mendeley paper! for title {}".format(biblio_title)
        # print "got mendeley for {} using {}".format(product.id, method)
        resp = {}
        resp["reader_count"] = doc.reader_count
        resp["reader_count_by_academic_status"] = doc.reader_count_by_academic_status
        resp["reader_count_by_subdiscipline"] = doc.reader_count_by_subdiscipline
        resp["reader_count_by_country"] = doc.reader_count_by_country
        resp["mendeley_url"] = doc.link
        resp["abstract"] = doc.abstract
        resp["method"] = method

    except (KeyError, MendeleyException):
        pass

    return resp

