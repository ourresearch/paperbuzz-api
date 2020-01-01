from time import time
import argparse
import os

from sqlalchemy import orm
from sqlalchemy import text

from app import db
from app import logger
from util import elapsed
from util import safe_commit
from util import run_sql
from date_range import DateRange


def update_fn(cls, method, obj_id_list, shortcut_data=None, index=1):

    # we are in a fork!  dispose of our engine.
    # will get a new one automatically
    # if is pooling, need to do .dispose() instead
    db.engine.dispose()

    start = time()

    # logger(u"obj_id_list: {}".format(obj_id_list))

    q = db.session.query(cls).options(orm.undefer('*')).filter(cls.id.in_(obj_id_list))
    obj_rows = q.all()
    num_obj_rows = len(obj_rows)

    # if the queue includes items that aren't in the table, build them
    # assume they can be built by calling cls(id=id)
    if num_obj_rows != len(obj_id_list):
        logger.info("not all objects are there, so creating")
        ids_of_got_objects = [obj.id for obj in obj_rows]
        for id in obj_id_list:
            if id not in ids_of_got_objects:
                new_obj = cls(id=id)
                db.session.add(new_obj)
        safe_commit(db)
        logger.info("done")

    q = db.session.query(cls).options(orm.undefer('*')).filter(cls.id.in_(obj_id_list))
    obj_rows = q.all()
    num_obj_rows = len(obj_rows)

    logger.info("{pid} {repr}.{method_name}() got {num_obj_rows} objects in {elapsed} seconds".format(
        pid=os.getpid(),
        repr=cls.__name__,
        method_name=method.__name__,
        num_obj_rows=num_obj_rows,
        elapsed=elapsed(start)
    ))

    for count, obj in enumerate(obj_rows):
        start_time = time()

        if obj is None:
            return None

        method_to_run = getattr(obj, method.__name__)

        logger.info("***")
        logger.info("#{count} starting {repr}.{method_name}() method".format(
            count=count + (num_obj_rows*index),
            repr=obj,
            method_name=method.__name__
        ))

        if shortcut_data:
            method_to_run(shortcut_data)
        else:
            method_to_run()

        logger.info("finished {repr}.{method_name}(). took {elapsed} seconds".format(
            repr=obj,
            method_name=method.__name__,
            elapsed=elapsed(start_time, 4)
        ))


    logger.info("committing\n\n")
    start_time = time()
    commit_success = safe_commit(db)
    if not commit_success:
        logger.info("COMMIT fail")
    logger.info("commit took {} seconds".format(elapsed(start_time, 2)))
    db.session.remove()  # close connection nicely
    return None  # important for if we use this on RQ


class UpdateRegistry:
    def __init__(self):
        self.updates = {}

    def register(self, update):
        self.updates[update.name] = update

    def get(self, update_name):
        return self.updates[update_name]


update_registry = UpdateRegistry()


class UpdateDbQueue:
    def __init__(self, **kwargs):
        self.job = kwargs["job"]
        self.method = self.job
        self.cls = DateRange  # manually set class to support python 3
        self.chunk = kwargs.get("chunk", 10)
        self.shortcut_fn = kwargs.get("shortcut_fn", None)
        self.shortcut_fn_per_chunk = kwargs.get("shortcut_fn_per_chunk", None)
        self.name = "{}.{}".format(self.cls.__name__, self.method.__name__)
        self.action_table = kwargs.get("action_table", None)
        self.where = kwargs.get("where", None)
        self.queue_name = kwargs.get("queue_name", None)

    def run(self, **kwargs):
        single_obj_id = kwargs.get("id", None)
        limit = kwargs.get("limit", 0)
        chunk = kwargs.get("chunk", self.chunk)
        after = kwargs.get("after", None)
        queue_table = "doi_queue_paperbuzz"

        my_dyno_name = os.getenv("DYNO", "unknown")
        if kwargs.get("hybrid", False) or "hybrid" in my_dyno_name:
            queue_table += "_with_hybrid"
        elif kwargs.get("dates", False) or "dates" in my_dyno_name:
            queue_table += "_dates"

        if single_obj_id:
            limit = 1
        else:
            if not limit:
                limit = 1000

        ## based on http://dba.stackexchange.com/a/69497
        text_query_pattern = """WITH picked_from_queue AS (
                   SELECT *
                   FROM   {queue_table}
                   WHERE  started is null
                   ORDER BY rand
               LIMIT  {chunk}
               FOR UPDATE SKIP LOCKED
               )
            UPDATE {queue_table} doi_queue_rows_to_update
            SET    enqueued=TRUE, started=now(), dyno='{my_dyno_name}'
            FROM   picked_from_queue
            WHERE picked_from_queue.id = doi_queue_rows_to_update.id
            RETURNING doi_queue_rows_to_update.id;"""
        text_query = text_query_pattern.format(
            chunk=chunk,
            my_dyno_name=my_dyno_name,
            queue_table=queue_table
        )
        logger.info("the queue query is:\n{}".format(text_query))

        index = 0

        start_time = time()
        while True:
            new_loop_start_time = time()
            if single_obj_id:
                object_ids = [single_obj_id]
            else:
                # logger.info(u"looking for new jobs")
                row_list = db.engine.execute(text(text_query).execution_options(autocommit=True)).fetchall()
                object_ids = [row[0] for row in row_list]
                # logger.info(u"finished get-new-ids query in {} seconds".format(elapsed(new_loop_start_time)))

            if not object_ids:
                break
                # logger.info(u"sleeping for 5 seconds, then going again")
                # sleep(5)
                # continue

            update_fn_args = [self.cls, self.method, object_ids]

            shortcut_data = None
            if self.shortcut_fn_per_chunk:
                shortcut_data_start = time()
                logger.info("Getting shortcut data...")
                shortcut_data = self.shortcut_fn_per_chunk()
                logger.info("Got shortcut data in {} seconds".format(
                    elapsed(shortcut_data_start)))

            update_fn(*update_fn_args, index=index, shortcut_data=shortcut_data)

            object_ids_str = ",".join(["'{}'".format(id) for id in object_ids])
            run_sql(db, "update {queue_table} set finished=now() where id in ({ids})".format(
                queue_table=queue_table, ids=object_ids_str))

            index += 1

            if single_obj_id:
                return
            else:
                num_items = limit  #let's say have to do the full limit
                num_jobs_remaining = num_items - (index * chunk)
                try:
                    jobs_per_hour_this_chunk = chunk / float(elapsed(new_loop_start_time) / 3600)
                    predicted_mins_to_finish = round(
                        (num_jobs_remaining / float(jobs_per_hour_this_chunk)) * 60,
                        1
                    )
                    logger.info("\n\nWe're doing {} jobs per hour. At this rate, if we had to do everything up to limit, done in {}min".format(
                        int(jobs_per_hour_this_chunk),
                        predicted_mins_to_finish
                    ))
                    logger.info("\t{} seconds this loop, {} chunks in {} seconds, {} seconds/chunk average\n".format(
                        elapsed(new_loop_start_time),
                        index,
                        elapsed(start_time),
                        round(elapsed(start_time)/float(index), 1)
                    ))
                except ZeroDivisionError:
                    # logger.info(u"not printing status because divide by zero")
                    logger.info("."),


def main(fn, optional_args=None):
    start = time()

    # call function by its name in this module, with all args :)
    # http://stackoverflow.com/a/4605/596939
    if optional_args:
        globals()[fn](*optional_args)
    else:
        globals()[fn]()

    logger.info("total time to run: {} seconds".format(elapsed(start)))


if __name__ == "__main__":

    # get args from the command line:
    parser = argparse.ArgumentParser(description="Run stuff.")
    parser.add_argument('function', type=str, help="what function you want to run")
    parser.add_argument('optional_args', nargs='*', help="positional args for the function")

    args = vars(parser.parse_args())

    function = args["function"]
    optional_args = args["optional_args"]

    logger.info("running main.py {function} with these args:{optional_args}\n".format(
        function=function, optional_args=optional_args))

    main(function, optional_args)

    db.session.remove()


