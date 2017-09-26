import sqlite3
import pygsheets
import time

from time import sleep
from objc import NULL
from threading import Timer
from AppKit import NSWorkspace as ws
from Foundation import NSAppleScript
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
from urllib.parse import urlparse


class Application():
    '''Active application wrapper
    
    Documentation:
        https://developer.apple.com/documentation/appkit/nsapplication
    
    '''
    def __init__(self, bid, pid, name, path, shigh, slow, key, tab=None):
        self.name   = name
        self.bid    = bid
        self.pid    = pid
        self.path   = path
        self.shigh  = shigh
        self.slow   = slow
        self.key    = key
        # Window can be an app window or a browser tab which is effectively
        # the same thing in mlog context.
        if name == 'Google Chrome' or name == 'Safari' or name == 'Firefox':
            self.window = tab.get_tab().parse_tab().domain
        else:
            self.window = self.get_window_name(self.pid)
    
    def __repr__(self):
        return f'Application(bid: {self.bid}, pid: {self.pid}, name: {self.name}, path: {self.path}' \
            f'shigh: {self.shigh}, slow: {self.slow}, window: {self.window}, key: {self.key})'

    def get_active(tab=None):
        '''Constructor function (not a method) of an Application
        
        Example

        app = Application.get_active()
        window = app.get_window_name()

        Returns:
            Current active application'''
        a = ws.sharedWorkspace().activeApplication()
        return Application(a['NSApplicationBundleIdentifier'],
                      a['NSApplicationProcessIdentifier'],
                      a['NSApplicationName'], a['NSApplicationPath'],
                      a['NSApplicationProcessSerialNumberHigh'],
                      a['NSApplicationProcessSerialNumberLow'],
                      a['NSWorkspaceApplicationKey'],
                      tab)
    
    def get_window_name(self, pid):
        '''Get a window name by PID.
        
        This method employs functionality of Quartz Window Server in order
        to get a name of the window.

        Documentation:
            https://developer.apple.com/documentation/coregraphics/quartz_window_services
        '''
        # List of currently opened windows
        l = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
        
        for window in l:
            if window['kCGWindowOwnerPID'] == pid:
                return window['kCGWindowName']
        
        return ''
        

class Browser():
    '''Browser utilities.

    Main task of Browser class is to find a name of currently opened tab
    and parse it.

    Current tab name exctracted using NSAppleScript, which is a part of Foundation
    framework. General form of a query string:
        tell application X
            get URL of active tab of first window
        end tell

    Documentation:
        https://developer.apple.com/documentation/foundation/nsapplescript
    '''
    def __init__(self):
        script_source = self._load_script()
        self.script = NSAppleScript.alloc().initWithSource_(script_source)
    
    def _load_script(self, path='./scripts/'):
        '''Load separate AppleScript file'''
        with open(path + 'browser.applescript', 'r') as f:
            data = f.read()
        
        return data
    
    def find_tab(self):
        '''Get a tab name from a current browser.

        Documentation:
            https://developer.apple.com/documentation/foundation/nsapplescript/1410034-executeandreturnerror?language=objc
        '''
        res = self.script.executeAndReturnError_(NULL)

        # res is a tuple of 2 objects: (NSAppleEventDescription, objc.NULL)
        if res[0] is None:
            return None
        
        return res[0].stringValue()


class Tab(Browser):
    '''Representation of relevant data from a browser's tab'''
    def __init__(self):
        '''Initialization should be performed semi-manually.
        
        Example:
            t = Tab().get_tab().parse_tab()
        
        Reason for this is that parent class has two expensive routines:
        _load_script:
            Loads script from a file - i/o
        NSAppleScript.alloc().initWithSource_():
            Allocates space for and compiles a script
        
        Therefore we want to make these two steps to be performed only once.
        '''
        super().__init__()
        self.url = None
        self.scheme = None
        self.domain = None
        self.path = None
    
    def get_tab(self):
        self.url = self.find_tab()
        return self
    
    def parse_tab(self):
        parser = urlparse(self.url)
        self.scheme = parser.scheme
        self.domain = parser.netloc
        self.path   = parser.path
        return self
    
    def __repr__(self):
        return f'Tab(url: {self.url}, scheme: {self.scheme}, domain: {self.domain}, path: {self.path})'


class TimerTask:
    def __init__(self, interval=5, fn=None):
        self.timer = None
        self.interval = interval
        self.fn = fn
        self.is_running = False
        self.start()
    
    def run(self):
        self.is_running = False
        self.start()
        self.fn()
    
    def start(self):
        if not self.is_running:
            self.timer = Timer(self.interval, self.run)
            self.timer.start()
            self.is_running = True
    
    def stop(self):
        self.timer.cancel()
        self.is_running = False


class Model:
    '''Simple persistent storage'''
    def __init__(self, dbname='time'):
        self.con, self.cur = self.init(dbname)
        self.create_schema()

    def init(self, n):
        con = sqlite3.connect(n, check_same_thread=False)
        cur = con.cursor()
        return con, cur

    def create_schema(self):
        containers = '''
        CREATE TABLE IF NOT EXISTS containers (
            container_id    integer primary key autoincrement,
            name            integer
        );
        '''
        blocks = '''
        create table if not exists blocks (
            block_id        integer primary key autoincrement,
            container_id    integer,
            name            text,
            foreign key (container_id) references containers (container_id)
        );
        '''
        windows = '''
        create table if not exists windows (
            window_id   integer primary key autoincrement,
            block_id    integer,
            name        text,
            time        integer,
            foreign key (block_id) references blocks (block_id)
        );
        '''
        self.cur.execute(containers)
        self.cur.execute(blocks)
        self.cur.execute(windows)
        self.con.commit()
    
    def drop(self):
        windows     = 'drop table windows;'
        blocks      = 'drop table blocks;'
        containers  = 'drop table containers;'
        self.cur.execute(windows)
        self.cur.execute(blocks)
        self.cur.execute(containers)
        self.con.commit()
    
    def add_container(self):
        q = 'insert into containers (name) values (?)'
        self.cur.execute(q, (self.name, ))

        fk = self.cur.lastrowid

        for block in self.blocks:
            self.add_block(block, fk)
    
    def add_block(self, block, fk):
        q = 'insert into blocks (container_id, name) values (?, ?)'
        self.cur.execute(q, (fk, block.name))

        fk = self.cur.lastrowid

        for window in block.windows:
            self.add_window(window, fk)
    
    def add_window(self, window, fk):
        q = 'insert into windows (block_id, name, time) values (?, ?, ?)'
        self.cur.execute(q, (fk, window.name, window.time))

        self.con.commit()


class Sheet():
    '''Experimental class for storing rows into Google Shread Sheets.
    
    Development is stopped for now due to insufficient response speed
    from sheets.
    '''
    def __init__(self):
        auth = pygsheets.authorize(service_file='api.json')
        self.data = auth.open('mlog').sheet1
        self.index = self._row_count()
    
    def _row_count(self):
        return len(self.data.get_all_records(head=0))
    
    def insert(self, entry):
        self.index += 1
        self.data.update_row(self.index, entry)


class Log:
    '''Class for producing a log instances.
    
    Log is a simple, atomic information about a currently running application.
    '''
    def __init__(self, app):
        self.name = app.name
        self.window = app.window
        self.epoch = time.time()
        self.time, self.date = self.timestamp()

    def __repr__(self):
        return f'Log(date: "{self.date}", time: "{self.time}",' \
               f' name: "{self.name}", window: "{self.window}")'

    def timestamp(self):
        t = time.strftime("%H:%M:%S")
        d = time.strftime("%d/%m/%Y")
        return t, d


class Container(Model):
    '''Container class contains and manages blocks.
    
    
    '''
    class Block:
        '''Block class represent an application and its windows.'''
        class Window:
            '''Window class represent an application window.
            
            Application may has {1, .., n} windows. '''
            def __init__(self, name, time):
                self.name = name
                self.time = int(time)

        def __init__(self, name):
            self.name = name
            self.windows = []
            
        def add_window(self, name, time):
            for window in self.windows:
                if window.name == name:
                    window.time += int(time)
                    return
            
            self.windows.append(Container.Block.Window(name, time))
        
        def __repr__(self):
            s = ''
            for window in self.windows:
                s += f'[name: {window.name}, time: {window.time}],'
            return f'Block(name: {self.name}, windows: {s})'
    
    def __init__(self, interval=5):
        super().__init__()
        self.interval = interval
        self.name = self._get_name()
        self.blocks = []
    
    def _get_name(self):
        return int(time.time())
    
    def add(self, log):
        '''Get a log and put it into corresponding block. If block doesnt exist,
        create it.'''
        for block in self.blocks:
            if block.name == log.name:
                # block exists, add time to it
                block.add_window(log.window, self.interval)
                return
        
        b = Container.Block(log.name)
        b.add_window(log.window, self.interval)
        self.blocks.append(b)
    
    def dump(self):
        '''Write Containers data into a persistent storage.
        
        After dumping, deallocate all old blocks, since they are already stored
        and start to write new blocks.
        '''
        self.add_container()
        del self.blocks[:]
    
    def __repr__(self):
        s = ''
        for block in self.blocks:
            s += block.__repr__()
        return f'Container(name: {self.name}, blocks: {s})'


class Runner:
    def __init__(self):
        self.interval = 5
        self.iteration = 1
        # Load an applescript and compile it during Tab initialization
        self.tab = Tab()
        self.container = Container(self.interval)
        self.task = None
    
    def start(self):
        def activate():
            log = Log(Application.get_active(self.tab))
            self.container.add(log)
            print(self.container)

            if self.iteration % 60 == 0:
                self.container.dump()
                self.iteration = 0
            
            self.iteration += 1
        
        self.task = TimerTask(self.interval, activate)
    
    def stop(self):
        self.task.stop()
    

if __name__ == '__main__':
    r = Runner()
    r.start()