from AppKit import NSWorkspace as ws


class Window():
    '''Active application wrapper'''
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
        return Window(a['NSApplicationBundleIdentifier'],
                      a['NSApplicationProcessIdentifier'],
                      a['NSApplicationName'], a['NSApplicationPath'],
                      a['NSApplicationProcessSerialNumberHigh'],
                      a['NSApplicationProcessSerialNumberLow'],
                      a['NSWorkspaceApplicationKey'])


if __name__ == '__main__':
    w = Window.get_active()
    print(w)
