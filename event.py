import datetime
import shortuuid
import hashlib

from app import db
from sqlalchemy.dialects.postgresql import JSONB


class CedEvent(db.Model):
    id = db.Column(db.Text, primary_key=True)
    updated = db.Column(db.DateTime)
    doi = db.Column(db.Text)
    source_id = db.Column(db.Text)
    normalized_subj_id = db.Column(db.Text)
    occurred_at = db.Column(db.DateTime)
    uniqueness_key = db.Column(db.Text)
    api_raw = db.Column(JSONB)

    def __init__(self, **kwargs):
        self.id = shortuuid.uuid()[0:20]
        self.updated = datetime.datetime.utcnow()
        self.api_raw = kwargs["api_raw"]
        self.occurred_at = self.get_occurred_at()
        self.source_id = self.get_source_id()
        self.normalized_subj_id = self.get_normalized_subj_id()

        # this one has to be last
        self.uniqueness_key = self.get_uniqueness_key()
        super(CedEvent, self).__init__(**kwargs)

    @property
    def action(self):
        if not self.api_raw:
            return None
        return self.api_raw["action"]

    @property
    def subj_id(self):
        if not self.api_raw:
            return None
        return self.api_raw["subj_id"]

    def get_uniqueness_key(self):
        key = u"{} {} {}".format(self.source_id, self.normalized_subj_id, self.action)
        hash_key = hashlib.md5(key).hexdigest()
        return hash_key

    def get_occurred_at(self):
        if not self.api_raw:
            return None
        return self.api_raw["occurred_at"]

    def get_source_id(self):
        if not self.api_raw:
            return None
        return self.api_raw["source_id"]

    def get_normalized_subj_id(self):
        if not self.subj_id:
            return None
        if self.source_id=="wikipedia":
            # return just the main page part from here: https://en.wikipedia.org/w/index.php?title=George_Harrison&oldid=799153948
            return self.subj_id.split("&oldid")[0]
        return self.subj_id

    def __repr__(self):
        return u"<CedEvent ({} {})>".format(self.source_id, self.id)



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

