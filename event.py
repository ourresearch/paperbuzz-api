


class Event(object):
    def __init__(self, ced_event):
        self.ced_event = ced_event
        self.subj_id = ced_event["subj_id"]

    def get(self):
        # override for events that req
        pass

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


class WikipediaPageEvent(Event):
    # https://www.eventdata.crossref.org/guide/sources/wikipedia/

    # the CED model counts many events that happen on a given wiki page.
    # we just want one event to represent one page.
    # the age of the event should be the initial creation of the page.
    # for now we do not handle deleted pages or deleted references.

    def is_same_page_as(self, test_url):
        return self._find_stem(test_url) == self._find_stem(self.subj_id)

    def _find_stem(self, url):
        return url.split("&oldid=")[0]


    def add_ced_event(self, ced_event):

        # we are not interested in "replaces" or "is_version_of" for now.
        if ced_event["relation_type_id"] != "references":
            return False

        # if this CED event happened earlier than the one we have already, replace it.
        # we want this event to
        if self.ced_event["occurred_at"] > ced_event["occurred_at"]:
            self.ced_event = ced_event
            return True

        # otherwise, we are not interested in this new event.
        return False


    def to_dict(self):
        ret = super(WikipediaPageEvent, self).to_dict()
        ret["page_url"] = self._find_stem(self.subj_id)
        return ret

