import datetime
import shortuuid
import hashlib
import requests
from sqlalchemy.dialects.postgresql import JSONB

from app import db
from source import make_event_source
from event import CedEvent
from event import UnpaywallEvent



class Doi(object):

    def __init__(self, doi):
        self.doi = doi
        self.metadata = CrossrefMetadata(self.doi)
        self.open_access = OaDoi(self.doi)
        self.altmetrics = AltmetricsForDoi(self.doi)

    def get(self):
        self.metadata.get()
        self.open_access.get()
        self.altmetrics.get()

    def altmetrics_dict_including_unpaywall_views(self):
        altmetrics_value = self.altmetrics.to_dict()
        return altmetrics_value

    def to_dict(self):

        altmetrics = self.altmetrics.to_dict()


        ret = {
            "doi": self.doi,
            "altmetrics_sources": altmetrics["sources"],
            "crossref_event_data_url": altmetrics["crossref_event_data_url"],
            "metadata": self.metadata.to_dict(),
            "open_access": self.open_access.to_dict()
        }
        return ret



class AltmetricsForDoi(object):
    def __init__(self, doi):
        self.doi = doi
        self.ced_url = "https://api.eventdata.crossref.org/v1/events?rows=10000&filter=from-collected-date:1990-01-01,until-collected-date:2099-01-01,obj-id:{}".format(
            self.doi
        )
        self.events = []
        self.sources = []

    def get(self):
        #     """
        #     Handy test data:
        #     10.2190/EC.43.3.f                       # no events
        #     10.1371/journal.pone.0000308            # many events, incl lots of wiki
        #     """
        ced_events = CedEvent.query.filter(CedEvent.doi==self.doi).limit(2500).all()
        for ced_event in ced_events:
            self.add_event(ced_event)

    def add_event(self, ced_event):
        source_id = ced_event.source.id

        # get the correct source for this event
        my_source = None
        for source in self.sources:
            if source.id == source_id:
                my_source = source
                break

        # we don't have this source for this DOI.
        # make it and add it to the list
        if my_source is None:
            my_source = make_event_source(ced_event.source)
            self.sources.append(my_source)

        # this source exists now for sure because we either found it or made it
        # add the event to the source.
        my_source.add_event(ced_event.api_raw)

    def to_dict(self):
        ret = {
            "crossref_event_data_url": self.ced_url,
            "sources": [s.to_dict() for s in self.sources]
        }
        return ret



# currently unused, since we're moving Unpaywall to its own API
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
        r = requests.get(self.url + '?email=paperbuzz@impactstory.org', timeout=20)
        if r.status_code == 200:
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
        r = requests.get(self.url, timeout=20)
        if r.status_code == 200:
            self.data = r.json()

    def to_dict(self):
        self.data["crossref_url"] = self.url
        return self.data

