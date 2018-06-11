import os
from datetime import datetime, timedelta
from app import db
from util import run_sql

def daily_update():
    # insert recent date into database
    today = datetime.today()
    new_date = (today - timedelta(days=2)).strftime('%Y-%m-%d')
    q = u"""insert into doi_queue_paperbuzz_dates (select s as id, random() as rand, 
            false as enqueued, null::timestamp as finished, null::timestamp 
            as started, null::text as dyno FROM generate_series
            ('{start}'::timestamp, '{end}'::timestamp, '1 day'::interval) s);""".format(
            start=new_date, end=new_date)
    run_sql(db, q)

    # run update script
    os.system('python doi_queue.py --dates --run')

if __name__ == "__main__":
    daily_update()