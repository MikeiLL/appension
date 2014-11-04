import threading

class Hotswap(threading.Thread):
    def __init__(self, out, gen):
        self.out = out
        self.gen = gen

        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        while True:
            self.out(next(self.gen))
