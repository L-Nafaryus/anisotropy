import logging

from multiprocessing import Queue, Process, cpu_count
import socket


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

import copy

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

class Logger:
    def __init__(self, name, logpath):
        logging.basicConfig(
            level = logging.INFO, 
            format = "%(levelname)s: %(message)s",
            handlers = [
                logging.StreamHandler(),
                logging.FileHandler(logpath)
            ]
        )

        self.logger = logging.getLogger(name)
        self.warnings = 0
        self.errors = 0
        self.criticals = 0
        self.exceptions = 0
        
    def info(self, *args):
        self.logger.info(*args)

    def warning(self, *args):
        self.warnings += 1
        self.logger.warning(*args)

    def error(self, *args):
        self.errors += 1
        self.logger.error(*args)

    def critical(self, *args):
        self.criticals += 1
        self.logger.critical(*args)

    def exception(self, *args):
        self.exceptions += 1
        self.logger.exception(*args)

    def fancyline(self):
        self.logger.info("-" * 80)



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



