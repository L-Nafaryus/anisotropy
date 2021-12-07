# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from datetime import datetime
from os import path

from anisotropy.core.config import DefaultConfig
from anisotropy.database import *
from anisotropy.shaping import Simple, BodyCentered, FaceCentered
from anisotropy.meshing import Mesh
from anisotropy.openfoam.presets import CreatePatchDict
from anisotropy.solving.onephase import OnePhaseFlow

class UltimateRunner(object):
    def __init__(self, config = None, exec_id = None):
        
        self.config = config or DefaultConfig()

        self.database = Database(self.config["database"])
        self.database.setup()

        if not exec_id:
            self.exec_id = Execution(date = datetime.now())
            self.exec_id.save()

        self.shape = None
        self.mesh = None
        self.flow = None

    def casepath(self):
        params = self.config.cases[0]

        return path.abspath(path.join(
            self.config["build"], 
            params["label"], 
            "direction-[{},{},{}]".format(*[ str(d) for d in params["direction"] ]), 
            "theta-{}".format(params["theta"])
        ))

    def computeShape(self):
        params = self.config.cases[0]
        filename = "shape.step"

        self.shape = {
            "simple": Simple,
            "bodyCentered": BodyCentered,
            "faceCentered": FaceCentered
        }[params["label"]](params["direction"])

        self.shape.build()

        os.makedirs(self.casepath(), exist_ok = True)
        self.shape.export(path.join(self.casepath(), filename))

    def computeMesh(self):
        params = self.config.cases[0]
        filename = "mesh.mesh"

        self.mesh = Mesh(self.shape.shape)
        self.mesh.build()

        os.makedirs(self.casepath(), exist_ok = True)
        self.mesh.export(path.join(self.casepath(), filename))
        
    def computeFlow(self):
        params = self.config.cases[0]
        flow = OnePhaseFlow(path = self.casepath())

        # initial 43 unnamed patches -> 
        # 6 named patches (inlet, outlet, wall, symetry0 - 3/5) ->
        # 4 inGroups (inlet, outlet, wall, symetry)
        createPatchDict = CreatePatchDict()
        createPatchDict["patches"] = []
        patches = {}

        for n, patch in enumerate(self.shape.shape.faces):
            #   shifted index 
            n += 1
            name = patch.name

            if patches.get(name):
                patches[name].append(f"patch{ n }")
            
            else:
                patches[name] = [ f"patch{ n }" ]

        for name in patches.keys():
            if name == "inlet":
                patchGroup = "inlet"
                patchType = "patch"

            elif name == "outlet":
                patchGroup = "outlet"
                patchType = "patch"

            elif name == "wall":
                patchGroup = "wall"
                patchType = "wall"

            else:
                patchGroup = "symetry"
                patchType = "symetryPlane"

            createPatchDict["patches"].append({
                "name": name,
                "patchInfo": {
                    "type": patchType,
                    "inGroups": [patchGroup]
                },
                "constructFrom": "patches",
                "patches": patches[name]
            })

        flow.append(createPatchDict)
        flow.write()
        #   Build a flow
        #flow.build()


    def pipeline(self, stage: str = None):
        stage = stage or self.config["stage"]

        if stage in ["shape", "all"]:
            with self.database.atomic():
                Shape.create(self._exec_id, **self.config.cases[0])

            self.computeShape()

        elif stage in ["mesh", "all"]:
            with self.database.atomic():
                Mesh.create(self._exec_id)

            self.computeMesh()

        elif stage in ["flow", "all"]:
            with self.database.atomic():
                Flow.create(self._exec_id)

            self.computeFlow()

        elif stage in ["postProcess", "all"]:
            self.postProcess()


    
    def parallel(queue: list, nprocs = None):
        nprocs = nprocs or self.config["nprocs"]

        parallel(nprocs, [()] * len(queue), [ runner.pipeline for runner in queue ])

