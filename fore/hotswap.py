import os
import logging
import threading

log = logging.getLogger(__name__)


class Hotswap(threading.Thread):
    def __init__(self, out, mod, *args, **kwargs):
        self.out = out
        self.gen = mod.generate(*args, **kwargs)

        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        while True:
            self.handle(self.gen.next())

    def handle(self, elem):
        self.out(elem)
