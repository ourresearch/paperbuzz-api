from collections import defaultdict
from event import create_event




def make_event_source(id):
    if id == "wikipedia":
        return ExtantWikipediaEventSource(id)

    else:
        return EventSource(id)


class EventSource(object):

    def __init__(self, source_id):
        self.id = source_id
        self.events = []
        self.events_count_by_day = []

    def add_event(self, ced_event):
        my_event = create_event(ced_event)
        self.events.append(my_event)
        self._update()

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



class ExtantWikipediaEventSource(EventSource):
    pass






















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














