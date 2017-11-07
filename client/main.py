# Flask based backend
#
# To keep codebase as minimal as possible main.py contains all parts
# if the application.
#

import json
import datetime
import operator

from collections import namedtuple

from flask import Flask, request, render_template
from utils import Reader, Timeframe

app = Flask(__name__)
reader = Reader()
readers = {
    'today': reader.today,
    'yesterday': reader.yesterday,
    'week': reader.last_weeks
}


# View
@app.route('/')
def home():
    return render_template('main.html')


#
# API
#
@app.route('/records')
def records():
    '''Return JSON of records in a given time period'''
    days = request.args.get('days')

    if days == None:
        days = 1
    else:
        days = int(days)

    rec = reader.last_days(days)
    data = get_bar_records(rec, days)

    return json.dumps(data)


@app.route('/records/today')
def today_records():
    name = request.args.get('name')
    rec = reader.today()

    if name == None:
        data = get_bar_records(rec, 0)
    else:
        data = get_detailed_bar_records(rec, 0, name)

    return json.dumps(data)


@app.route('/records/yesterday')
def yesterday_records():
    name = request.args.get('name')
    rec = reader.yesterday()

    if name == None:
        data = get_bar_records(rec, 1)
    else:
        data = get_detailed_bar_records(rec, 1, name)

    return json.dumps(data)


@app.route('/records/week')
def week_records():
    name = request.args.get('name')
    rec = reader.last_weeks(1)

    if name == None:
        data = get_bar_records(rec, 7)
    else:
        data = get_detailed_bar_records(rec, 7, name)

    return json.dumps(data)


# TODO:
# Inherited bug. Month is more that 4 weeks, appropriate method should be
# added to the core of mlog.
@app.route('/records/month')
def month_records():
    name = request.args.get('name')
    rec = reader.last_weeks(4)

    if name == None:
        data = get_bar_records(rec, 4 * 7)
    else:
        data = get_detailed_bar_records(rec, 4 * 7, name)

    return json.dumps(data)


def get_bar_records(rec, range):
    data = Timeframe(rec).sum()

    for block in data:
        block.total_time = block.get_total_time()

    blocks = sorted(data, key=operator.attrgetter('total_time'))[::-1]

    apps = []
    for app in blocks:
        apps.append(dict(name=app.name, time=app.total_time))

    return {'status': 200, 'range': range, 'frames': apps}


def get_detailed_bar_records(rec, range, wname):
    data = Timeframe(rec).sum()

    for block in data:
        block.total_time = block.get_total_time()

    apps = []
    for block in data:
        if block.name.lower() != wname.lower():
            continue
        windows = []
        for window in block.windows:
            windows.append(dict(name=str(window.name), time=window.time))
        apps.append(
            dict(name=block.name, time=block.total_time, windows=windows))

    return {'status': 200, 'range': range, 'frames': apps}


def run():
    app.run(debug=True)
