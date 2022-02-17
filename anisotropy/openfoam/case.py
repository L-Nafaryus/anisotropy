# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import shutil
import re
import pathlib
import io
from lz.reversal import reverse as lz_reverse

from . import FoamFile


class FoamCase(object):
    def __init__(self, files: FoamFile | list[FoamFile] = None, path: str = None):
        
        self.path = path 
        self._backpath = None
        self._files = []
        
        if files is not None:
            self.add(files)
    
    def __repr__(self) -> str:
        content = [ file.object for file in self._files ]

        return "<FoamCase: {}>".format(", ".join(content) or None)

    def add(self, files: FoamFile | list[FoamFile]):
        if type(files) is not list:
            assert type(files) is FoamFile, "passed object is not a FoamFile"

            files = [ files ]

        for file in files:
            assert type(file) is FoamFile, "passed object is not a FoamFile"
            assert file.object is not None, "FoamFile object attribute is None"

            idn = self.contains(file.object)

            if idn is not None:
                self._files.pop(idn)
                self._files.append(file)
                
                return self
            
            self._files.append(file)
        
        return self
            
    def __add__(self, files: FoamFile | list[FoamFile]):
        return self.add(files)

    def contains(self, name: str) -> int | None:
        for n, file in enumerate(self._files):
            if file.object == name:
                return n

        return None

    def write(self, path: str = None):
        path = pathlib.Path(path or self.path or "")

        for file in self._files:
            path_ = path / (
                file.location + "/" + file.object 
                if file.location else file.object
            )

            file.write(path_.resolve())
    
    def read(self, path: str = None):
        path = pathlib.Path(path or self.path or "")

        for file in self._files:
            path_ = path / (
                file.location + "/" + file.object 
                if file.location else file.object
            )

            file.read(path_.resolve())

    def remove(self, path: str = None):
        path = pathlib.Path(path or self.path or "")

        for file in self._files:
            path_ = path / (
                file.location + "/" + file.object 
                if file.location else file.object
            )

            file.remove(path_.resolve())

    def clean(self, included: list = ["0", "constant", "system"]):
        regxs = [
            r"^\d+.\d+$",
            r"^\d+$",
            r"^processor\d+$",
            r"^log..+$",
            r"^.+.log$",
            r"^logs$",
            r"^postProcessing$",
            r"^polyMesh$"
        ]
        excluded = []

        for root, dirs, files in os.walk(os.path.abspath("")):
            for _dir in dirs:
                excluded += [ 
                    os.path.join(root, _dir) 
                    for regx in regxs if re.match(regx, _dir) 
                ]

            for file in files:
                excluded += [ 
                    os.path.join(root, file) 
                    for regx in regxs if re.match(regx, file) 
                ]

        for file in excluded:
            if os.path.split(file)[1] not in included and os.path.exists(file):
                if os.path.isdir(file):
                    shutil.rmtree(file)

                if os.path.isfile(file):
                    os.remove(file)

    def chdir(self, path: str = None):
        path = pathlib.Path(path or self.path or "").resolve()
        self._backpath = os.getcwd()
        
        os.chdir(path)
    
    def chback(self):
        path = pathlib.Path(self._backpath or "").resolve()

        os.chdir(path)

    def is_converged(self, path: str = None) -> None | bool:
        path = pathlib.Path(path or self.path or "").resolve()
        controlDict = FoamFile()

        if controlDict.exists(path / "system" / "controlDict"):
            controlDict.read(path / "system" / "controlDict")
        
        else:
            return None
        
        application = controlDict.get("application")

        if application is None:
            return None
        
        logfile = (
            path / f"{ application }.log" 
            if (path / f"{ application }.log").exists() else (path / f"log.{ application }")
        )
        status = False
        
        if logfile.exists():
            with open(logfile, "r") as infile:
                limit = 30

                for line in lz_reverse(infile, batch_size = io.DEFAULT_BUFFER_SIZE):
                    if not line.find("End") < 0:
                        status = True
                    
                    if limit <= 0:
                        status = False
                    
                    limit -= 1

        return status
