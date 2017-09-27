import sqlite3
import datetime

from datetime import datetime as dt

# find yesterday's epoch and select from sql where name is >= than that


class Reader:
    def __init__(self, dbname='time'):
        self.con, self.cur = self.init(dbname)
        self.now = dt.now()

    def init(self, n):
        con = sqlite3.connect(n)
        cur = con.cursor()
        return con, cur

    def ttoe(self, t):
        '''Datetime to epoch'''
        return int(t.timestamp())

    def etot(self, e):
        '''Epoch to datetime'''
        return int(datetime.datetime.fromtimestamp(epoch))

    def today(self):
        '''Get records from today.
        
        For most people a calendar alias "today" means a time subset from
        a time series where starting point is a current date time minus time
        and no ending point, or practically point is the current date time.'''
        # zero time from date time
        today = self._zero(self.now)
        epoch = int(today.timestamp())
        self._get_records(epoch)

    def yesterday(self):
        self.last_days(1)

    def last_days(self, n):
        x = self._zero(self.now) - datetime.timedelta(days=n)
        y = self._zero(self.now)
        x_epoch = int(x.timestamp())
        y_epoch = int(y.timestamp())
        self._get_records(x_epoch, y_epoch)

    def month(self):
        self.last_weeks(4)

    def last_weeks(self, n):
        x = self._zero(self.now) - datetime.timedelta(weeks=n)
        y = self.now
        x_epoch = int(x.timestamp())
        y_epoch = int(y.timestamp())
        self._get_records(x_epoch, y_epoch)

    def _zero(self, t):
        '''Remove hours, minutes, seconds from a datetime'''
        delta = datetime.timedelta(
            hours=t.hour, minutes=t.minute, seconds=t.second)

        return (t - delta)

    def _get_records(self, x, y=None):
        '''Get records from a database from x to y.
        
        Arguments:
            x: epoch time, starting point
            y: epoch time, ending point, optional
        
        If y argument isn't given that implies that y is now.
        '''
        if type(x) != int:
            x = int(x)

        if y == None:
            y = int(self.now.timestamp())

        q = 'select * from containers where name >= (?) and name <= (?);'
        self.cur.execute(q, (x, y))
        res = self.cur.fetchall()
        print(res)


if __name__ == '__main__':
    r = Reader()
    r.today()
    r.yesterday()