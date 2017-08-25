
def create_event(ced_event):
    event = Event(ced_event)
    return event


class Event(object):
    def __init__(self, ced_event):
        self.ced_event = ced_event


    @property
    def occurred_at(self):
        return self.ced_event["occurred_at"]

    def to_dict(self):
        try:
            author_url = self.ced_event["subj"]["author"]["url"]
        except KeyError:
            author_url = None


        # return self.ced_event

        return {
            # "full": self.ced_event,
            "author": author_url,
            "occurred_at": self.ced_event["occurred_at"],
            "url": self.ced_event["subj_id"]
        }


class ExtantWikipediaEvent(Event):
    def __init__(self):
        self.page_id = None
        self.events = []

    def add(self, page_id, event):
        self.page_id = page_id
        self.events.append(event)

    def to_dict(self):
        events = sorted(self.events, key=lambda x: x["date"])


