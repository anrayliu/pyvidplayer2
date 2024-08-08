
"""
A backward-compatible partial implementation of logging.
The name is long so as not to interfere with the system's package.
"""
from __future__ import print_function
import sys


class Logger:
    """A backward-compatible partial implementation of logging.Logger
    without logging levels (everything is shown)
    """
    def __init__(self, name):
        if name is None:
            name = __name__
        self.name = name

    def warning(self, msg):
        print(msg, file=sys.stderr)

    def error(self, msg):
        print(msg, file=sys.stderr)

    def critical(self, msg):
        print(msg, file=sys.stderr)

    def fatal(self, msg):
        print(msg, file=sys.stderr)

    def exception(self, ex):
        print("{}: {}".format(type(ex).__name__, ex), file=sys.stderr)

    def info(self, msg):
        print(msg, file=sys.stderr)


try:
    from logging import getLogger
except ImportError:  # Python 2
    # ^ This exception works on Python 3 as well,
    #   since its ModuleNotFoundError is a subclass of ImportError
    def getLogger(name):
        """A backward-compatible replacement for logging.getLogger"""
        return Logger(name=name)
