from __future__ import absolute_import

# need to get system mendeley library
from mendeley.exception import MendeleyException
import mendeley as mendeley_lib
import os
import re
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
from util import clean_html

discipline_lookup = {
    u'Arts and Humanities': u'arts and humanities',
    u'Design': u'arts and humanities',
    u'Philosophy': u'arts and humanities',
    u'Agricultural and Biological Sciences': u'life science',
    u'Biochemistry, Genetics and Molecular Biology': u'life science',
    u'Immunology and Microbiology': u'life science',
    u'Veterinary Science and Veterinary Medicine': u'life science',
    u'Business, Management and Accounting': u'society',
    u'Decision Sciences': u'society',
    u'Economics, Econometrics and Finance': u'society',
    u'Chemistry': u'life science',
    u'Computer Science': u'technology',
    u'Chemical Engineering': u'life science',
    u'Engineering': u'technology',
    u'Materials Science': u'technology',
    u'Earth and Planetary Sciences': u'environment',
    u'Energy': u'environment',
    u'Environmental Science': u'environment',
    u'Medicine and Dentistry': u'health',
    u'Nursing and Health Professions': u'health',
    u'Pharmacology, Toxicology and Pharmaceutical Science': u'health',
    u'Sports and Recreations': u'health',
    u'Mathematics': u'technology',
    u'Physics and Astronomy': u'physics and astronomy',
    u'Neuroscience': u'brain and mind',
    u'Psychology': u'brain and mind',
    u'Linguistics': u'society',
    u'Social Sciences': u'society',
    u'Unspecified': u'unspecified'
}

class WeeklyStats(db.Model):
    id = db.Column(db.Text, primary_key=True)
    updated = db.Column(db.DateTime)
    mendeley_api_raw = db.Column(JSONB)
    oadoi_api_raw = db.Column(JSONB)
    pubmed_api_raw = db.Column(JSONB)
    sources = db.Column(JSONB)
    main_discipline = db.Column(db.Text)
    num_main_discipline = db.Column(db.Numeric)
    num_unpaywall_events = db.Column(db.Numeric)
    num_twitter_events = db.Column(db.Numeric)
    num_ced_events = db.Column(db.Numeric)
    num_academic_unpaywall_events = db.Column(db.Numeric)
    num_nonacademic_unpaywall_events = db.Column(db.Numeric)
    ratio_academic_unpaywall_events = db.Column(db.Numeric)
    is_open_access = db.Column(db.Boolean)
    abstract = db.Column(db.Text)
    week = db.Column(db.Numeric)


    def __init__(self, **kwargs):
        self.updated = datetime.datetime.utcnow()
        super(WeeklyStats, self).__init__(**kwargs)

    def set_sources(self):
        event_count_dict = defaultdict(int)

        ced_events = CedEvent.query.filter(CedEvent.doi==self.id).all()
        ced_events_this_week = [e for e in ced_events if e.week==self.week]
        for e in ced_events_this_week:
            event_count_dict[e.source_id] += 1

        unpaywall_events = UnpaywallEvent.query.filter(UnpaywallEvent.doi==self.id).all()
        unpaywall_events_this_week = [e for e in unpaywall_events if e.week==self.week]
        event_count_dict["unpaywall_views"] = len(unpaywall_events_this_week)
        event_count_dict["unpaywall_views_academic"] = len([e for e in unpaywall_events_this_week if e.is_academic_location])
        event_count_dict["unpaywall_views_nonacademic"] = len([e for e in unpaywall_events_this_week if not e.is_academic_location])

        sources = []
        for (source_id, num) in event_count_dict.iteritems():
            sources.append({
                "source_id": source_id,
                "event_count": num
            })
        self.sources = sources

    def get_event_count(self, source_id):
        try:
            return [s["event_count"] for s in self.sources if s["source_id"]==source_id][0]
        except IndexError:
            return 0

    # get abstracts
    def run(self):
        self.updated = datetime.datetime.utcnow()

        if not self.abstract:
            r = requests.get("http://doi.org/{}".format(self.id))
            text = r.text
            if u'</header>' in text:
                text_after_header = text.split("</header", 1)[1]
                text_after_p = text_after_header.split("																						<p>", 1)[1]
                clean_text = clean_html(text_after_p)
                print clean_text[0:1000]
                self.abstract = clean_text[0:1000]


    def run_other_things(self):
        self.updated = datetime.datetime.utcnow()

        url = "http://api.oadoi.org/v2/{}?email=paperbuzz@impactstory.org".format(self.id)
        r = requests.get(url)
        self.oadoi_api_raw = r.json()
        if self.oadoi_api_raw and "is_oa" in self.oadoi_api_raw:
            self.is_open_access = self.oadoi_api_raw["is_oa"]

        self.set_sources()
        self.num_twitter_events = self.get_event_count("twitter")

        self.num_unpaywall_events = self.get_event_count("unpaywall_views")
        self.num_academic_unpaywall_events = self.get_event_count("unpaywall_views_academic")
        self.num_nonacademic_unpaywall_events = self.get_event_count("unpaywall_views_nonacademic")
        if self.num_unpaywall_events:
            self.ratio_academic_unpaywall_events = float(self.num_academic_unpaywall_events)/self.num_unpaywall_events

        if self.mendeley_api_raw and self.mendeley_api_raw.get("abstract", None):
            self.abstract = self.mendeley_api_raw.get("abstract", None)
        else:
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={}[doi]&tool=paperbuzz&email=team@impactstory.org&retmode=json".format(self.id)
            print url
            r = requests.get(url)
            try:
                pmid = r.json()["esearchresult"]["idlist"][0]
            except (KeyError, IndexError):
                pmid = None

            if pmid:
                url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}&tool=paperbuzz&email=team@impactstory.org".format(pmid)
                print url
                r = requests.get(url)
                abstract_hits = re.findall(u'abstract.*?"(.*?)"', r.text.replace("\n", ""), re.MULTILINE)
                if abstract_hits:
                    self.abstract = abstract_hits[0]
                url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={}&retmode=json&tool=paperbuzz&email=team@impactstory.org".format(pmid)
                print url
                r = requests.get(url)
                self.pubmed_api_raw = r.json()["result"][pmid]


    def get_our_discipline(self, mendeley_discipline):
        schol_comm_title_words = [
            "reproducibility",
            "medical research",
            "open access",
            "open-access",
            "scientists",
            "medical literature",
            "journal",
            "grey literature",
            "gray literature",
            "researcher",
            "research funding",
            "peer review",
            "peer-review",
            "preprint",
            "academic",
            "altmetric",
            "google scholar",
            "bibliometrics",
            "data sharing",
            "data management"
        ]
        our_discipline = discipline_lookup[mendeley_discipline]
        if self.title:
            if our_discipline == "physics and astronomy":
                if "gender" in self.title.lower():
                    return "society"
                if "comput" in self.title.lower():
                    return "technology"
            for word in schol_comm_title_words:
                if word in self.title.lower():
                    return "scholarly communication"

        return our_discipline

    def run_disciplines(self):
        self.updated = datetime.datetime.utcnow()

        # if not mendeley data, call it
        if not self.mendeley_api_raw:
            self.mendeley_api_raw = set_mendeley_data(self.id)

        # if not there now, return
        if not self.mendeley_api_raw:
            return
        if not self.mendeley_api_raw.get("reader_count_by_subdiscipline", None):
            return

        self.num_main_discipline = 0
        self.main_discipline = None
        discipline_dict = defaultdict(int)
        for mendeley_discipline in self.mendeley_api_raw["reader_count_by_subdiscipline"]:
            our_discipline = self.get_our_discipline(mendeley_discipline)
            num_in_discipline = self.mendeley_api_raw["reader_count_by_subdiscipline"][mendeley_discipline][mendeley_discipline]
            discipline_dict[our_discipline] += num_in_discipline

        total_in_all_disciplines = 0
        for (our_discipline, num) in discipline_dict.iteritems():
            total_in_all_disciplines += num
            if num > self.num_main_discipline:
                self.num_main_discipline = num
                self.main_discipline = our_discipline

        if total_in_all_disciplines < 5:
            self.num_main_discipline = None
            self.main_discipline = None

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

    @property
    def display_abstract(self):
        if not self.abstract:
            return None
        abstract = self.abstract
        abstract = abstract.replace("<p>", " ")
        abstract = abstract.replace("</p>", " ")
        return abstract

    @property
    def title(self):
        if not self.oadoi_api_raw:
            return None
        return self.oadoi_api_raw.get("title", None)

    def to_dict_hotness(self):
        metadata_keys = ["year", "journal_name", "journal_authors", "title"]
        open_access_keys = ["best_oa_location", "is_oa", "journal_is_oa"]
        metadata = dict((k, v) for k, v in self.oadoi_api_raw.iteritems() if k in metadata_keys)
        metadata["abstract"] = self.display_abstract
        # also use other pubmed data here if no mendeley

        ret = {
            "doi": self.id,
            "metadata": metadata,
            "open_access": dict((k, v) for k, v in self.oadoi_api_raw.iteritems() if k in open_access_keys),
            "sources": self.sources,
            "debug": {}
        }

        if self.mendeley_api_raw:
            ret["debug"]["mendeley_disciplines"] = self.mendeley_api_raw["reader_count_by_subdiscipline"]

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

