# need to get system mendeley library
from mendeley.exception import MendeleyException
import mendeley as mendeley_lib
import os
import re
import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import deferred
from collections import defaultdict
import requests

from app import db
from app import logger
from doi import Doi
from event import CedEvent
from util import clean_html

discipline_lookup = {
    "Arts and Humanities": "arts and humanities",
    "Design": "arts and humanities",
    "Philosophy": "arts and humanities",
    "Agricultural and Biological Sciences": "life science",
    "Biochemistry, Genetics and Molecular Biology": "life science",
    "Immunology and Microbiology": "life science",
    "Veterinary Science and Veterinary Medicine": "life science",
    "Business, Management and Accounting": "society",
    "Decision Sciences": "society",
    "Economics, Econometrics and Finance": "society",
    "Chemistry": "life science",
    "Computer Science": "technology",
    "Chemical Engineering": "life science",
    "Engineering": "technology",
    "Materials Science": "technology",
    "Earth and Planetary Sciences": "environment",
    "Energy": "environment",
    "Environmental Science": "environment",
    "Medicine and Dentistry": "health",
    "Nursing and Health Professions": "health",
    "Pharmacology, Toxicology and Pharmaceutical Science": "health",
    "Sports and Recreations": "health",
    "Mathematics": "technology",
    "Physics and Astronomy": "physics and astronomy",
    "Neuroscience": "brain and mind",
    "Psychology": "brain and mind",
    "Linguistics": "society",
    "Social Sciences": "society",
    "Unspecified": "unspecified",
}

discipline_overrides = {
    "10.1016/j.joi.2017.08.007": "scholarly communication",
    "10.1038/549023a": "scholarly communication",
    "10.1038/549018a": "scholarly communication",
}

photos = {
    "10.1080/01436597.2017.1369037": "https://i.imgur.com/AZ8g46k.png",
    "10.1136/bmj.j4030": "https://i.imgur.com/xLLK0do.png",
    "10.1038/s41564-017-0012-7": "https://i.imgur.com/6InNONL.png",
    "10.1038/549133a": "https://i.imgur.com/cUQU6lO.png",
    "10.7717/peerj.1262": "https://i.imgur.com/sZmOngy.png",
    "10.1038/nature.2017.22580": "https://i.imgur.com/koJ22Wk.png",
    "10.1002/leap.1116": "https://i.imgur.com/cGKRXJl.png",
    "10.1038/nrg.2017.65": "https://i.imgur.com/uie4fum.png",
    "10.1038/549149a": "https://i.imgur.com/qgjZes4.png",
    "10.1038/s41598-017-11721-z": "https://i.imgur.com/j9Pqfuo.png",
    "10.1056/nejmp1711886": "https://i.imgur.com/407Jcs9.png",
    "10.1371/journal.pbio.2002173": "https://i.imgur.com/KZs41pQ.png",
    "10.1038/nature23878": "https://i.imgur.com/oXpam6C.png",
    "10.1016/j.cub.2014.03.022": "https://i.imgur.com/nl1gNRa.png",
    "10.1057/palcomms.2017.93": "https://i.imgur.com/08ChMe2.png",
    "10.1056/nejmoa1708337": "https://i.imgur.com/229NN3r.png",
    "10.1056/nejmoa1705915": "https://i.imgur.com/5C4q3nz.png",
    "10.1056/nejmoa1709684": "https://i.imgur.com/OvzqLLp.png",
    "10.1038/nature23879": "https://i.imgur.com/1UpBCgZ.png",
    "10.1038/nphys4254": "https://i.imgur.com/YIh9ngF.png",
    "10.1038/nclimate3382": "https://i.imgur.com/uQe4Hmj.png",
    "10.1371/journal.pone.0183967": "https://i.imgur.com/6GRL9fe.png",
    "10.1056/nejmra1608969": "https://i.imgur.com/pOjQfkC.png",
    "10.1038/s41467-017-00109-2": "https://i.imgur.com/T86Ls2t.png",
    "10.1038/s41559-017-0305-5": "https://i.imgur.com/CCqEXtd.png",
    "10.3389/feduc.2017.00037": "https://i.imgur.com/BQgDZBc.png",
    "10.1111/dar.12596": "https://i.imgur.com/z93iJAn.png",
    "10.1038/s41562-017-0195-1": "https://i.imgur.com/QbZPG7z.png",
    "10.1038/nn.4637": "https://i.imgur.com/yBkSSOD.png",
    "10.1007/s00704-015-1597-5": "https://i.imgur.com/IFUxkcz.png",
    "10.1007/s10899-009-9174-4": "https://i.imgur.com/pi4ych8.png",
    "10.1038/ijo.2017.220": "https://i.imgur.com/SrhhXtA.png",
    "10.1007/s10584-017-1978-0": "https://i.imgur.com/4tdNWou.png",
    "10.1038/s41598-017-10675-6": "https://i.imgur.com/c2UqUBX.png",
    "10.1002/ajpa.23308": "https://i.imgur.com/qh3UcfN.png",
    "10.1038/s41598-017-09250-w": "https://i.imgur.com/UpD1XtU.png",
    "10.1136/bmj.38705.470590.55": "https://i.imgur.com/Yeggq6e.png",
    "10.3758/s13423-017-1343-3": "https://i.imgur.com/zMsWBPA.png",
    "10.1016/s0140-6736(17)32336-x": "https://i.imgur.com/75SzNhQ.png",
    "10.1038/s41598-017-12055-6": "https://i.imgur.com/yTyqbyV.png",
    "10.3389/fnhum.2016.00511": "https://i.imgur.com/7XwVvrS.png",
    "10.1136/bmj.311.7021.1668": "https://i.imgur.com/4npP5VA.png",
    "10.1038/nature23651": "https://i.imgur.com/xH84ajU.png",
    "10.1371/journal.pone.0181970": "https://i.imgur.com/rWussar.png",
    "10.1088/1748-9326/aa815f": "https://i.imgur.com/f6TzWVi.png",
    "10.1038/nature23681": "https://i.imgur.com/cUICqNA.png",
    "10.1103/physrevlett.116.061102": "https://i.imgur.com/vKiKVCy.png",
    "10.1016/j.joi.2017.08.007": "https://i.imgur.com/z6RP6TN.png",
    "10.1103/physrevlett.119.110501": "https://i.imgur.com/1ZTBiUE.png",
    "10.1038/nature23459": "https://i.imgur.com/gC7oDpy.png",
    "10.1103/physreve.96.030101": "https://i.imgur.com/VAb0Wjj.png",
    "10.1038/s41562-017-0082": "https://i.imgur.com/tVs9ONj.png",
    "10.1136/bmjopen-2017-016942": "https://i.imgur.com/yWOubE3.png",
    "10.1038/s41598-017-07948-5": "https://i.imgur.com/uGGxpWZ.png",
    "10.1007/978-3-319-67389-9_7": "https://i.imgur.com/e8eVWrE.png",
    "10.1038/ngeo3017": "https://i.imgur.com/1bEyVeX.png",
    "10.1016/s0140-6736(17)32152-9": "https://i.imgur.com/qd8NenR.png",
    "10.1038/s41598-017-09429-1": "https://i.imgur.com/6GHoU5b.png",
    "10.1038/s41467-017-00378-x": "https://i.imgur.com/fyQMWrM.png",
    "10.1038/srep00754": "https://i.imgur.com/9IRFQGh.png",
    "10.1093/afraf/adw030": "https://i.imgur.com/7F1ngrs.png",
    "10.1103/physrevlett.118.204101": "https://i.imgur.com/GozQ0LI.jpg",
    "10.1038/533452a": "https://i.imgur.com/FuREqtu.png",
    "10.3390/mi5020139": "https://i.imgur.com/1Y9ZXFl.png",
    "10.1088/0953-8984/17/2/l06": "https://i.imgur.com/0AwY3yx.png",
    "10.1103/physrevb.74.104405": "https://i.imgur.com/uv69jzk.png",
    "10.1080/03057925.2016.1138396": "https://i.imgur.com/jEpkFaP.png",
    "10.17159/sajs.2017/20170010": "https://i.imgur.com/6I4b2Ku.png",
    "10.22269/170207": "https://i.imgur.com/zefb3z9.png",
    "10.1038/538446a": "https://i.imgur.com/E389P27.png",
    "10.1038/s41467-017-00371-4": "https://i.imgur.com/HNoiMYx.png",
    "10.2514/1.b36120": "https://i.imgur.com/72r34AL.png",
    "10.1007/s00199-010-0573-7": "https://i.imgur.com/490MplS.png",
    "10.1007/s11109-016-9373-5": "https://i.imgur.com/j5MksbV.png",
    "10.1108/jstp-09-2014-0208": "https://i.imgur.com/WqjjXAe.png",
    "10.1073/pnas.0913352107": "https://i.imgur.com/mWuq0bY.png",
    "10.1016/j.acalib.2017.04.005": "https://i.imgur.com/lXQ1gN6.png",
    "10.1016/j.hm.2017.08.001": "https://i.imgur.com/9Yc3tgI.png",
    "10.2105/ajph.2011.300576": "https://i.imgur.com/9ZHGsmc.png",
    "10.1215/10829636-2647301": "https://i.imgur.com/srfJyWu.png",
    "10.1007/jhep09(2016)038": "https://i.imgur.com/oCJqZYg.png",
    "10.1051/0004-6361/201321531": "https://i.imgur.com/gbaAe3D.png",
    "10.1038/ncomms12671": "https://i.imgur.com/GyLVkHq.png",
    "10.1029/2005wr004820": "https://i.imgur.com/o7JWepN.png",
    "10.1038/srep21691": "https://i.imgur.com/B4KuMtm.png",
    "10.1371/journal.pone.0176896": "https://i.imgur.com/XdPu3Qf.png",
    "10.1088/1748-9326/9/10/104008": "https://i.imgur.com/erLpug4.png",
}


class WeeklyStats(db.Model):
    id = db.Column(db.Text, primary_key=True)
    updated = db.Column(db.DateTime)
    mendeley_api_raw = db.Column(JSONB)
    oadoi_api_raw = db.Column(JSONB)
    pubmed_api_raw = db.Column(JSONB)
    altmetric_com_api_raw = deferred(db.Column(JSONB))
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

        ced_events = CedEvent.query.filter(CedEvent.doi == self.id).all()
        ced_events_this_week = [e for e in ced_events if e.week == self.week]
        for e in ced_events_this_week:
            event_count_dict[e.source_id] += 1

        sources = []
        for (source_id, num) in event_count_dict.items():
            sources.append({"source_id": source_id, "event_count": num})
        self.sources = sources

    def get_event_count(self, source_id):
        try:
            return [
                s["event_count"] for s in self.sources if s["source_id"] == source_id
            ][0]
        except IndexError:
            return 0

    # get altmetric.com
    def run(self):
        self.updated = datetime.datetime.utcnow()

        try:
            url = "http://api.altmetric.com/v1/fetch/doi/{doi}?key={key}".format(
                doi=self.id, key=os.getenv("ALTMETRIC_KEY")
            )
            # print u"calling {}".format(url)

            r = requests.get(url, timeout=10)  # timeout in seconds

            if r.status_code == 200:
                # we got a good status code, the DOI has metrics.
                self.altmetric_com_api_raw = r.json()
            else:
                logger.info(
                    "got unexpected altmetric status_code code {}".format(r.status_code)
                )

        except requests.Timeout:
            logger.info("got requests.Timeout")

    # get abstracts
    def run_get_abstracts(self):
        self.updated = datetime.datetime.utcnow()

        if not self.abstract:
            r = requests.get("http://doi.org/{}".format(self.id))
            text = r.text
            if "</header>" in text:
                try:
                    text_after_header = text.split("</header", 1)[1]
                    text_after_p = text_after_header.split(
                        "																						<p>", 1
                    )[1]
                    clean_text = clean_html(text_after_p)
                    # print clean_text[0:1000]
                    self.abstract = clean_text[0:1000]
                except IndexError:
                    pass

    def run_other_things(self):
        self.updated = datetime.datetime.utcnow()

        url = "http://api.oadoi.org/v2/{}?email=team+paperbuzz@ourresearch.org".format(self.id)
        r = requests.get(url)
        self.oadoi_api_raw = r.json()
        if self.oadoi_api_raw and "is_oa" in self.oadoi_api_raw:
            self.is_open_access = self.oadoi_api_raw["is_oa"]

        self.set_sources()
        self.num_twitter_events = self.get_event_count("twitter")

        self.num_unpaywall_events = self.get_event_count("unpaywall_views")
        self.num_academic_unpaywall_events = self.get_event_count(
            "unpaywall_views_academic"
        )
        self.num_nonacademic_unpaywall_events = self.get_event_count(
            "unpaywall_views_nonacademic"
        )
        if self.num_unpaywall_events:
            self.ratio_academic_unpaywall_events = (
                float(self.num_academic_unpaywall_events) / self.num_unpaywall_events
            )

        if self.mendeley_api_raw and self.mendeley_api_raw.get("abstract", None):
            self.abstract = self.mendeley_api_raw.get("abstract", None)
        else:
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={}[doi]&tool=paperbuzz&email=team@ourresearch.org&retmode=json".format(
                self.id
            )
            print(url)
            r = requests.get(url)
            try:
                pmid = r.json()["esearchresult"]["idlist"][0]
            except (KeyError, IndexError):
                pmid = None

            if pmid:
                url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}&tool=paperbuzz&email=team@ourresearch.org".format(
                    pmid
                )
                print(url)
                r = requests.get(url)
                abstract_hits = re.findall(
                    'abstract.*?"(.*?)"', r.text.replace("\n", ""), re.MULTILINE
                )
                if abstract_hits:
                    self.abstract = abstract_hits[0]
                url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={}&retmode=json&tool=paperbuzz&email=team@ourresearch.org".format(
                    pmid
                )
                print(url)
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
            "data management",
        ]
        quantum_computing_words = [
            "reproducibility",
            "medical research",
            "open access",
        ]
        our_discipline = discipline_lookup[mendeley_discipline]

        # use override if it is there
        if self.id in discipline_overrides:
            return discipline_overrides[self.id]

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
        for mendeley_discipline in self.mendeley_api_raw[
            "reader_count_by_subdiscipline"
        ]:
            our_discipline = self.get_our_discipline(mendeley_discipline)
            num_in_discipline = self.mendeley_api_raw["reader_count_by_subdiscipline"][
                mendeley_discipline
            ][mendeley_discipline]
            discipline_dict[our_discipline] += num_in_discipline

        total_in_all_disciplines = 0
        for (our_discipline, num) in discipline_dict.items():
            total_in_all_disciplines += num
            if num > self.num_main_discipline:
                self.num_main_discipline = num
                self.main_discipline = our_discipline

        if total_in_all_disciplines < 5:
            self.num_main_discipline = None
            self.main_discipline = None

        logger.info(
            "discipline for {} is {}={}".format(
                self.id, self.main_discipline, self.num_main_discipline
            )
        )

    def sources_dicts_no_events(self):
        my_doi_obj = Doi(self.id)
        my_doi_obj.altmetrics.get()
        sources_dicts_with_events = (
            my_doi_obj.altmetrics_dict_including_unpaywall_views()
        )
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
        metadata = dict(
            (k, v) for k, v in self.oadoi_api_raw.items() if k in metadata_keys
        )
        metadata["abstract"] = self.display_abstract
        # also use other pubmed data here if no mendeley

        ret = {
            "doi": self.id,
            "metadata": metadata,
            "open_access": dict(
                (k, v) for k, v in self.oadoi_api_raw.items() if k in open_access_keys
            ),
            "sources": self.sources,
            "photo": photos.get(self.id, None),
            "debug": {},
        }

        # if self.mendeley_api_raw:
        #     ret["debug"]["mendeley_disciplines"] = self.mendeley_api_raw["reader_count_by_subdiscipline"]

        return ret

    def __repr__(self):
        return "<WeeklyStats ({}, {}={})>".format(
            self.id, self.main_discipline, self.num_main_discipline
        )


def get_mendeley_session():
    mendeley_client = mendeley_lib.Mendeley(
        client_id=os.getenv("MENDELEY_OAUTH2_CLIENT_ID"),
        client_secret=os.getenv("MENDELEY_OAUTH2_SECRET"),
    )
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
            doc = mendeley_session.catalog.by_identifier(doi=doi, view="stats")
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
