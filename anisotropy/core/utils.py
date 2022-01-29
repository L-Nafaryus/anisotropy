# -*- coding: utf-8 -*-

import logging
import time
import contextlib


class CustomFormatter(logging.Formatter):
    def __init__(self, colors: bool = True):
        self.colors = colors

    def applyColors(self, level: int, info: str, msg: str):
        grey = "\x1b[38;21m"
        yellow = "\x1b[33;21m"
        red = "\x1b[31;21m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        
        formats = {
            logging.DEBUG: grey + info + reset + msg,
            logging.INFO: grey + info + reset + msg,
            logging.WARNING: yellow + info + reset + msg,
            logging.ERROR: red + info + reset + msg,
            logging.CRITICAL: bold_red + info + reset + msg
        }

        return formats.get(level)

    def format(self, record):
        info = "[%(levelname)s %(processName)s %(asctime)s %(funcName)s]"  # [ %(processName)s ]
        msg = " %(message)s"
        
        if self.colors:
            log_fmt = self.applyColors(record.levelno, info, msg)

        else:
            log_fmt = info + msg

        time_fmt = "%d-%m-%y %H:%M:%S"
        formatter = logging.Formatter(log_fmt, time_fmt)

        return formatter.format(record)


def setupLogger(level: int, filepath: str = None):
    """Applies settings to root logger

    :param level: 
        Logging level (logging.INFO, logging.WARNING, ..)

    :param filepath: 
        Path to directory
    """

    logging.addLevelName(logging.INFO, "II")
    logging.addLevelName(logging.WARNING, "WW")
    logging.addLevelName(logging.ERROR, "EE")
    logging.addLevelName(logging.CRITICAL, "CC")
    
    streamhandler = logging.StreamHandler()
    streamhandler.setLevel(level)
    streamhandler.setFormatter(CustomFormatter())
    logging.root.addHandler(streamhandler)
    
    logging.root.setLevel(level)
    
    if filepath:
        filehandler = logging.FileHandler(filepath)
        filehandler.setLevel(logging.INFO)
        filehandler.setFormatter(CustomFormatter(colors = False))

        logging.root.addHandler(filehandler)


class Timer(object):
    def __init__(self):
        self.update()

    def update(self):
        self.start = time.monotonic()
        
    def elapsed(self):
        return time.monotonic() - self.start


class ErrorHandler(contextlib.AbstractContextManager):
    def __init__(self):
        self.error = ""
        self.returncode = 0
        self.traceback = None

    def __enter__(self):
        return self, self.handle

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.error = exc_value.args
            self.returncode = 1
            self.traceback = traceback

    def handle(self, obj):
        def inner(*args, **kwargs):
            try:
                output = obj(*args, **kwargs)
            
            except Exception as e:
                self.error = e.args
                self.returncode = 1
            
            else:
                return output
        
        return inner
