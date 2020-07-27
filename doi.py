import datetime
import requests

from app import db
from source import make_event_source
from event import CedEvent, MetadataCache


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


class OaDoi(object):
    def __init__(self, doi):
        self.doi = doi
        self.url = "https://api.oadoi.org/v2/{}".format(doi)
        self.data = {}

    def get(self):
        r = requests.get(self.url + '?email=team@ourresearch.org', timeout=5)
        if r.status_code == 200:
            self.data = r.json()

    def to_dict(self):
        self.data["oadoi_url"] = self.url
        return self.data


class CrossrefMetadata(object):
    def __init__(self, doi):
        self.doi = doi
        self.url = "https://api.crossref.org/works/{}/transform/application/vnd.citationstyles.csl+json".format(doi)
        self.data = {}

    def get(self):
        cached_item = MetadataCache.query.get(self.doi)
        expired = datetime.datetime.today() - datetime.timedelta(6*365/12)

        if cached_item and cached_item.updated > expired:
            self.data = cached_item.api_raw
        else:
            r = requests.get(self.url, timeout=10)
            if r.status_code == 200:
                self.data = r.json()
                self.save_to_cache()

    def to_dict(self):
        self.data["crossref_url"] = self.url
        return self.data

    def save_to_cache(self):
        existing_cache_item = MetadataCache.query.get(self.doi)
        if existing_cache_item:
            existing_cache_item.updated = datetime.datetime.utcnow()
            existing_cache_item.api_raw = self.data
            db.session.commit()
        else:
            new_cache_item = MetadataCache(id=self.doi, api_raw=self.data)
            db.session.add(new_cache_item)
            db.session.commit()
