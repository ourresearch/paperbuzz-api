import os
from app import db
from util import run_sql


def old_dates_update():
    """
    This function updates data by pulling 5 old dates from the past year.
    When run once each day, the entire past year will update every 73 days.
    """

    # pick 5 oldest dates from past year
    date_sql = """
        SELECT * FROM doi_queue_paperbuzz_dates 
        WHERE id > now() - interval '1 year' 
        ORDER BY finished ASC NULLS FIRST LIMIT 5;
    """
    dates = db.session.execute(date_sql)

    # set values to null so they are picked up by importer
    for date in dates:
        id_date = date[0]
        run_sql(
            db,
            """update doi_queue_paperbuzz_dates 
                       set enqueued=NULL, finished=NULL, started=NULL, dyno=NULL 
                       where id = '{id_date}'""".format(
                id_date=id_date
            ),
        )

    # run update script
    os.system("python doi_queue.py --dates --run")


if __name__ == "__main__":
    old_dates_update()
