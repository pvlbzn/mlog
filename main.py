from time import sleep
from threading import Timer
from AppKit import NSWorkspace as ws


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
    def __init__(self, interval, fn, *args, **kwargs):
        self.timer = None
        self.interval = interval
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()
    
    def run(self):
        self.is_running = False
        self.start()
        self.fn(*self.args, **self.kwargs)
    
    def start(self):
        if not self.is_running:
            self.timer = Timer(self.interval, self.run)
            self.timer.start()
            self.is_running = True
    
    def stop(self):
        self.timer.cancel()
        self.is_running = False

def active_app(*args):
    print(Application.get_active())


if __name__ == '__main__':
    t = TimerTask(1, active_app, None, None)