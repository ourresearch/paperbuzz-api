import os
from datetime import datetime, timedelta
from app import db
from util import run_sql

def daily_update():
    # get date we want to add to database
    today = datetime.today()
    new_date = (today - timedelta(days=2)).strftime('%Y-%m-%d')

    # check if date already exists, if not then add it
    ts = new_date + ' 00:00:00.000000'
    existing_record = db.session.execute('select * from doi_queue_paperbuzz_dates where id = :val', {'val': ts})

    if existing_record.first() is None:
        q = """insert into doi_queue_paperbuzz_dates (select s as id, random() as rand, 
                false as enqueued, null::timestamp as finished, null::timestamp 
                as started, null::text as dyno FROM generate_series
                ('{start}'::timestamp, '{end}'::timestamp, '1 day'::interval) s);""".format(
                start=new_date, end=new_date)
        run_sql(db, q)

    # run update script
    os.system('python doi_queue.py --dates --run')

if __name__ == "__main__":
    daily_update()