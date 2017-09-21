import requests
from source import make_event_source
from event import CedEvent



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

    def to_dict(self):
        ret = {
            "doi": self.doi,
            "altmetrics":  self.altmetrics.to_dict(),
            "metadata": self.metadata.to_dict(),
            "open_access": self.open_access.to_dict()
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

        print "doi", self.doi
        event_objs = CedEvent.query.filter(CedEvent.doi==self.doi).all()
        event_dicts = [event.api_raw for event in event_objs]
        print "event_dicts", event_dicts
        return event_dicts


    def to_dict(self):
        ret = {
            "crossref_event_data_url": self.ced_url,
            "sources": [s.to_dict() for s in self.sources]
        }
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

