# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import os
import toml
import copy
import numpy as np


class Config(object):
    def __init__(self):
        self.content = {}
        self.options = {}
        self.params = {}
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
        self.options = copy.deepcopy(self.content["options"])
        self.content.pop("options")

    def dump(self, filename: str):
        path = os.path.abspath(filename)
        ext = os.path.splitext(path)[1]

        if not ext == ".toml":
            path += ".toml"

        os.makedirs(os.path.split(path)[0], exist_ok = True)

        self.content.update(options = self.options)

        with open(path, "w") as io:
            toml.dump(self.content, io, encoder = toml.TomlNumpyEncoder())

    def minimize(self):
        self.content = None
        self.cases = None

    def purge(self):
        self.minimize()
        self.params = None

    def copy(self):
        return copy.deepcopy(self)

    def expand(self):
        self.cases = []

        #   Expand structures for each direction and each alpha
        for structure in self.content["structures"]:
            structure = copy.deepcopy(structure)
            alphaA = np.round(np.arange(
                structure["alpha"][0], 
                structure["alpha"][1] + structure["alphaStep"], 
                structure["alphaStep"]
            ), 9)
            directionA = np.array(structure["directions"], dtype = float) 
            structure.pop("alpha")
            structure.pop("directions")

            for direction in directionA:
                for alpha in alphaA:
                    self.cases.append({
                        "alpha": alpha,
                        "direction": direction,
                        **structure
                    })

    def chooseParams(self, idn: int):
        if len(self.cases) > 0:
            self.params = self.cases[idn]

        else:
            raise IndexError("list index out of range in cause of zero length of 'cases'")


def default_config() -> Config:
    config = Config()

    config.options = {
        "nprocs": 1,
        "stage": "all",
        "overwrite": False,
        "database": "anisotropy.db",
        "build": "build",
        "logs": "logs",
        "shapefile": "shape.step",
        "meshfile": "mesh.mesh"
    }

    config.content = {
        "structures": []
    }

    labels = ["simple", "bodyCentered", "faceCentered"]
    alphas = [[0.01, 0.28], [0.01, 0.17], [0.01, 0.13]]

    for label, alpha in zip(labels, alphas):
        config.content["structures"].append({
            "label": label,
            "alpha": alpha,
            "alphaStep": 0.01,
            "directions": [[1., 0., 0.], [0., 0., 1.], [1., 1., 1.]],
            "r0": 1,
            "filletsEnabled": True,
            "pressureInlet": 1,
            "pressureOutlet": 0,
            "pressureInternal": 0,
            "velocityInlet": [0., 0., 0.],
            "velocityOutlet": None,
            "velocityInternal": [0., 0., 0.],
            "density": 1000,
            "viscosity": 1e-3
        })
    
    return config
