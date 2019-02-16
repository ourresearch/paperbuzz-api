import os
from app import db
from util import run_sql


def old_dates_update():
    """
    This function updates data by pulling 15 old dates from the past 3 years.
    When run twice each day, the entire 3 years will update every 36 days.
    """

    # pick 15 oldest dates from past 3 years
    date_sql = """
        SELECT * FROM doi_queue_paperbuzz_dates 
        WHERE id > now() - interval '3 years' 
        ORDER BY finished ASC NULLS LAST LIMIT 15;
    """
    dates = db.session.execute(date_sql)

    # set values to null so they are picked up by importer
    for date in dates:
        id_date = date[0]
        run_sql(db, """update doi_queue_paperbuzz_dates 
                       set enqueued=NULL, finished=NULL, started=NULL, dyno=NULL 
                       where id = '{id_date}'""".format(id_date=id_date))

    # run update script
    os.system('python doi_queue.py --dates --run')


if __name__ == "__main__":
    old_dates_update()