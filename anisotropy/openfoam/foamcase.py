# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from anisotropy.openfoam.foamfile import FoamFile

class ControlDict(FoamFile):
    def __init__(self):
        ff = FoamFile(
            "system/controlDict",
            _location = "system"
        )
        self.header = ff.header
        self.content = {
            "application": "simpleFoam",
            "startFrom": "startTime",
            "startTime": 0,
            "stopAt": "endTime",
            "endTime": 2000,
            "deltaT": 1,
            "writeControl": "timeStep",
            "writeInterval": 100,
            "purgeWrite": 0,
            "writeFormat": "ascii",
            "writePrecision": 6,
            "writeCompression": "off",
            "timeFormat": "general",
            "timePrecision": 6,
            "runTimeModifiable": True
        }
