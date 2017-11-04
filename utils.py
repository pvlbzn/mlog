import os
import sqlite3
import operator
import datetime

from datetime import datetime as dt


class Timeframe:
    def __init__(self, containers):
        self.containers = containers

    def sum(self):
        '''Reduce all containers to one timeframe.
        
        Container represents some time interval, which is set in mlog.
        If interval is 60, then one container stores 60 seconds of information.
        Information collected in time intervals.

        To reduce all containers to one timeframe program needs to read
        all containers and find block duplicates. For example user used application
        x in container c1 for 60 seconds and in container c9 for 45 seconds.
        Therefore, in total user used application x for 105 seconds. Data about
        at what minute user used it is irrelevant.

        Application abstracted to Blocks. Each Block has Windows. For example
        Window "stackoverflow.com" is quite different from "facebook.com"
        by its value / meaning.
        '''
        # Move all blocks into one storage
        blocks = []
        for container in self.containers:
            blocks += container.blocks

        groups = self._group(blocks)
        data = self._sum(groups)

        return data

    def _group(self, blocks):
        '''Group blocks by name'''
        # blocks = sorted(blocks, key=operator.attrgetter('name'))

        # Linearly go though names and record all the possibilities
        names = []
        for block in blocks:
            if block.name in names:
                continue
            else:
                names.append(block.name)

        # Linearly create groups
        groups = []
        for name in names:
            groups.append(Block(None, None, name))

        # Go linearly through each block in blocks and place them into
        # group accordingly. This ops will take extra n space
        for block in blocks:
            for group in groups:
                if block.name == group.name:
                    group.windows += block.windows

        return groups

    def _sum(self, groups):
        '''Sum time for each group'''
        for group in groups:
            names = []
            for window in group.windows:
                if window.name in names:
                    continue
                else:
                    names.append(window.name)

            windows = []
            for name in names:
                windows.append(Window(None, None, name, 0))

            for window in group.windows:
                for item in windows:
                    if window.name == item.name:
                        item.time += window.time
            group.windows = windows

        return groups

    def print(self, threshold=5):
        '''Print timeframe in a formated way.

        Use threshold to clean output and get rid of useless noise. Threshold
        set in minutes. Standard threshold is 5 minutes. However, ignored
        outputs, if a window is ignored, will be calculated in total sum, too.

        For example Google Chrome can show 7 minutes in total, but no windows,
        if threshold is set to 5. Because user used two pages for 3 minutes,
        and one another page for a minute. Therefore windows themselfes arent
        displayed, but their sum will be shown.

        If container's, which is an application, total time is less then threshold
        it will be ignored complitely.
        
        Arguments:
            threshold: everything which is < threshold value will be ignored
            on printing
        '''
        data = self.sum()

        print(f'Threshold: {threshold}\n')

        for block in data:
            block.total_time = block.get_total_time()

        # Sort and reverse an order
        blocks = sorted(data, key=operator.attrgetter('total_time'))[::-1]

        for block in blocks:
            btime = block.total_time

            if btime < threshold * 60:
                continue

            if btime < 60:
                print(f'{block.name}:\t{btime} sec')
            else:
                btime /= 60
                print(f'{block.name}:\t{int(btime)} min')

            block.windows = sorted(
                block.windows, key=operator.attrgetter('time'))[::-1]
            for window in block.windows:
                wtime = int(window.time / 60)
                if wtime >= threshold:
                    print(f'\t* {wtime}\tmin \t{window.name}')
                else:
                    continue

            print()


class Container:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.blocks = []

    def add_block(self, block):
        assert type(block) is Block
        self.blocks.append(block)

    def __repr__(self):
        b = ''
        for block in self.blocks:
            b += block.__repr__()

        return f'Container(id: {self.id}, name: {self.name}, blocks: [{b}])\n'


class Block:
    def __init__(self, container_id, block_id, name):
        self.container_id = container_id
        self.block_id = block_id
        self.name = name
        self.total_time = 0
        self.windows = []

    def add_window(self, window):
        assert type(window) is Window
        self.windows.append(window)

    def is_window(self, window):
        for w in self.windows:
            if w.block_id == window.block_id and w.name == window.name and w.time == window.time and w.window_id == window.window_id:
                return True
        return False

    def is_window_name(self, name):
        for w in self.windows:
            if w.name == name:
                return True
        return False

    def add_to_name(self, name, time):
        for w in self.windows:
            if w.name == name:
                w.time += time
                return
        raise NameError('no such a name')

    def get_total_time(self):
        t = 0

        for window in self.windows:
            t += window.time

        return t

    def __repr__(self):
        w = ''
        for window in self.windows:
            w += window.__repr__()

        return f'Block(container_id: {self.container_id}, block_id: {self.block_id},' \
               f'name: {self.name}, total_time: {self.total_time}, windows: [\n{w}])\n'


class Window:
    def __init__(self, window_id, block_id, name, time):
        self.window_id = window_id
        self.block_id = block_id
        self.name = name
        self.time = time

    def __add__(self, other):
        assert type(other) is Window
        self.time += other.time

    def __repr__(self):
        return f'\tWindow(window_id: {self.window_id}, block_id: {self.block_id},' \
               f'name: {self.name}, time: {self.time})\n'


class Reader:
    def __init__(self, dbname='.mlog.db'):
        path = os.path.expanduser('~/') + dbname
        self.con, self.cur = self.init(path)
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
        return int(datetime.datetime.fromtimestamp(e))

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
                    w = Window(raw_window[0], raw_window[1], raw_window[2],
                               raw_window[3])
                    windows.append(w)

                for window in windows:
                    b.add_window(window)

                blocks.append(b)

            for block in blocks:
                c.add_block(block)

            containers.append(c)

        return containers
