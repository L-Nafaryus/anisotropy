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

from anisotropy.database import database, tables as T

from anisotropy.shaping import Simple, BodyCentered, FaceCentered
from anisotropy.meshing import Mesh
from anisotropy.openfoam.presets import CreatePatchDict
from anisotropy.solving import OnePhaseFlow
from multiprocessing import current_process, parent_process

class UltimateRunner(object):
    def __init__(self, config = None, t_exec = None, t_shape = None):
        # Configuration file
        self.config = config or DefaultConfig()

        # Process recognition
        typo = True if not t_exec else False
        #if current_process().name == "MainProcess" and parent_process() == None:
        #    current_process().name = "master"
        
        # Database preparation
        if typo: #current_process().name == "master":
            self.prepareDatabase()

        if typo: #current_process().name == "master":
            with self.database:
                self.t_exec = T.Execution(date = datetime.now())
                self.t_exec.save()
                
            self.t_shape = None

        else:
            self.t_exec = t_exec
            self.t_shape = t_shape

        # Parameters
        self.shape = None
        self.mesh = None
        self.flow = None
        
        self.queue = []
        
    
    def prepareDatabase(self):
        # NOTE: separate function in cause of unpicklability of connections (use after process is started)
        self.database = database
        self.database.setup(self.config["database"])
        
    def createRow(self):
        # create a row in each table for the current case
        with self.database:
            
            self.t_mesh = T.Mesh(t_exec = self.t_exec, shape_id = self.t_shape)
            self.t_mesh.save()
            self.t_flow = T.FlowOnephase(t_exec = self.t_exec, mesh_id = self.t_mesh)
            self.t_flow.save()
            
    def fill(self):
        self.config.expand()
        logger.info(f"Preparing queue: { len(self.config.cases) }")
        
        for case in self.config.cases:
            with self.database:
                t_shape = T.Shape(
                    exec_id = self.t_exec,
                    **case
                )
                t_shape.save()
            
            self.queue.append(UltimateRunner(
                config = self.config,
                t_exec = self.t_exec,
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
                T.Shape.exec_id == self.t_exec, 
                T.Shape.shape_id == self.t_shape.shape_id
            )

        direction = "direction-[{},{},{}]".format(*[ str(d) for d in params.direction ])
        alpha = "alpha-{}".format(params.alpha)
        dirpath = path.join(self.config["build"], params.label, direction, alpha)
        
        return path.abspath(dirpath)

    def computeShape(self):
        #if current_process().name == "master":
        #    return
        
        with self.database:
            params = T.Shape.get(
                T.Shape.exec_id == self.t_exec, 
                T.Shape.shape_id == self.t_shape.shape_id
            )
            
        logger.info("Computing shape for {} with direction = {} and alpha = {}".format(
            params.label, params.direction, params.alpha
        ))
        filename = "shape.step"
        timer = Timer()
        
        shape = {
            "simple": Simple,
            "bodyCentered": BodyCentered,
            "faceCentered": FaceCentered
        }[params.label]
        
        self.shape = shape(
            direction = params.direction, 
            alpha = params.alpha, 
            r0 = params.r0, 
            filletsEnabled = params.filletsEnabled
        )
        #out, err, returncode = self.shape.build()
        self.shape.build()

        os.makedirs(self.casepath(), exist_ok = True)
        out, err, returncode = self.shape.export(path.join(self.casepath(), filename))
        
        if returncode == 0:
            params.shapeStatus = "done"

        else:
            logger.error(err)
            params.shapeStatus = "failed"

        with self.database:
            params.shapeExecutionTime = timer.elapsed()
            params.save()

    def computeMesh(self):
        #if not self.type == "worker":
        #    return
        
        with self.database:
            t_params = T.Shape.get(
                T.Shape.exec_id == self.t_exec, 
                T.Shape.shape_id == self.t_shape.shape_id
            )
            params = T.Mesh.get(
                T.Mesh.shape_id == self.t_shape.shape_id
            )
            
        logger.info("Computing mesh for {} with direction = {} and alpha = {}".format(
            t_params.label, t_params.direction, t_params.alpha
        ))
        filename = "mesh.mesh"
        timer = Timer()

        # TODO: load from object or file
        self.mesh = Mesh(self.shape.shape)
        #out, err, returncode = self.mesh.build()
        self.mesh.build()

        os.makedirs(self.casepath(), exist_ok = True)
        out, err, returncode = self.mesh.export(path.join(self.casepath(), filename))

        if returncode == 0:
            params.meshStatus = "done"

        else:
            logger.error(err)
            params.meshStatus = "failed"

        with self.database:
            params.meshExecutionTime = timer.elapsed()
            params.save()
        
    def computeFlow(self):
        # if not self.type == "worker":
        #    return

        with self.database:
            t_params = T.Shape.get(
                T.Shape.exec_id == self.t_exec,
                T.Shape.shape_id == self.t_shape.shape_id
            )
            m_params = T.Mesh.get(
                T.Mesh.shape_id == self.t_shape.shape_id
            )
            params = T.FlowOnephase.get(
                T.FlowOnephase.mesh_id == self.t_mesh.mesh_id
            )

        logger.info("Computing flow for {} with direction = {} and alpha = {}".format(
            t_params.label, t_params.direction, t_params.alpha
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
            params.flowStatus = "done"

        else:
            #logger.error(err)
            params.flowStatus = "failed"

        with self.database:
            params.flowExecutionTime = timer.elapsed()
            params.save()

    def pipeline(self, stage: str = None):
        self.prepareDatabase()
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



