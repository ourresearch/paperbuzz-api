import requests
from source import make_event_source
from event import CedEvent
from event import UnpaywallEvent


metadata = {
    "DOI": "10.7717/peerj.3828",
    "ISSN": [
      "2167-8359"
    ],
    "URL": "http://dx.doi.org/10.7717/peerj.3828",
    "abstract": "<jats:p>The phylogeny of the Salmonidae family, the only living one of the Order Salmoniformes, remains still unclear because of several reasons. Such reasons include insufficient taxon sampling and/or DNA information. The use of complete mitochondrial genomes (mitogenomics) could provide some light on it, but despite the high number of mitogenomes of species belonging to this family published during last years, an integrative work containing all this information has not been done. In this work, the phylogeny of 46 Salmonidae species was inferred from their mitogenomic sequences. Results include a Bayesian molecular-dated phylogenetic tree with very high statistical support showing Coregoninae and Salmoninae as sister subfamilies, as well as several new phylogenetic relationships among species and genus of the family. All these findings contribute to improve our understanding of the Salmonidae systematics and could have consequences on related evolutionary studies, as well as highlight the importance of revisiting phylogenies with integrative studies.</jats:p>",
    "article-number": "e3828",
    "author": [
      {
        "affiliation": [
          {
            "name": "Department of Biodiversity and Evolutionary Biology, National Museum of Natural Sciences (CSIC),  Madrid, Spain"
          }
        ],
        "family": "Horreo",
        "given": "Jose L."
      }
    ],
    "container-title": "PeerJ",
    "crossref_url": "https://api.crossref.org/works/10.7717/peerj.3828/transform/application/vnd.citationstyles.csl+json",
    "issued": {
      "date-parts": [
        [
          2017,
          9,
          18
        ]
      ]
    },
    "member": "4443",
    "page": "e3828",
    "relation": {
      "cites": []
    },
    "score": 1.0,
    "title": "Revisiting the mitogenomic phylogeny of Salmoninae: new insights thanks to recent sequencing advances",
    "type": "article-journal",
    "volume": "5"
  }

open_access = {
    "best_oa_location": {
      "evidence": "hybrid (via crossref license)",
      "host_type": "publisher",
      "is_best": True,
      "license": "cc-by",
      "updated": "2017-09-24T00:09:23.763770",
      "url": "http://doi.org/10.7717/peerj.3828",
      "version": "publishedVersion"
    },
    "data_standard": 1,
    "doi": "10.7717/peerj.3828",
    "is_oa": True,
    "journal_is_oa": False,
    "journal_issns": "2167-8359",
    "journal_name": "PeerJ",
    "oa_locations": [
      {
        "evidence": "hybrid (via crossref license)",
        "host_type": "publisher",
        "is_best": True,
        "license": "cc-by",
        "updated": "2017-09-24T00:09:23.763770",
        "url": "http://doi.org/10.7717/peerj.3828",
        "version": "publishedVersion"
      }
    ],
    "oadoi_url": "https://api.oadoi.org/v2/10.7717/peerj.3828",
    "publisher": "PeerJ",
    "title": "Revisiting the mitogenomic phylogeny of Salmoninae: new insights thanks to recent sequencing advances",
    "updated": "2017-09-24T00:09:23.754159",
    "x_reported_noncompliant_copies": [],
    "year": 2017
  }

sources = [
{
"events": [],
"events_count": 29,
"events_count_by_day": [],
"source_id": "twitter"
},
{
"events": [],
"source_id": "unpaywall_views"
}
]



class Doi(object):

    def __init__(self, doi):
        self.doi = doi
        self.metadata = CrossrefMetadata(self.doi)
        self.open_access = OaDoi(self.doi)
        self.altmetrics = AltmetricsForDoi(self.doi)
        self.unpaywall_views = UnpaywallViewsForDoi(self.doi)

    def get(self):
        self.metadata.get()
        self.open_access.get()
        self.altmetrics.get()
        self.unpaywall_views.get()

    def to_dict(self):
        altmetrics_value = self.altmetrics.to_dict()
        altmetrics_value["sources"] += [{
                "source_id": "unpaywall_views",
                "events": self.unpaywall_views.to_dict()}]
        ret = {
            "doi": self.doi,
            "altmetrics":  altmetrics_value,
            "metadata": self.metadata.to_dict(),
            "open_access": self.open_access.to_dict(),
            "unpaywall_views": self.unpaywall_views.to_dict()
        }
        return ret


    def to_dict_hotness(self):
        ret = {
            "doi": self.doi,
            "metadata": metadata,
            "open_access": open_access,
            "sources": sources,
        }
        return ret

class AltmetricsForDoi(object):
    def __init__(self, doi):
        self.doi = doi
        self.ced_url = "http://query.eventdata.crossref.org/events?rows=10000&filter=from-collected-date:1990-01-01,until-collected-date:2099-01-01,obj-id:{}".format(
            self.doi
        )
        self.events = []
        self.sources = []

    def get(self):
        ced_events = self._get_ced_events()
        for ced_event in ced_events:
            self.add_event(ced_event)

    def add_event(self, ced_event):
        source_id = ced_event["source_id"]

        # get the correct source for this event
        my_source = None
        for source in self.sources:
            if source.id == source_id:
                my_source = source
                break

        # we don't have this source for this DOI.
        # make it and add it to the list
        if my_source is None:
            my_source = make_event_source(source_id)
            self.sources.append(my_source)

        # this source exists now for sure because we either found it or made it
        # add the event to the source.
        my_source.add_event(ced_event)


    def _get_ced_events(self):
        """
        Handy test data:
        10.2190/EC.43.3.f                       # no events
        10.1371/journal.pone.0000308            # many events, incl lots of wiki
        """

        event_objs = CedEvent.query.filter(CedEvent.doi==self.doi).all()
        event_dicts = [event.api_raw for event in event_objs]
        return event_dicts

        return event_dicts

    def to_dict(self):
        ret = {
            "crossref_event_data_url": self.ced_url,
            "sources": [s.to_dict() for s in self.sources]
        }
        return ret



class UnpaywallViewsForDoi(object):
    def __init__(self, doi):
        self.doi = doi

    def get(self):
        event_objs = UnpaywallEvent.query.filter(UnpaywallEvent.doi==self.doi).all()
        event_dicts = [event.api_dict() for event in event_objs]
        return event_dicts

    def to_dict(self):
        ret = self.get()
        return ret


class OaDoi(object):
    def __init__(self, doi):
        self.doi = doi
        self.url = u"https://api.oadoi.org/v2/{}".format(doi)
        self.data = {}

    def get(self):
        r = requests.get(self.url)
        self.data = r.json()

    def to_dict(self):
        self.data["oadoi_url"] = self.url
        return self.data



class CrossrefMetadata(object):
    def __init__(self, doi):
        self.doi = doi
        self.url = u"https://api.crossref.org/works/{}/transform/application/vnd.citationstyles.csl+json".format(doi)
        self.data = {}

    def get(self):
        r = requests.get(self.url)
        self.data = r.json()

    def to_dict(self):
        self.data["crossref_url"] = self.url
        return self.data

