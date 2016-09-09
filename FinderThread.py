import threading

import time


class FinderThread(object):
    def __init__(self, finder):
        self.finder = finder
        self.event = threading.Event()
        self.event.set()
        self.thread = threading.Thread(target=self.callable, args=(self.event,))
        self.thread.daemon = True

    def callable(self, event):
        while event.is_set():
            self.finder.process()
            inv = self.finder.interval
            print 'sleep'
            while inv > 0:
                if not event.is_set():
                    break
                inv -= 1
                time.sleep(1)
            print 'wake'

    def start(self):
        self.thread.start()

    def restart(self):
        print 'Thread restart'
        self.stop()
        self.finder.from_config()
        self.event.set()
        self.thread = threading.Thread(target=self.callable, args=(self.event,))
        self.thread.start()

    def stop(self):
        self.event.clear()
        self.thread.join()
