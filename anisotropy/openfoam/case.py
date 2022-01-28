# -*- coding: utf-8 -*-

import os, shutil
import re
from copy import deepcopy

from . import FoamFile


class FoamCase(object):
    def __init__(self, foamfiles: list = None, path: str = None):
        
        self.path = path or os.path.abspath("")

        if foamfiles:
            self.extend(foamfiles)
            
    def __enter__(self):
        self.__curpath = os.path.abspath("")
        os.chdir(self.path)
        return

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.__curpath)
        self.__curpath = None

    def append(self, ff: FoamFile):
        if FoamFile in ff.__class__.mro():
            setattr(self, ff.header["object"], deepcopy(ff))

        else:
            raise Exception("Trying to put not a FoamFile to FoamCase.")

    def extend(self, foamfiles: list):
        for ff in foamfiles:
            self.append(ff)

    def write(self):
        for value in self.__dict__.values():
            if FoamFile in value.__class__.mro():
                value.write(self.path)

    def read(self):
        for value in self.__dict__.values():
            if FoamFile in value.__class__.mro():
                value.read()

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
                excluded += [ os.path.join(root, _dir) for regx in regxs if re.match(regx, _dir) ]

            for file in files:
                excluded += [ os.path.join(root, file) for regx in regxs if re.match(regx, file) ]

        for file in excluded:
            if os.path.split(file)[1] not in included and os.path.exists(file):
                if os.path.isdir(file):
                    shutil.rmtree(file)

                if os.path.isfile(file):
                    os.remove(file)
            

