from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import deferred
from sqlalchemy import or_
from sqlalchemy import sql
from sqlalchemy import text
from sqlalchemy import orm
import requests
from time import sleep
from time import time
import datetime
import shortuuid
from urllib import quote
import os
import re

from app import logger
from app import db
from event import CedEvent
from util import elapsed
from util import safe_commit
from util import clean_doi
from util import NoDoiException


# insert into doi_queue_paperbuzz_dates (select s as id, random() as rand, false as enqueued, null::timestamp as finished, null::timestamp as started, null::text as dyno FROM generate_series
#         ( '2017-02-01'::timestamp
#         , '2017-09-20'::timestamp
#         , '1 day'::interval) s);


class DateRange(db.Model):
    id = db.Column(db.DateTime, primary_key=True)
    # end_date = db.Column(db.DateTime)

    @property
    def first(self):
        return self.id

    @property
    def first_day(self):
        return self.id.isoformat()[0:10]

    @property
    def last_day(self):
        return self.last.isoformat()[0:10]

    @property
    def last(self):
        return self.first + datetime.timedelta(days=1)

    def get_events(self, rows=10000):
        headers={"Accept": "application/json", "User-Agent": "impactstory.org"}
        base_url = "http://query.eventdata.crossref.org/events?rows={rows}&filter=from-collected-date:{first},until-collected-date:{first}"
        base_url_with_cursor = "http://query.eventdata.crossref.org/events?rows={rows}&next-cursor={cursor}"

        cursor = None
        has_more_responses = True
        num_so_far = 0
        to_commit = []

        while has_more_responses:
            start_time = time()
            if cursor:
                url = base_url_with_cursor.format(cursor=cursor, rows=rows)
            else:
                url = base_url.format(
                    first=self.first_day,
                    last=self.last_day,
                    rows=rows)
            logger.info(u"calling url: {}".format(url))

            call_tries = 0
            resp = None
            while not resp and call_tries < 25:
                try:
                    s = requests.Session()
                    resp = s.get(url, headers=headers, timeout=20)
                except requests.exceptions.ReadTimeout:
                    logger.info(u"timed out, trying again after sleeping")
                    sleep(2)

            if not resp:
               raise(requests.exceptions.ReadTimeout)

            logger.info(u"getting CED data took {} seconds".format(elapsed(start_time, 2)))
            if resp.status_code != 200:
                logger.info(u"error in CED call, status_code = {}".format(resp.status_code))
                return

            resp_data = resp.json()["message"]
            old_cursor = cursor
            cursor = resp_data.get("next-cursor", None)

            if cursor == old_cursor:
                logger.info(u"cursors are the same!  url {}.  stopping.".format(url))
                cursor = None

            if cursor:
                cursor = quote(cursor)

            if resp_data["events"] and cursor:
                has_more_responses = True
            else:
                has_more_responses = False

            for api_raw in resp_data["events"]:
                try:
                    doi = clean_doi(api_raw["obj_id"])
                except NoDoiException:
                    # no valid doi, not storing these
                    # this removes wikipedia "replaces" and "is_version_of"
                    continue

                source_id = api_raw["source_id"]
                occurred_at = api_raw["occurred_at"]
                ced_obj = CedEvent(doi=doi, api_raw=api_raw)
                if not CedEvent.query.filter(CedEvent.uniqueness_key==ced_obj.uniqueness_key).first() and \
                                ced_obj.uniqueness_key not in [obj.uniqueness_key for obj in to_commit]:
                    db.session.merge(ced_obj)
                    to_commit.append(ced_obj)
                    num_so_far += 1
                else:
                    # logger.info(u"not committing, is dup")
                    pass

                if len(to_commit) >= 100:
                    # logger.info(u"committing")
                    start_commit = time()
                    safe_commit(db)
                    logger.info(u"committing done in {} seconds".format(elapsed(start_commit, 2)))
                    to_commit = []

            logger.info(u"at bottom of loop, got {} records".format(len(resp_data["events"])))

        # make sure to get the last ones
        logger.info(u"done everything, saving last ones")
        safe_commit(db)

        return num_so_far


    def __repr__(self):
        return u"<DateRange (starts: {})>".format(self.id)






