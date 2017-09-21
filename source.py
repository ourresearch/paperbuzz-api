from collections import defaultdict
from event import Event
from event import WikipediaPageEvent




def make_event_source(id):
    if id == "wikipedia":
        return WikipediaEventSource(id)

    else:
        return EventSource(id)


class EventSource(object):

    def __init__(self, source_id):
        self.id = source_id
        self.events = []
        self.events_count_by_day = []

    def add_event(self, ced_event):
        my_event = Event(ced_event)
        self.events.append(my_event)
        self._update()
        return my_event

    def _update(self):
        # sort events by time
        self.events = sorted(self.events, key=lambda x: x.occurred_at)

        # recompute the count_by_day histogram
        occurred_ats = [e.occurred_at for e in self.events]
        self.events_count_by_day = count_by_day(occurred_ats)


    def to_dict(self):
        ret = {
            "source_id": self.id,
            "events": [e.to_dict() for e in self.events],
            "events_count": len(self.events),
            "events_count_by_day": self.events_count_by_day
        }

        return ret



class WikipediaEventSource(EventSource):
    # https://www.eventdata.crossref.org/guide/sources/wikipedia/

    # We need to add wiki events differently, because in this case a
    # single Event in our model rolls up a whole bunch of CED events.
    # We want just one Event for every wiki page, and they have oodles.


    def _get_base_wiki_page_for_url(self, url):
        for my_event in self.events:
            if my_event.is_same_page_as(url):
                return my_event

        return None


    def add_event(self, ced_event):
        event_for_this_wiki_page = self._get_base_wiki_page_for_url(ced_event["subj_id"])

        # first we see if this wiki page already has an Event
        try:
            event_for_this_wiki_page.add_ced_event(ced_event)

        # if not, we creat a new Event for this wiki page
        except AttributeError:
            event_for_this_wiki_page = WikipediaPageEvent(ced_event)
            self.events.append(event_for_this_wiki_page)

        self._update()
        return event_for_this_wiki_page

















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













