from jobs import update_registry
from jobs import UpdateDbQueue
from date_range import DateRange
from mendeley_source import MendeleyData

# run with python doi_queue.py --dates --run
update_registry.register(UpdateDbQueue(
    job=DateRange.get_events,
    action_table="date_range"
))

update_registry.register(UpdateDbQueue(
    job=MendeleyData.run
))