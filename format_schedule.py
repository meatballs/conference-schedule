import pickle
import pandas as pd

with open('definition/conference.bin', 'rb') as file:
    conference = pickle.load(file)

slots = conference['slots']['talk']
events = conference['events']['talk']


def scheduled_events():
    """The scheduled event index (or None) for each slot"""
    scheduled_events = [None for _ in range(len(slots))]
    for item in conference['solution']:
        scheduled_events[item[1]] = item[0]
    return scheduled_events


def slots_by_venue(venue):
    """The slots for a given venue"""
    return [
        slots.index(slot)
        for slot in conference['slots']['talk'] if slot.venue == venue]


def scheduled_events_by_venue(venue):
    """The scheduled event title (or None) for each slot for a given venue"""
    return [scheduled_events()[slot] for slot in slots_by_venue(venue)]

programme = {
    venue: [
        events[e].name if e is not None else None
        for e in scheduled_events_by_venue(venue)]
    for venue, details in conference['venues'].items()
    if 'talk' in details['suitable_for']
}


df = pd.DataFrame.from_dict(programme)
print(df.head())
