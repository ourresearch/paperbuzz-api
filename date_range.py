import datetime
from time import sleep, time
from urllib.parse import quote

import requests
from sqlalchemy.exc import IntegrityError

from app import db, logger
from event import CedEvent
from util import clean_doi, elapsed, NoDoiException, run_sql, safe_commit

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

    def get_events(self, rows=1000):
        headers = {"Accept": "application/json", "User-Agent": "ourresearch.org"}
        base_url = "https://api.eventdata.crossref.org/v1/events?rows={rows}&filter=from-collected-date:{first},until-collected-date:{first}&mailto=team@ourresearch.org"

        cursor = None
        has_more_responses = True
        num_so_far = 0
        to_commit = []

        while has_more_responses:
            start_time = time()
            url = base_url.format(first=self.first_day, last=self.last_day, rows=rows)
            if cursor:
                url += "&cursor={cursor}".format(cursor=cursor)
            logger.info("calling url: {}".format(url))

            call_tries = 0
            resp = None
            while not resp and call_tries < 5:
                try:
                    s = requests.Session()
                    resp = s.get(url, headers=headers, timeout=60)
                except (
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.ConnectionError,
                ):
                    logger.info(
                        "timed out or connection error, trying again after sleeping"
                    )
                    call_tries += 1
                    sleep(2)

            if not resp:
                self.process_failed_import()

            logger.info(
                "getting CED data took {} seconds".format(elapsed(start_time, 2))
            )
            if resp.status_code != 200:
                logger.info(
                    "error in CED call, status_code = {}".format(resp.status_code)
                )
                return

            resp_data = resp.json()["message"]
            old_cursor = cursor
            cursor = resp_data.get("next-cursor", None)

            if cursor == old_cursor:
                logger.info("cursors are the same!  url {}.  stopping.".format(url))
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

                try:
                    ced_obj = CedEvent(doi=doi, api_raw=api_raw)
                except KeyError:
                    logger.info("missing key for event, skipping. {}".format(api_raw))
                    continue

                bad_dates = [
                    "0000-01-01T00:00:00Z",
                    "-0001-11-30T00:00:00Z",
                    "-0001-11-28T00:00:00Z",
                ]
                if api_raw["occurred_at"] in bad_dates:
                    logger.info(
                        "bad date format in occurred_at field, skipping. {}".format(
                            api_raw
                        )
                    )
                    continue

                if not CedEvent.query.filter(
                    CedEvent.uniqueness_key == ced_obj.uniqueness_key
                ).first() and ced_obj.uniqueness_key not in [
                    obj.uniqueness_key for obj in to_commit
                ]:
                    try:
                        db.session.merge(ced_obj)
                        to_commit.append(ced_obj)
                        num_so_far += 1
                    except IntegrityError:
                        logger.error("missing source. {}".format(ced_obj.source_id))
                        raise
                else:
                    # logger.info(u"not committing, is dup")
                    pass

                if len(to_commit) >= 100:
                    # logger.info(u"committing")
                    start_commit = time()
                    safe_commit(db)
                    logger.info(
                        "committing done in {} seconds".format(elapsed(start_commit, 2))
                    )
                    to_commit = []

            logger.info(
                "at bottom of loop, got {} records".format(len(resp_data["events"]))
            )

        # make sure to get the last ones
        logger.info("done everything, saving last ones")
        safe_commit(db)

        return num_so_far

    def process_failed_import(self):
        run_sql(
            db,
            """update doi_queue_paperbuzz_dates 
                                       set enqueued=NULL, finished=NULL, started=NULL, dyno=NULL 
                                       where id = '{id_date}'""".format(
                id_date=self.id
            ),
        )
        raise requests.exceptions.ReadTimeout

    def __repr__(self):
        return "<DateRange (starts: {})>".format(self.id)
