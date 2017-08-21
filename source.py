import requests
from collections import defaultdict


class Doi(object):

    def __init__(self, doi):
        self.doi = doi
        self.ced_sources = []



    def query(self):
        ced_events = get_ced_events(self.doi)

        # make Source objects for all the CED sources, put them in a list
        # easier to start with a dict
        ced_sources_dict = defaultdict(list)
        for event in ced_events:
            ced_sources_dict[event["source_id"]].append(event)


        # convert to objects and append to list
        for source_id, events in ced_sources_dict.iteritems():
            my_source_obj = CedSource(source_id, events)
            self.ced_sources.append(my_source_obj)



    def to_dict(self):
        ret = {
            "doi": self.doi,
            "altmetrics": [s.to_dict() for s in self.ced_sources]
        }

        return ret


class CedSource(object):

    def __init__(self, source_id, events_list):
        self.source_id = source_id
        self.raw_events_list = events_list

    def to_dict(self):
        ret = {
            "source_id": self.source_id,
            "events": [],
            "events_count": len(self.raw_events_list),
            "events_count_by_day": []  # todo make this work.
        }

        for raw_event in self.raw_events_list:
            my_event_obj = CedEvent(raw_event)
            ret["events"].append(my_event_obj.to_dict())

        return ret


class CedEvent(object):
    def __init__(self, event_dict):
        self.event_dict = event_dict


    def to_dict(self):
        try:
            author_url = self.event_dict["subj"]["author"]["url"]
        except KeyError:
            author_url = None


        # return self.event_dict

        return {
            # "full": self.event_dict,
            "author": author_url,
            "occurred_at": self.event_dict["occurred_at"],
            "url": self.event_dict["subj_id"]
        }






def get_ced_events(doi):
        url = "http://query.eventdata.crossref.org/events?rows=10000&filter=from-collected-date:1990-01-01,until-collected-date:2099-01-01,obj-id:{}".format(
            doi
        )
        r = requests.get(url)
        data = r.json()
        events = data["message"]["events"]
        return events
