# Flask based backend
#
# To keep codebase as minimal as possible main.py contains all parts
# if the application.
#

import json

from flask import Flask, request
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
    return 'main'


#  API
@app.route('/records')
def records():
    '''Return JSON of records in a given time period.

    Response example:
        {
            'status': 200,
            'blocks': [
                {
                    'name': 'Google Chrome',
                    'time': 22115
                }
            ]
        }
    '''
    range = request.args.get('range')
    number = request.args.get('number')
    resolution = None

    if range == None:
        range = 'today'

    resolution = 'week' if range == 'week' else 'day'

    data = get_records(range, number, resolution)

    return json.dumps(data)


def get_records(range, number, resolution):
    rec = None

    if number == None:
        number = 1

    if range == 'day':
        rec = reader.last_days(number)
    elif range == 'week':
        rec = reader.last_weeks(number)

    tf = Timeframe(rec).sum()

    apps = []
    for frame in tf:
        apps.append(dict(name=frame.name, time=frame.total_time))

    res = {'status': 200, 'range': range, 'number': number, 'frames': apps}

    return res


def run():
    app.run(debug=True)
