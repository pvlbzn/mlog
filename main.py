import sqlite3

from time import sleep
from objc import NULL
from threading import Timer
from AppKit import NSWorkspace as ws
from Foundation import NSAppleScript
from urllib.parse import urlparse


class Application():
    '''Active application wrapper
    
    Documentation:
        https://developer.apple.com/documentation/appkit/nsapplication
    
    '''
    def __init__(self, bid, pid, name, path, shigh, slow, key):
        self.bid = bid
        self.pid = pid
        self.name = name
        self.path = path
        self.shigh = shigh
        self.slow = slow
        self.key = key
    
    def __repr__(self):
        return f'bid: {self.bid}, pid: {self.pid}, name: {self.name}, path: {self.path}' \
            f'shigh: {self.shigh}, slow: {self.slow}, key: {self.key}'

    def get_active():
        a = ws.sharedWorkspace().activeApplication()
        return Application(a['NSApplicationBundleIdentifier'],
                      a['NSApplicationProcessIdentifier'],
                      a['NSApplicationName'], a['NSApplicationPath'],
                      a['NSApplicationProcessSerialNumberHigh'],
                      a['NSApplicationProcessSerialNumberLow'],
                      a['NSWorkspaceApplicationKey'])


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


def active_app():
    print(Application.get_active())


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
    
    def get_tab_name(self):
        '''Get a tab name from a current browser.

        Documentation:
            https://developer.apple.com/documentation/foundation/nsapplescript/1410034-executeandreturnerror?language=objc
        '''
        res = self.script.executeAndReturnError_(NULL)

        # res is a tuple of 2 objects: (NSAppleEventDescription, objc.NULL)
        if res[0] is None:
            return None
        
        return res[0].stringValue()

    def get_domain_name(self):
        url = self.get_tab_name()
        return urlparse(url).netloc


class Model:
    '''Simple persistent storage'''
    def __init__(self, dbname='time'):
        self.con, self.cur = self.init(dbname)

    def init(self, n):
        con = sqlite3.connect(n)
        cur = con.cursor()
        return con, cur

    def check(self):
        q = '''
        create table if not exists time (
            id          integer primary key autoincrement,
            application text,
            description text,
            duration    integer
        );
        '''
        self.cur.execute(q)
        self.con.commit()
    
    def drop(self):
        q = 'drop table time;'
        self.cur.execute(q)
        self.con.commit()
    
    def add_entry(self, aname, desc, duration):
        q = '''
        insert into time (
            application, description, duration
        ) values (?, ?, ?)
        '''
        self.cur.execute(q, (aname, desc, duration))
        self.con.commit()





if __name__ == '__main__':
    t = TimerTask(1, active_app)