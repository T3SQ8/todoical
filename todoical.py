#!/usr/bin/env python3

import re
from datetime import timedelta
from dateutil.parser import parse as dtparse
from icalendar import Calendar, Event

TODO_DATE_FORMAT = r'^(\d\d\d\d-\d\d-\d\d)( \d\d:\d\d)?(--(\d\d\d\d-\d\d-\d\d)?( ?\d\d:\d\d)?)?'

def parse_todo_file(todo_file):
    tasks_list = []
    with open(todo_file) as f:
        for line in f:
            if time := re.search(TODO_DATE_FORMAT, line):
                start_day, start_time, _, end_day, end_time = time.groups()
                summary = line[time.span()[1]:].strip()
                tasks_list.append({
                    'summary': summary,
                    'start_day': start_day,
                    'start_time': start_time,
                    'end_day': end_day,
                    'end_time': end_time,
                })
    return tasks_list


def main(todo_file, ical_file=None):
    tasks = parse_todo_file(todo_file)
    cal = todo_to_ical(tasks)
    if ical_file:
        write_to_file(cal, ical_file)
    else:
        print(pretty_format(cal))


def todo_to_ical(tasks):
    cal = Calendar()
    cal.add('prodid', '-//My calendar product//mxm.dk//') # for compliance
    cal.add('version', '2.0') # for compliance

    for task in tasks:
        event = Event()

        summary = task.get('summary')
        if '+hide' in summary: summary = '[REDACTED]'
        event.add('summary', summary)

        start_day  = task.get('start_day')
        start_time = task.get('start_time')
        end_day    = task.get('end_day')
        end_time   = task.get('end_time')

        if start_time: # Assuming start_day exists for all cases bellow
            t = dtparse(f'{start_day} {start_time}')
            event.add('dtstart', t)
        else:
            t = dtparse(start_day)
            event.add('dtstart', t.date())
        if end_day and end_time:
            t = dtparse(f'{end_day} {end_time}')
            event.add('dtend', t)
        elif end_day:
            t = dtparse(end_day)
            event.add('dtend', t.date()+timedelta(days=1)) # timedelta ends it beginning of next day
        elif end_time:
            t = dtparse(f'{start_day} {end_time}')
            event.add('dtend', t)
        elif start_time and not (end_day or end_time):
            event.add('dtend', t + timedelta(hours=1))
        cal.add_component(event)
    return cal


def write_to_file(cal, file):
    with open(file, 'wb') as f:
        f.write(cal.to_ical())

def pretty_format(cal):
    return cal.to_ical().decode("utf-8").replace('\r\n', '\n').strip()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='todo.txt file to iCalendar')
    parser.add_argument('todofile', metavar='FILE', help='input file(s)')
    parser.add_argument('-o', '--output', help='specify output iCalendar file')

    args = parser.parse_args()
    main(args.todofile, args.output)
