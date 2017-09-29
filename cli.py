import sqlite3
import datetime

from datetime import datetime as dt


class Container:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.blocks = []
    
    def add_block(self, block):
        assert type(block) is Block
        self.blocks.append(block)


class Block:
    def __init__(self, container_id, block_id, name):
        self.container_id = container_id
        self.block_id = block_id
        self.name = name
        self.windows = []
    
    def add_window(self, window):
        assert type(window) is Window
        self.windows.append(window)

class Window:
    def __init__(self, window_id, block_id, name, time):
        self.window_id = window_id
        self.block_id = block_id
        self.name = name
        self.time = time
    
    def __repr__(self):
        return f'Window(block_id: {self.block_id}, name: "{self.name}", time: {self.time})\n'


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
        return self._get_records(epoch)

    def yesterday(self):
        return self.last_days(1)

    def last_days(self, n):
        x = self._zero(self.now) - datetime.timedelta(days=n)
        y = self._zero(self.now)
        x_epoch = int(x.timestamp())
        y_epoch = int(y.timestamp())
        return self._get_records(x_epoch, y_epoch)

    def month(self):
        return self.last_weeks(4)

    def last_weeks(self, n):
        x = self._zero(self.now) - datetime.timedelta(weeks=n)
        y = self.now
        x_epoch = int(x.timestamp())
        y_epoch = int(y.timestamp())
        return self._get_records(x_epoch, y_epoch)

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

        containers = []

        for raw_container in self.cur.fetchall():
            # for each container from containers table
            c = Container(raw_container[0], raw_container[1])

            q = 'select * from blocks where container_id = (?);'
            self.cur.execute(q, (c.id, ))

            blocks = []
            for raw_block in self.cur.fetchall():
                # for each block from blocks table
                b = Block(c.id, raw_block[0], raw_block[2])

                q = 'select * from windows where block_id = (?);'
                self.cur.execute(q, (b.block_id, ))

                windows = []
                for raw_window in self.cur.fetchall():
                    # for each window from windows table
                    w = Window(raw_window[0], raw_window[1], raw_window[2], raw_window[3])
                    windows.append(w)
                
                for window in windows:
                    b.add_window(window)
                
                blocks.append(b)
            
            for block in blocks:
                c.add_block(block)

            containers.append(c)
        
        return containers


if __name__ == '__main__':
    r = Reader()
    r.today()
    # containers, blocks, windows = r.today()
    # t = Timeframe.create(containers, blocks, windows)
