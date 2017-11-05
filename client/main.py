# Flask based backend
#
# To keep codebase as minimal as possible main.py contains all parts
# if the application.
#

import json
import datetime

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
    rec = reader.today()
    data = get_bar_records(rec, 0)

    return json.dumps(data)


@app.route('/records/yesterday')
def yesterday_records():
    rec = reader.yesterday()
    data = get_bar_records(rec, 1)

    return json.dumps(data)


@app.route('/records/week')
def week_records():
    rec = reader.last_weeks(1)
    data = get_bar_records(rec, 7)

    return json.dumps(data)


# TODO:
# Inherited bug. Month is more that 4 weeks, appropriate method should be
# added to the core of mlog.
@app.route('/records/month')
def month_records():
    rec = reader.last_weeks(4)
    data = get_bar_records(rec, 4 * 7)

    return json.dumps(data)


def get_bar_records(rec, range):
    tf = Timeframe(rec).sum()
    '''
    Record example:

    Container(id: 3413, name: 1509453500, blocks: [
        Block(container_id: 3413, block_id: 4260,name: Google Chrome, total_time: 0, windows: [
            Window(window_id: 5701, block_id: 4260,name: localhost:8888, time: 20)
            Window(window_id: 5702, block_id: 4260,name: b'', time: 5)
            Window(window_id: 5703, block_id: 4260,name: stackoverflow.com, time: 10)
            Window(window_id: 5704, block_id: 4260,name: encrypted.google.com, time: 5)
            Window(window_id: 5705, block_id: 4260,name: pandas.pydata.org, time: 20)
        ])
    ])

    So far windows are irrelevant, only block matters.
    '''

    apps = []
    for frame in tf:
        apps.append(dict(name=frame.name, time=frame.total_time))

    res = {'status': 200, 'range': range, 'frames': apps}

    print(res)

    return res


class Day:
    def __init__(self, records):
        apps = self._get_applications(records)
        self.buckets = self._timesort_applications(apps)

    def _get_applications(self, records):
        '''Format records into dictionaries of relevant data.
        
        Example:
            {
                'timestamp':    int,
                'name':         string,
                'time:          int
            }

        '''
        apps = []

        for container in records:
            for block in container.blocks:
                apps.append({
                    'timestamp': container.name,
                    'name': block.name,
                    'time': block.get_total_time()
                })

        return apps

    def _timesort_applications(self, apps):
        buckets = {
            '0': [],
            '1': [],
            '2': [],
            '3': [],
            '4': [],
            '5': [],
            '6': [],
            '7': [],
            '8': [],
            '9': [],
            '10': [],
            '11': [],
            '12': [],
            '13': [],
            '14': [],
            '15': [],
            '16': [],
            '17': [],
            '18': [],
            '19': [],
            '20': [],
            '21': [],
            '22': [],
            '23': []
        }

        for app in apps:
            dt = datetime.datetime.fromtimestamp(app['timestamp'])
            buckets[str(dt.hour)].append(app)

        return buckets

    def reduce(self):
        # Each hour bucket must contain no name duplicates
        pass


def run():
    app.run(debug=True)
