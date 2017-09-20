from jobs import update_registry
from jobs import UpdateDbQueue
from date_range import DateRange


# run with python doi_queue.py --dates --run
update_registry.register(UpdateDbQueue(
    job=DateRange.get_events,
    action_table="date_range"
))