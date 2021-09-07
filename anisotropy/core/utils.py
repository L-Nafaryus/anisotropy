# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import logging

from multiprocessing import Queue, Process, cpu_count
import socket
import copy
import time
from types import FunctionType
import os

class CustomFormatter(logging.Formatter):
    def _getFormat(self, level: int):
        grey = "\x1b[38;21m"
        yellow = "\x1b[33;21m"
        red = "\x1b[31;21m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        format = "[ %(asctime)s ] [ %(processName)s ] [ %(levelname)s ] %(message)s"

        formats = {
            logging.DEBUG: grey + format + reset,
            logging.INFO: grey + format + reset,
            logging.WARNING: yellow + format + reset,
            logging.ERROR: red + format + reset,
            logging.CRITICAL: bold_red + format + reset
        }

        return formats.get(level)

    def format(self, record):
        log_fmt = self._getFormat(record.levelno)
        time_fmt = "%H:%M:%S %d-%m-%y"
        formatter = logging.Formatter(log_fmt, time_fmt)

        return formatter.format(record)


def setupLogger(logger, level: int, filepath: str = None):
    """Applies settings to logger

    :param logger: 
        Instance of :class:`logging.Logger`
    
    :param level: 
        Logging level (logging.INFO, logging.WARNING, ..)

    :param filepath: 
        Path to directory
    """
    logger.handlers = []
    logger.setLevel(level)

    streamhandler = logging.StreamHandler()
    streamhandler.setLevel(level)
    streamhandler.setFormatter(CustomFormatter())
    logger.addHandler(streamhandler)

    if filepath:
        if not os.path.exists(filepath):
            os.makedirs(filepath, exist_ok = True)

        filehandler = logging.FileHandler(
            os.path.join(filepath, "{}.log".format(logger.name))
        )
        filehandler.setLevel(level)
        filehandler.setFormatter(CustomFormatter())
        logger.addHandler(filehandler)


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
            if not k in target:
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

            for kk,vv in ret.items():
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

#if os.path.exists(env["CONFIG"]):
#    config = toml.load(env["CONFIG"])

#    for restricted in ["ROOT", "BUILD", "LOG", "CONFIG"]:
#        if config.get(restricted):
#            config.pop(restricted)

    # TODO: not working if custom config empty and etc
#    for m, structure in enumerate(config["structures"]):
#        for n, estructure in enumerate(env["structures"]):
#            if estructure["name"] == structure["name"]:
#                deepupdate(env["structures"][n], config["structures"][m])

#    config.pop("structures")
#    deepupdate(env, config)

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
        self.start = time.monotonic()

    def elapsed(self):
        return time.monotonic() - self.start


def queue(cmd, qin, qout, *args):
    
    while True:
        # Get item from the queue
        pos, var = qin.get()
        
        # Exit point 
        if pos is None:
            break

        # Execute command
        res = cmd(*var, *args)

        # Put results to the queue
        qout.put((pos, res))

    return


def parallel(np, var, cmd):

    varcount = len(var)

    processes = []
    nprocs = np if np <= cpu_count() else cpu_count()
    
    qin = Queue(1)
    qout = Queue()
    
    # Create processes
    for n in range(nprocs):
        pargs = [cmd, qin, qout]

        p = Process(target = queue, args = tuple(pargs))

        processes.append(p)
    
    # Start processes
    for p in processes:
        p.daemon = True
        p.start()

    # Fill queue
    for n in range(varcount):
        qin.put((n, var[n]))

    for _ in range(nprocs):
        qin.put((None, None))
    
    # Get results
    results = [[] for n in range(varcount)]

    for n in range(varcount):
        index, res = qout.get()
        
        results[index] = res
    
    # Wait until each processor has finished
    for p in processes:
        p.join()

    return results

    
def portIsFree(address, port):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((address, port)) == 0



