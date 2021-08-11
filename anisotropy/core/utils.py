import logging

from multiprocessing import Queue, Process, cpu_count
import socket
import copy
import time
from types import FunctionType
import os

class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[ %(asctime)s ] [ %(levelname)s ] %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)

        return formatter.format(record)

def setupLogger(logger, level: int):
    logger.setLevel(level)

    sh = logging.StreamHandler()
    sh.setLevel(level)
    sh.setFormatter(CustomFormatter())

    fh = logging.FileHandler(os.path.join("logs", logger.name))
    fh.setLevel(level)
    fh.setFormatter(CustomFormatter())

    logger.addHandler(sh)
    logger.addHandler(fh)

    return logger

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
        #if type(v) == list:
        #    if not k in target:
        #        target[k] = copy.deepcopy(v)
        #    else:
        #        target[k].extend(v)
        if type(v) == dict:
            if not k in target:
                target[k] = copy.deepcopy(v)
            else:
                deepupdate(target[k], v)
        #elif type(v) == set:
        #    if not k in target:
        #        target[k] = v.copy()
        #    else:
        #        target[k].update(v.copy())
        else:
            target[k] = copy.copy(v)



def timer(func: FunctionType) -> (tuple, float):
    """(Decorator) Returns output of inner function and execution time
    
    :param func: inner function
    :type: FunctionType

    :return: output, elapsed time
    :rtype: tuple(tuple, float)
    """
    def inner(*args, **kwargs):
        start = time.monotonic()
        ret = func(*args, **kwargs)
        elapsed = time.monotonic() - start

        return ret, elapsed

    return inner



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
    
    logging.info("cpu count: {}".format(np))
    logging.info("var: {}".format(var))
    logging.info("cmd: {}".format(cmd))

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



