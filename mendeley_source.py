from __future__ import absolute_import

# need to get system mendeley library
from mendeley.exception import MendeleyException
import mendeley as mendeley_lib
import os
import datetime
from sqlalchemy.dialects.postgresql import JSONB
from collections import defaultdict

from app import db
from util import remove_punctuation

discipline_lookup = {
    u'Arts and Humanities': u'arts and humanities',
    u'Design': u'arts and humanities',
    u'Philosophy': u'arts and humanities',
    u'Agricultural and Biological Sciences': u'life science',
    u'Biochemistry, Genetics and Molecular Biology': u'life science',
    u'Immunology and Microbiology': u'life science',
    u'Veterinary Science and Veterinary Medicine': u'life science',
    u'Business, Management and Accounting': u'business',
    u'Decision Sciences': u'business',
    u'Economics, Econometrics and Finance': u'business',
    u'Chemistry': u'chemistry',
    u'Computer Science': u'computing',
    u'Chemical Engineering': u'engineering',
    u'Engineering': u'engineering',
    u'Materials Science': u'engineering',
    u'Earth and Planetary Sciences': u'environment',
    u'Energy': u'environment',
    u'Environmental Science': u'environment',
    u'Medicine and Dentistry': u'health',
    u'Nursing and Health Professions': u'health',
    u'Pharmacology, Toxicology and Pharmaceutical Science': u'health',
    u'Sports and Recreations': u'health',
    u'Mathematics': u'mathematics',
    u'Physics and Astronomy': u'physics and astronomy',
    u'Neuroscience': u'brain and mind',
    u'Psychology': u'brain and mind',
    u'Linguistics': u'social science',
    u'Social Sciences': u'social science',
    u'Unspecified': u'unspecified'
}

class MendeleyData(db.Model):
    id = db.Column(db.Text, primary_key=True)
    updated = db.Column(db.DateTime)
    api_raw = db.Column(JSONB)
    main_discipline = db.Column(db.Text)
    num_main_discipline = db.Column(db.Numeric)
    # num_unpaywall_events = db.Column(db.Numeric)
    # num_ced_events = db.Column(db.Numeric)
    # num_academic_ced_events = db.Column(db.Numeric)
    # num_nonacademic_ced_events = db.Column(db.Numeric)
    # is_open_access = db.Column(db.Boolean)
    # week = db.Column(db.Text)
    # ratio


    def __init__(self, **kwargs):
        self.updated = datetime.datetime.utcnow()
        super(MendeleyData, self).__init__(**kwargs)

    def run(self):
        self.updated = datetime.datetime.utcnow()
        self.api_raw = set_mendeley_data(self.id)
        self.num_main_discipline = 0
        self.main_discipline = None

        discipline_dict = defaultdict(int)
        if self.api_raw and "reader_count_by_subdiscipline" in self.api_raw:
            for discipline in self.api_raw["reader_count_by_subdiscipline"]:
                discipline_dict[discipline_lookup[discipline]] += self.api_raw["reader_count_by_subdiscipline"][discipline][discipline]
            for (discipline, num) in discipline_dict.iteritems():
                if num > self.num_main_discipline:
                    self.num_main_discipline = num
                    self.main_discipline = discipline

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

