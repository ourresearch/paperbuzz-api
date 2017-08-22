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
            "altmetrics_sources": [s.to_dict() for s in self.ced_sources]
        }

        return ret


class CedSource(object):

    def __init__(self, source_id, events_list):
        self.source_id = source_id
        self.raw_events_list = events_list

    def to_dict(self):

        event_objects = []

        for raw_event in self.raw_events_list:
            event_objects.append(CedEvent(raw_event))

        # sort events by time
        event_objects = sorted(event_objects, key=lambda x: x.occurred_at)
        occurred_ats = [e.occurred_at for e in event_objects]

        ret = {
            "source_id": self.source_id,
            "events": [e.to_dict() for e in event_objects],
            "events_count": len(event_objects),
            "events_count_by_day": count_by_day(occurred_ats)
        }

        return ret


class CedEvent(object):
    def __init__(self, event_dict):
        self.event_dict = event_dict


    @property
    def occurred_at(self):
        return self.event_dict["occurred_at"]

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



def count_by_day(timestamps):
    """
    Make a frequency histogram based on a list of timestamps.

    :param timestamps: list of ISO 8601 timestamps
    :return: a list of dicts showing how frequently each timestamp appears
    """
    trimmed_timestamps = [ts.split("T")[0] for ts in timestamps]

    hist_dict = defaultdict(int)
    for ts in trimmed_timestamps:
        hist_dict[ts] += 1

    ret = []
    for ts, count in hist_dict.iteritems():
        ret.append({
            "date": ts,
            "count": count
        })

    ret = sorted(ret, key=lambda x: x["date"])

    return ret














