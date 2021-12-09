# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from datetime import datetime
import os
from os import path

from anisotropy.core.config import DefaultConfig

import logging
from anisotropy.core.utils import parallel, ParallelRunner, setupLogger

logger = logging.getLogger(__name__)

from anisotropy.database import database, tables

T = tables

from anisotropy.shaping import Simple, BodyCentered, FaceCentered
from anisotropy.meshing import Mesh
from anisotropy.openfoam.presets import CreatePatchDict
from anisotropy.solving.onephase import OnePhaseFlow


class UltimateRunner(object):
    def __init__(self, config = None, exec_id = None, t_shape = None):
        
        self.config = config or DefaultConfig()

        self.type = "master" if not exec_id else "worker"
        
        if self.type == "master":
            self.prepareDatabase()

        if self.type == "master":
            with self.database:
                self.exec_id = T.Execution(date = datetime.now())
                self.exec_id.save()
                
            self.t_shape = None

        else:
            self.exec_id = exec_id
            self.t_shape = t_shape

        self.shape = None
        self.mesh = None
        self.flow = None
        
        self.queue = []
        
    
    def prepareDatabase(self):
        # NOTE: separate function in cause of unpicklability of connections
        self.database = database
        self.database.setup(self.config["database"])
        
    def fill(self):
        self.config.expand()
        logger.info(f"Preparing queue: { len(self.config.cases) }")
        
        for case in self.config.cases:
            with self.database:
                t_shape = T.Shape(
                    exec_id = self.exec_id,
                    **case
                )
                t_shape.save()
            
            self.queue.append(UltimateRunner(
                config = self.config,
                exec_id = self.exec_id,
                t_shape = t_shape
            ))
        
    def start(self, queue: list = None, nprocs: int = None):
        nprocs = nprocs or self.config["nprocs"]
        
        logger.info(f"Starting subprocesses: { nprocs }")
        parallel = ParallelRunner(nprocs = nprocs)
        parallel.start()
        
        for runner in self.queue:
            parallel.append(runner.pipeline, args = [self.config["stage"]])
        
        parallel.wait()
        # TODO: if runner done - remove from queue; results from parallel function
        
    def casepath(self):
        with self.database:
            params = T.Shape.get(
                T.Shape.exec_id == self.exec_id, 
                T.Shape.shape_id == self.t_shape.shape_id
            )

        direction = "direction-[{},{},{}]".format(*[ str(d) for d in params.direction ])
        theta = "theta-{}".format(params.theta)
        dirpath = path.join(self.config["build"], params.label, direction, theta)
        
        return path.abspath(dirpath)

    def computeShape(self):
        if not self.type == "worker":
            return
        
        with self.database:
            params = T.Shape.get(
                T.Shape.exec_id == self.exec_id, 
                T.Shape.shape_id == self.t_shape.shape_id
            )
            
        logger.info("Computing shape for {} with direction = {} and theta = {}".format(params.label, params.direction, params.theta))
        filename = "shape.step"

        self.shape = {
            "simple": Simple,
            "bodyCentered": BodyCentered,
            "faceCentered": FaceCentered
        }[params.label]

        self.shape(params.direction)
        self.shape.build()

        os.makedirs(self.casepath(), exist_ok = True)
        self.shape.export(path.join(self.casepath(), filename))
        
        with self.database:
            params.shapeStatus = "Done"
            params.save()

    def computeMesh(self):
        if not self.type == "worker":
            return
        
        with self.database:
            params = (T.Mesh.select(T.Shape, T.Mesh)
            .join(
                T.Mesh, 
                JOIN.INNER, 
                on = (T.Mesh.shape_id == T.Shape.shape_id)
            ).where(
                T.Shape.exec_id == self.exec_id, 
                T.Shape.shape_id == self.t_shape.shape_id
            ))
            
        logger.info("Computing mesh for {} with direction = {} and theta = {}".format(params.label, params.direction, params.theta))
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
        self.prepareDatabase()
        
        stage = stage or self.config["stage"]

        if stage in ["shape", "all"]:
            self.computeShape()

        elif stage in ["mesh", "all"]:
            self.computeMesh()

        elif stage in ["flow", "all"]:
            self.computeFlow()

        elif stage in ["postProcess", "all"]:
            self.postProcess()




