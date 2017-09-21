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

    def get_events(self, rows=100):
        headers={"Accept": "application/json", "User-Agent": "impactstory.org"}
        base_url = "http://query.eventdata.crossref.org/events?rows={rows}&filter=from-collected-date:{first},until-collected-date:{first}"
        base_url_with_cursor = "http://query.eventdata.crossref.org/events?rows={rows}&next-cursor={cursor}"

        cursor = None
        has_more_responses = True
        num_so_far = 0
        num_between_commits = 0

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
                    logger.info(u"timed out, trying again after sleeping for 3 seconds")
                    sleep(3)

            if not resp:
               raise(requests.exceptions.ReadTimeout)

            logger.info(u"getting CED data took {} seconds".format(elapsed(start_time, 2)))
            if resp.status_code != 200:
                logger.info(u"error in CED call, status_code = {}".format(resp.status_code))
                return

            resp_data = resp.json()["message"]
            cursor = resp_data.get("next-cursor", None)
            if cursor:
                cursor = quote(cursor)

            if not resp_data["events"] or not cursor:
                has_more_responses = False

            for api_raw in resp_data["events"]:

                doi = clean_doi(api_raw["obj_id"])
                print doi
                ced_obj = CedEvent(doi=doi, api_raw=api_raw)
                # db.session.add(ced_obj)
                num_between_commits += 1
                num_so_far += 1

                if num_between_commits > 1000:
                    # logger.info(u"committing")
                    start_commit = time()
                    # safe_commit(db)
                    logger.info(u"committing done in {} seconds".format(elapsed(start_commit, 2)))
                    num_between_commits = 0

            logger.info(u"at bottom of loop, got {} records".format(len(resp_data["events"])))

        # make sure to get the last ones
        # @todo uncomment this
        # logger.info(u"done everything, saving last ones")
        # safe_commit(db)

        return num_so_far

    def __repr__(self):
        return u"<DateRange (starts: {})>".format(self.id)






