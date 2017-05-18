
import yaml
import pickle
import pulp
import numpy as np
import itertools as it
from datetime import datetime, timedelta
from conference_scheduler.resources import Slot, Event
from conference_scheduler import scheduler

event_types = ['talk', 'workshop', 'plenary']
files = [
    'venues', 'days', 'session_times', 'talks', 'speaker_unavailability',
    'speaker_clashes']
definition = {}

for file in files:
    with open(f'definition/{file}.yml') as f:
        definition[file] = yaml.load(f)

session_times = definition['session_times']
slot_times = {
    event_type: [{
        'starts_at': slot_time['starts_at'],
        'duration': slot_time['duration'],
        'session_name': session_name}
        for session_name, slot_times in session_times[event_type].items()
        for slot_time in slot_times]
    for event_type in event_types}

venues = definition['venues']
days = {
    datetime.strptime(key, '%d-%b-%Y'): value
    for key, value in definition['days'].items()}
slots = {
    event_type: [
        Slot(
            venue=venue,
            starts_at=(day + timedelta(0, slot_time['starts_at'])).strftime('%d-%b-%Y %H:%M'),
            duration=slot_time['duration'],
            session=f"{day.date()} {slot_time['session_name']}",
            capacity=venues[venue]['capacity'])
        for venue, day, slot_time in it.product(
            venues, days, slot_times[event_type])
        if (event_type in venues[venue]['suitable_for'] and
            event_type in days[day]['event_types'])]
    for event_type in event_types}

talks = definition['talks']
events = {'talk': [
    Event(
        talk['title'], talk['duration'], demand=None,
        tags=talk.get('tags', None))
    for talk in talks]}

speaker_unavailability = definition['speaker_unavailability']
talk_unavailability = {
    talks.index(talk): [
        slots['talk'].index(slot)
        for period in periods
        for slot in slots['talk']
        if period['unavailable_from'] <= datetime.strptime(slot.starts_at, '%d-%b-%Y %H:%M') and
        period['unavailable_until'] >= datetime.strptime(slot.starts_at, '%d-%b-%Y %H:%M') + timedelta(0, slot.duration * 60)]
    for speaker, periods in speaker_unavailability.items()
    for talk in talks if talk['speaker'] == speaker}

for talk, unavailable_slots in talk_unavailability.items():
    events['talk'][talk].add_unavailability(
        *[slots['talk'][s] for s in unavailable_slots])

speaker_clashes = definition['speaker_clashes']
talk_clashes = {
    talks.index(talk): [
        talks.index(t) for s in clashing_speakers
        for t in talks if t['speaker'] == s]
    for speaker, clashing_speakers in speaker_clashes.items()
    for talk in talks if talk['speaker'] == speaker}

for talk, clashing_talks in talk_clashes.items():
    events['talk'][talk].add_unavailability(
        *[events['talk'][t] for t in clashing_talks])

solution = scheduler.solution(
    events['talk'], slots['talk'], solver=pulp.GLPK())
schedule_array = scheduler.solution_to_array(
    solution, events['talk'], slots['talk'])

conference = {
    'session_times': session_times,
    'venues': venues,
    'days': days,
    'slots': slots,
    'events': events,
}

with open('definition/conference.bin', 'wb') as file:
    pickle.dump(conference, file)

np.savetxt(
    'definition/schedule.csv', schedule_array.astype(int), fmt='%i',
    delimiter=',')
