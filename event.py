import datetime
import dateutil.parser
import shortuuid
import hashlib

from app import db
from sqlalchemy.dialects.postgresql import JSONB

class IpInsights(db.Model):
    id = db.Column(db.Text, primary_key=True)
    ip = db.Column(db.Text, db.ForeignKey('unpaywall_event.ip'))
    insights = db.Column(JSONB)
    updated = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        self.id = shortuuid.uuid()[0:20]
        self.updated = datetime.datetime.utcnow()
        super(IpInsights, self).__init__(**kwargs)



class UnpaywallEvent(db.Model):
    id = db.Column(db.Text, primary_key=True)
    doi = db.Column(db.Text)
    collected = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    ip = db.Column(db.Text, unique=True)

    insights_list = db.relationship(
        'IpInsights',
        lazy='subquery',
        viewonly=True,
        cascade="all, delete-orphan",
        backref=db.backref("unpaywall_event", lazy="subquery"),
        foreign_keys="IpInsights.ip"
    )


    def __init__(self, **kwargs):
        self.id = shortuuid.uuid()[0:20]
        self.updated = datetime.datetime.utcnow()
        super(UnpaywallEvent, self).__init__(**kwargs)

    @property
    def week(self):
        d = self.collected
        if isinstance(d, basestring):
            d = dateutil.parser.parse(d)
        return d.isocalendar()[1]

    @property
    def insights(self):
        if self.insights_list and self.insights_list[0]:
            return self.insights_list[0].insights
        else:
            return None

    @property
    def country(self):
        if not self.insights:
            return None
        return self.insights["country"]["name"]

    @property
    def country_iso(self):
        if not self.insights:
            return None
        return self.insights["country"]["iso_code"]

    @property
    def is_academic_location(self):
        if not self.insights:
            return None
        try:
            user_type = self.insights["traits"]["user_type"]
            if user_type == "college":
                return True
            else:
                return False
        except KeyError:
            return None



    def api_dict(self):
        return {
            "doi": self.doi,
            "occurred_at": "{}00:00".format(self.collected.isoformat()[:-5]),
            "country": self.country,
            "country_iso": self.country_iso,
            "is_college_location": self.is_academic_location,
            "author": None,
            "url": None
        }
    def __repr__(self):
        return u"<UnpaywallEvent ({})>".format(self.doi, self.collected)


class CedEvent(db.Model):
    id = db.Column(db.Text, primary_key=True)
    updated = db.Column(db.DateTime)
    doi = db.Column(db.Text)
    source_id = db.Column(db.Text, db.ForeignKey('ced_source.id'))
    source = db.relationship("CedSource")
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
    def week(self):
        d = self.occurred_at
        if isinstance(d, basestring):
            d = dateutil.parser.parse(d)
        return d.isocalendar()[1]

    @property
    def action(self):
        if not self.api_raw:
            return None
        if "action" in self.api_raw:
            return self.api_raw["action"]
        if "message_action" in self.api_raw:
            return self.api_raw["message_action"]
        return None


    @property
    def subj_id(self):
        if not self.api_raw:
            return None
        return self.api_raw["subj_id"]

    def get_uniqueness_key(self):
        key = u"{} {} {}".format(self.source_id, self.normalized_subj_id, self.action)
        hash_key = hashlib.md5(key.encode('utf-8')).hexdigest()
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


class CedSource(db.Model):
    id = db.Column(db.Text, primary_key=True)
    display_name = db.Column(db.Text)
    icon_url = db.Column(db.Text)
    events = db.relationship("CedEvent")

    def __repr__(self):
        return u"<CedSource ({} {} {})>".format(self.id, self.display_name, self.icon_url)
