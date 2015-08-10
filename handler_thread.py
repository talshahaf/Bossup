import threading, traceback
from collections import deque

class HandlerThread(threading.Thread):
    def __init__(self):
        super(HandlerThread, self).__init__()
        self.lck = threading.Condition()
        self.queue = deque(maxlen = 10)
        self.shouldStop = True
    
    def run(self):
        self.shouldStop = False
        while True:
            try:
                self.lck.acquire()
                while not bool(self.queue):
                    self.lck.wait()
                    if self.shouldStop:
                        return;
                i = self.queue.popleft()
                
            finally:
                self.lck.release()
            try:
                i[0](*i[1], **i[2])
            except Exception:
                print('exception in runnable')
                print(traceback.format_exc())
                
                
                
    def post(self, func, *args, **kwargs):
        try:
            self.lck.acquire()
            if not self.shouldStop:
                self.queue.append((func, args, kwargs))
                self.lck.notify()
        finally:
                self.lck.release()
                
    def StopThread(self):
        try:
            self.lck.acquire()
            self.shouldStop = True
            self.lck.notify()
        finally:
            self.lck.release()