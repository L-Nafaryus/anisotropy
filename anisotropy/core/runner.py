# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from datetime import datetime
import os
from os import path

from anisotropy.core.config import DefaultConfig

import logging
from anisotropy.core.utils import ParallelRunner, Timer

logger = logging.getLogger(__name__)

from anisotropy.database import Database, tables as T

from anisotropy.shaping import Simple, BodyCentered, FaceCentered
from anisotropy.meshing import Mesh
from anisotropy.openfoam.presets import CreatePatchDict
from anisotropy.solving import OnePhaseFlow
from multiprocessing import current_process, parent_process

class UltimateRunner(object):
    def __init__(self, config = None, exec_id: int = None): #t_exec = None, t_shape = None):
        # Configuration file
        self.config = config or DefaultConfig()

        # Process recognition
        typo = True if not exec_id else False
        #if current_process().name == "MainProcess" and parent_process() == None:
        #    current_process().name = "master"

        # Database preparation
        if typo: #current_process().name == "master":
            self.database = Database(path = self.config["database"])

        if typo: #current_process().name == "master":
            with self.database:
                self.t_exec = T.Execution(date = datetime.now())
                self.t_exec.save()
                
            #self.t_shape = None

        else:
            #self.t_exec = self.database.getExecution(exec_id)
            self.exec_id = exec_id
            #self.t_exec = t_exec
            #self.t_shape = t_shape

        # Parameters
        self.shape = None
        self.mesh = None
        self.flow = None
        
        self.queue = []
        

    def createRow(self):
        # create a row in each table for the current case
        with self.database:
            t_shape = T.Shape(exec_id = self.exec_id, **self.config.params)
            t_shape.save()
            t_mesh = T.Mesh(shape_id = t_shape.shape_id)
            t_mesh.save()
            t_flow = T.FlowOnephase(mesh_id = t_mesh.mesh_id)
            t_flow.save()
            
    def fill(self):
        self.config.expand()
        logger.info(f"Preparing queue: { len(self.config.cases) }")
        
        for idn, case in enumerate(self.config.cases):
            config = self.config.copy()
            config.chooseParams(idn)
            config.minimize()

            #with self.database:
            #    t_shape = T.Shape(
            #        exec_id = self.t_exec,
            #        **case
            #    )
            #    t_shape.save()
            
            self.queue.append(UltimateRunner(
                config = config,
                exec_id = self.t_exec.exec_id
                #t_exec = self.t_exec,
                #t_shape = t_shape
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
        #with self.database:
        #    params = T.Shape.get(
        #        T.Shape.exec_id == self.t_exec,
        #        T.Shape.shape_id == self.t_shape.shape_id
        #    )
        params = self.config.params
        shapeParams = self.database.getShape(
            params["label"],
            params["direction"],
            params["alpha"],
            self.exec_id
        )

        execution = "execution-{}".format(self.exec_id)
        case = "{}-[{},{},{}]-{}".format(params["label"], *[ str(d) for d in params["direction"] ], params["alpha"])
        #alpha = "alpha-{}".format(shapeParams.alpha)
        #dirpath = path.join(self.config["build"], shapeParams.label, direction, alpha)
        dirpath = path.join(self.config["build"], execution, case)

        return path.abspath(dirpath)

    def computeShape(self):
        #if current_process().name == "master":
        #    return
        
        #with self.database:
        #    params = T.Shape.get(
        #        T.Shape.exec_id == self.t_exec,
        #        T.Shape.shape_id == self.t_shape.shape_id
        #    )

        params = self.config.params
        shapeParams = self.database.getShape(
            params["label"],
            params["direction"],
            params["alpha"],
            self.exec_id
        )

        logger.info("Computing shape for {} with direction = {} and alpha = {}".format(
            params["label"], params["direction"], params["alpha"]
        ))
        filename = "shape.step"
        timer = Timer()
        
        shape = {
            "simple": Simple,
            "bodyCentered": BodyCentered,
            "faceCentered": FaceCentered
        }[shapeParams.label]
        
        self.shape = shape(
            direction = shapeParams.direction,
            alpha = shapeParams.alpha,
            r0 = shapeParams.r0,
            filletsEnabled = shapeParams.filletsEnabled
        )
        #out, err, returncode = self.shape.build()
        # TODO: wrap build function for exceptions
        self.shape.build()

        os.makedirs(self.casepath(), exist_ok = True)
        out, err, returncode = self.shape.export(path.join(self.casepath(), filename))
        
        if returncode == 0:
            shapeParams.shapeStatus = "done"

        else:
            logger.error(err)
            shapeParams.shapeStatus = "failed"

        with self.database:
            shapeParams.shapeExecutionTime = timer.elapsed()
            shapeParams.save()

    def computeMesh(self):
        #if not self.type == "worker":
        #    return
        
        #with self.database:
        #    t_params = T.Shape.get(
        #        T.Shape.exec_id == self.t_exec,
        #        T.Shape.shape_id == self.t_shape.shape_id
        #    )
        #    params = T.Mesh.get(
        #        T.Mesh.shape_id == self.t_shape.shape_id
        #    )

        params = self.config.params
        meshParams = self.database.getMesh(
            params["label"],
            params["direction"],
            params["alpha"],
            self.exec_id
        )

        logger.info("Computing mesh for {} with direction = {} and alpha = {}".format(
            params["label"], params["direction"], params["alpha"]
        ))
        filename = "mesh.mesh"
        timer = Timer()

        # TODO: load from object or file
        self.mesh = Mesh(self.shape.shape)
        #out, err, returncode = self.mesh.build()
        # TODO: wrap build function for exceptions
        self.mesh.build()

        os.makedirs(self.casepath(), exist_ok = True)
        out, err, returncode = self.mesh.export(path.join(self.casepath(), filename))

        if returncode == 0:
            meshParams.meshStatus = "done"

        else:
            logger.error(err)
            meshParams.meshStatus = "failed"

        with self.database:
            meshParams.meshExecutionTime = timer.elapsed()
            meshParams.save()
        
    def computeFlow(self):
        # if not self.type == "worker":
        #    return

        #with self.database:
        #    t_params = T.Shape.get(
        #        T.Shape.exec_id == self.t_exec,
        #        T.Shape.shape_id == self.t_shape.shape_id
        #    )
        #    m_params = T.Mesh.get(
        #        T.Mesh.shape_id == self.t_shape.shape_id
        #    )
        #    params = T.FlowOnephase.get(
        #        T.FlowOnephase.mesh_id == self.t_mesh.mesh_id
        #    )

        params = self.config.params
        flowParams = self.database.getFlowOnephase(
            params["label"],
            params["direction"],
            params["alpha"],
            self.exec_id
        )

        logger.info("Computing flow for {} with direction = {} and alpha = {}".format(
            params["label"], params["direction"], params["alpha"]
        ))
        timer = Timer()

        self.flow = OnePhaseFlow(path = self.casepath())

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

        self.flow.append(createPatchDict)
        self.flow.write()
        #   Build a flow
        try:
            out, err, returncode = self.flow.build()

        except Exception as e:
            out, err, returncode = "", e, 1
            logger.error(e, exc_info = True)

        if returncode == 0:
            flowParams.flowStatus = "done"

        else:
            #logger.error(err)
            flowParams.flowStatus = "failed"

        with self.database:
            flowParams.flowExecutionTime = timer.elapsed()
            flowParams.save()

    def pipeline(self, stage: str = None):
        self.database = Database(path = self.config["database"])
        self.createRow()
        
        stage = stage or self.config["stage"]

        # TODO: fix flow
        # TODO: change case path to execDATE/label-direction-theta/*
        # TODO: fix nprocs
        #try:
        if stage in ["shape", "all"]:
            self.computeShape()

        if stage in ["mesh", "all"]:
            self.computeMesh()

        if stage in ["flow", "all"]:
            self.computeFlow()

            #elif stage in ["postProcess", "all"]:
            #    self.postProcess()
        #except Exception as e:
        #    logger.error(e)



