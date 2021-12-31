# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.


from multiprocessing import Queue, Process
import dill


class ParallelRunner(object):
    def __init__(self, nprocs: int = 1, daemon: bool = True):
        self.nprocs = nprocs
        self.daemon = daemon
        
        self.processes = []
        self.queueInput = Queue(maxsize = 1)
        self.queueOutput = Queue()
        
        self.__pos = -1
        self.output = []
    
    def append(self, command, args = [], kwargs = {}):
        self.__pos += 1
        self.queueInput.put(dill.dumps((self.__pos, command, args, kwargs)))
        
    def extend(self, commands: list, args: list = [], kwargs: list = []):
        for command, cargs, ckwargs in zip(commands, args, kwargs):
            self.append(command, cargs, ckwargs)
    
    @staticmethod
    def queueRelease(queueInput, queueOutput):
        while True:
            pos, command, args, kwargs = dill.loads(queueInput.get())
            
            if pos is None or command is None:
                break
                
            output = command(*args, **kwargs)
            
            queueOutput.put((pos, output))
    
    def start(self):
        for n in range(self.nprocs):
            self.processes.append(Process(
                target = self.queueRelease, 
                args = (self.queueInput, self.queueOutput),
                name = f"worker-{ n + 1 }"
            ))
        
        for proc in self.processes:
            proc.daemon = self.daemon
            proc.start()
        
    def wait(self):
        for _ in range(self.nprocs):
            self.append(None)
        
        self.output = [ [] for _ in range(self.queueOutput.qsize()) ]
        
        for _ in range(self.queueOutput.qsize()):
            pos, output = self.queueOutput.get()
            self.output[pos] = output
        
        for proc in self.processes:
            proc.join()
        
        self.__pos = -1
        




