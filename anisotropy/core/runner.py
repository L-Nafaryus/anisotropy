# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from datetime import datetime
from os import path
import logging

from anisotropy.core.config import DefaultConfig
from anisotropy.core.utils import parallel, ParallelRunner, setupLogger
from anisotropy.database import *
from anisotropy.shaping import Simple, BodyCentered, FaceCentered
from anisotropy.meshing import Mesh
from anisotropy.openfoam.presets import CreatePatchDict
from anisotropy.solving.onephase import OnePhaseFlow

logger = logging.getLogger("anisotropy")
setupLogger(logger, logging.INFO)

class UltimateRunner(object):
    def __init__(self, config = None, exec_id = None, m_shape = None):
        
        self.config = config or DefaultConfig()

        if not m_shape:
            self.database = Database(self.config["database"])
            self.database.setup()

        if not exec_id:
            with self.database.database:
                self.exec_id = Execution(date = datetime.now())
                self.exec_id.save()
            self.type = "master"
            self.m_shape = None

        else:
            self.exec_id = exec_id
            self.type = "worker"
            self.m_shape = m_shape

        self.shape = None
        self.mesh = None
        self.flow = None
        
        self.queue = []
        
    def fill(self):
        self.config.expand()
        
        for case in self.config.cases:
            with self.database.database:
                m_shape = Shape(
                    exec_id = self.exec_id,
                    **case
                )
                m_shape.save()
            
            self.queue.append(UltimateRunner(
                config = self.config,
                exec_id = self.exec_id,
                m_shape = m_shape
            ))
        
                
        
    def start(self, queue: list = None, nprocs: int = None):
        nprocs = nprocs or self.config["nprocs"]
        runners = [ runner.pipeline for runner in self.queue ]
        args = [[self.config["stage"]]] * len(self.queue)
        
        parallel = ParallelRunner(nprocs = nprocs)
        parallel.start()
        
        for runner in self.queue:
            parallel.append(runner.pipeline, args = [self.config["stage"]])
        
        parallel.wait()
        #parallel(nprocs, args, runners)
        # TODO: if runner done - remove from queue; results from parallel function
        
    def casepath(self):
        
        with self.database.database:
            params = Shape.get(
                Shape.exec_id == self.exec_id, 
                Shape.shape_id == self.m_shape.shape_id
            )

        return path.abspath(path.join(
            self.config["build"], 
            params.label, 
            "direction-[{},{},{}]".format(*[ str(d) for d in params.direction ]), 
            "theta-{}".format(params.theta)
        ))

    def computeShape(self):
        if not self.type == "worker":
            return
        self.database = Database(self.config["database"])
        self.database.setup()
        with self.database.database:
            params = Shape.get(
                Shape.exec_id == self.exec_id, 
                Shape.shape_id == self.m_shape.shape_id
            )
        filename = "shape.step"

        logger.info([params.label, params.direction, params.theta])
        self.shape = {
            "simple": Simple,
            "bodyCentered": BodyCentered,
            "faceCentered": FaceCentered
        }[params.label](params.direction)

        self.shape.build()

        os.makedirs(self.casepath(), exist_ok = True)
        self.shape.export(path.join(self.casepath(), filename))
        
        with self.database.database:
            params.shapeStatus = "Done"
            params.save()

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
            self.computeShape()

        elif stage in ["mesh", "all"]:
            self.computeMesh()

        elif stage in ["flow", "all"]:
            self.computeFlow()

        elif stage in ["postProcess", "all"]:
            self.postProcess()




