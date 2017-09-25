from __future__ import absolute_import

# need to get system mendeley library
from mendeley.exception import MendeleyException
import mendeley as mendeley_lib
import os
import datetime
from sqlalchemy.dialects.postgresql import JSONB
from collections import defaultdict
import requests

from app import db
from app import logger
from doi import Doi
from event import UnpaywallEvent
from event import CedEvent
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

class WeeklyStats(db.Model):
    id = db.Column(db.Text, primary_key=True)
    updated = db.Column(db.DateTime)
    mendeley_api_raw = db.Column(JSONB)
    oadoi_api_raw = db.Column(JSONB)
    sources = db.Column(JSONB)
    main_discipline = db.Column(db.Text)
    num_main_discipline = db.Column(db.Numeric)
    num_unpaywall_events = db.Column(db.Numeric)
    num_twitter_events = db.Column(db.Numeric)
    num_ced_events = db.Column(db.Numeric)
    num_academic_unpaywall_events = db.Column(db.Numeric)
    num_nonacademic_unpaywall_events = db.Column(db.Numeric)
    radio_academic_unpaywall_events = db.Column(db.Numeric)
    is_open_access = db.Column(db.Boolean)
    week = db.Column(db.Numeric)

    def __init__(self, **kwargs):
        self.updated = datetime.datetime.utcnow()
        super(WeeklyStats, self).__init__(**kwargs)

    def run(self):
        self.updated = datetime.datetime.utcnow()
        url = "http://api.oadoi.org/v2/{}?email=paperbuzz@impactstory.org".format(self.id)
        r = requests.get(url)
        self.oadoi_api_raw = r.json()
        if self.oadoi_api_raw and "is_oa" in self.oadoi_api_raw:
            self.is_open_access = self.oadoi_api_raw["is_oa"]

        ced_events = CedEvent.query.filter(CedEvent.doi==self.doi).all()

        self.num_twitter_events = 42

        unpaywall_events = UnpaywallEvent.query.filter(UnpaywallEvent.doi==self.doi).all()
        unpaywall_events_this_week = [e for e in unpaywall_events if e.week==37]

        self.num_unpaywall_events = len(unpaywall_events_this_week)
        self.num_academic_unpaywall_events = len([e for e in unpaywall_events if e.is_academic_location])
        self.num_nonacademic_unpaywall_events = len([e for e in unpaywall_events if not e.is_academic_location])
        if self.num_unpaywall_events:
            radio_academic_unpaywall_events = float(self.num_academic_unpaywall_events)/self.num_unpaywall_events

    def run_mendeley(self):
        self.updated = datetime.datetime.utcnow()
        self.mendeley_api_raw = set_mendeley_data(self.id)

        if not self.mendeley_api_raw:
            return
        if not self.mendeley_api_raw.get("reader_count_by_subdiscipline", None):
            return

        self.num_main_discipline = 0
        self.main_discipline = None
        discipline_dict = defaultdict(int)
        for discipline in self.mendeley_api_raw["reader_count_by_subdiscipline"]:
            discipline_dict[discipline_lookup[discipline]] += self.mendeley_api_raw["reader_count_by_subdiscipline"][discipline][discipline]
        for (discipline, num) in discipline_dict.iteritems():
            if num > self.num_main_discipline:
                self.num_main_discipline = num
                self.main_discipline = discipline
        logger.info(u"discipline for {} is {}={}".format(self.id, self.main_discipline, self.num_main_discipline))

    def sources_dicts_no_events(self):
        my_doi_obj = Doi(self.id)
        my_doi_obj.altmetrics.get()
        sources_dicts_with_events = my_doi_obj.altmetrics_dict_including_unpaywall_views()
        sources_dicts_without_events = []
        for sources_dict in sources_dicts_with_events["sources"]:
            sources_dict_new = sources_dict
            del sources_dict_new["events"]
            sources_dicts_without_events.append(sources_dict_new)
        return {"sources": sources_dicts_without_events}


    def to_dict_hotness(self):
        sources = [
            {
            "events": [],
            "events_count": self.num_ced_events,
            "events_count_by_day": [],
            "source_id": "twitter"
            },
            {
            "events": [],
            "events_count": 2*self.num_ced_events,
            "source_id": "unpaywall_views"
            }
            ]

        metadata_keys = ["year", "journal_name", "journal_authors", "title"]
        open_access_keys = ["best_oa_location", "is_oa", "journal_is_oa"]
        metadata = dict((k, v) for k, v in self.oadoi_api_raw.iteritems() if k in metadata_keys)
        if self.mendeley_api_raw:
            metadata["abstract"] = self.mendeley_api_raw.get("abstract", None)
        else:
            metadata["abstract"] = None

        ret = {
            "doi": self.id,
            "metadata": metadata,
            "open_access": dict((k, v) for k, v in self.oadoi_api_raw.iteritems() if k in open_access_keys),
            "sources": sources
        }
        return ret

    def __repr__(self):
        return u"<WeeklyStats ({}, {}={})>".format(self.id, self.main_discipline, self.num_main_discipline)


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

