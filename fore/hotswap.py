import os
import logging
import threading

log = logging.getLogger(__name__)


class Hotswap(threading.Thread):
    def __init__(self, out, mod, *args, **kwargs):
        self.out = out
        self.mod = mod
        self.gen = mod.generate(*args, **kwargs)
        self.loaded = self.current_modtime
        self.args = args
        self.kwargs = kwargs

        threading.Thread.__init__(self)
        self.daemon = True

    @property
    def current_modtime(self):
        return os.path.getmtime(self.mod.__file__.replace("pyc", "py"))

    def run(self):
        while True:
            if self.current_modtime != self.loaded:
                log.info("Hot-swapping module: %s", self.mod.__name__)
                # self.mod = reload(self.mod)
                self.loaded = self.current_modtime
                self.gen = self.mod.generate(*self.args, **self.kwargs)
            self.handle(self.gen.next())

    def handle(self, elem):
        self.out(elem)
