# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import os
import toml
from copy import deepcopy
from numpy import arange, array


class Config(object):
    def __init__(self):
        self.content = {}
        self.options = {},
        self.cases = None

    def __getitem__(self, key):
        return self.options[key]

    def __setitem__(self, key, value):
        self.options[key] = value

    def __delitem__(self, key):
        del self.options[key]

    def update(self, **kwargs):
        self.options.update(**kwargs)

    def __len__(self):
        return len(self.options)

    def __iter__(self):
        for key in self.options:
            yield key

    def load(self, filename: str):
        path = os.path.abspath(filename)

        if not os.path.exists(path):
            raise FileNotFoundError(path)

        self.content = toml.load(path)
        self.options = deepcopy(self.content["options"])

    def dump(self, filename: str):
        path = os.path.abspath(filename)
        ext = os.path.splitext(path)[1]

        if not ext == ".toml":
            path += ".toml"

        os.makedirs(os.path.split(path)[0], exist_ok = True)

        with open(path, "w") as io:
            toml.dump(self.content, io, encoder = toml.TomlNumpyEncoder())

    def expand(self):
        self.cases = []

        #   Expand structures for each direction and each theta
        for structure in self.content["structures"]:
            thetaA = arange(
                structure["theta"][0], 
                structure["theta"][1] + structure["thetaStep"], 
                structure["thetaStep"]
            )
            directionA = array(structure["directions"], dtype = float) 

            for direction in directionA:
                for theta in thetaA:
                    self.cases.append({
                        "label": structure["label"],
                        "theta": theta,
                        "thetaStep": structure["thetaStep"],
                        "direction": direction,
                        "r0": structure["r0"],
                        "filletsEnabled": structure["filletsEnabled"]
                    })


class DefaultConfig(Config):
    def __init__(self):
        Config.__init__(self)

        self.content = {
            "options": {
                "nprocs": 1,
                "stage": "all",
                "overwrite": False,

            },
            "structures": []
        }
        self.options = deepcopy(self.content["options"])

        labels = ["simple", "bodyCentered", "faceCentered"]
        thetas = array([[0.01, 0.28], [0.01, 0.17], [0.01, 0.13]], dtype = float)

        for label, theta in zip(labels, thetas):
            self.content["structures"].append({
                "label": label,
                "theta": theta,
                "thetaStep": 0.01,
                "directions": array([[1, 0, 0], [0, 0, 1], [1, 1, 1]], dtype = float),
                "r0": 1,
                "filletsEnabled": True
            })
