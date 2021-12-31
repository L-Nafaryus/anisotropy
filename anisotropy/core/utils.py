# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import logging
import copy
import time
from types import FunctionType


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


class struct:
    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            if type(args[0]) == dict:
                for (k, v) in args[0].items():
                    if type(v) == dict:
                        setattr(self, k, struct(v))
                    
                    else:
                        setattr(self, k, v)
        else:
            self.__dict__.update(kwargs)

    def __iter__(self):
        for k in self.__dict__:
            if type(getattr(self, k)) == struct:
                yield k, dict(getattr(self, k))

            else:
                yield k, getattr(self, k)

    def __str__(self):
        members = []

        for key in self.__dict__.keys():
            members.append(f"{ key } = ")

            if type(self.__dict__[key]) == str:
                members[len(members) - 1] += f"\"{ self.__dict__[key] }\""

            else: 
                members[len(members) - 1] += f"{ self.__dict__[key] }"
             
        return f"struct({', '.join(members)})"

    def __repr__(self):
        return str(self)


def deepupdate(target, src):
    for k, v in src.items():
        if isinstance(v, dict):
            if k not in target:
                target[k] = copy.deepcopy(v)

            else:
                deepupdate(target[k], v)

        else:
            target[k] = copy.copy(v)


def collapse(source, key = None, level = 0, sep = "_"):
    if isinstance(source, dict) and source:
        level = level + 1
        res = {}

        for k, v in source.items():
            ret, lvl = collapse(v, k, level)

            for kk, vv in ret.items():
                if level == lvl:
                    newkey = k

                else:
                    newkey = "{}{}{}".format(k, sep, kk)

                res.update({ newkey: vv })

        if level == 1:
            return res

        else:
            return res, level

    else:
        return { key: source }, level


def expand(source, sep = "_"):
    res = {}

    for k, v in source.items():
        if k.find(sep) == -1:
            res.update({ k: v })

        else:
            keys = k.split(sep)
            cur = res

            for n, kk in enumerate(keys):
                if not len(keys) == n + 1:
                    if not cur.get(kk):
                        cur.update({ kk: {} })

                    cur = cur[kk]

                else:
                    cur[kk] = v
    return res


def timer(func: FunctionType) -> (tuple, float):
    """(Decorator) Returns output of inner function and execution time
    
    :param func: inner function
    :type func: FunctionType

    :return: output, elapsed time
    :rtype: tuple(tuple, float)
    """

    def inner(*args, **kwargs):
        start = time.monotonic()
        ret = func(*args, **kwargs)
        elapsed = time.monotonic() - start

        return ret, elapsed

    return inner


class Timer(object):
    def __init__(self):
        self.update()

    def update(self):
        self.start = time.monotonic()
        
    def elapsed(self):
        return time.monotonic() - self.start
