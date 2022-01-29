# -*- coding: utf-8 -*-

from datetime import datetime
import os
from os import PathLike
from pathlib import Path

from anisotropy.core.config import DefaultConfig

import logging

from anisotropy.core.postProcess import PostProcess
from anisotropy.core.utils import Timer, ErrorHandler
from anisotropy.core.parallel import ParallelRunner

logger = logging.getLogger(__name__)

from anisotropy.database import Database, tables as T

from anisotropy.shaping import Simple, BodyCentered, FaceCentered, Shape
from anisotropy.meshing import Mesh
from anisotropy.solving import OnePhaseFlow


class UltimateRunner(object):
    def __init__(self, config = None, exec_id: int = None, typo: str = "master"):
        # Configuration file
        self.config = config or DefaultConfig()

        # Process recognition
        self.typo = typo

        # Database preparation
        self.database = Database(path = self.config["database"])
        self.exec_id = None

        if exec_id:
            if self.database.getExecution(exec_id):
                self.exec_id = exec_id
            
            else:
                logger.warning(f"Execution id '{ exec_id }' not found. Creating new.")

        if not self.exec_id:
            with self.database:
                self.exec_id = T.Execution.create(date = datetime.now())

        # Parameters
        self.queue = []

    def createRow(self):
        # create a row in each table for the current case
        with self.database:
            shape = self.database.getShape(execution = self.exec_id, **self.config.params)

        if not shape:
            shape = T.Shape(exec_id = self.exec_id, **self.config.params)
            self.database.csave(shape)

        with self.database:
            mesh = self.database.getMesh(execution = self.exec_id, **self.config.params)

        if not mesh:
            mesh = T.Mesh(shape_id = shape.shape_id)
            self.database.csave(mesh)

        with self.database:
            flow = self.database.getFlowOnephase(execution = self.exec_id, **self.config.params)

        if not flow:
            flow = T.FlowOnephase(mesh_id = mesh.mesh_id, **self.config.params)
            self.database.csave(mesh)

    def fill(self):
        self.config.expand()
        logger.info(f"Preparing queue: { len(self.config.cases) }")
        
        for idn, case in enumerate(self.config.cases):
            config = self.config.copy()
            config.chooseParams(idn)
            config.minimize()

            kwargs = {
                "config": config,
                "exec_id": self.exec_id
            }
            self.queue.append(kwargs)
    
    def start(self, queue: list = None, nprocs: int = None):
        nprocs = nprocs or self.config["nprocs"]
        
        logger.info(f"Starting subprocesses: { nprocs }")
        parallel = ParallelRunner(nprocs = nprocs)
        parallel.start()
        
        for kwargs in self.queue:
            parallel.append(self.subrunner, kwargs = kwargs)

        parallel.wait()

    @property
    def casepath(self) -> PathLike:
        params = self.config.params
        path = Path(os.environ["ANISOTROPY_CWD"], os.environ["ANISOTROPY_BUILD_DIR"])
        path /= "execution-{}".format(self.exec_id)
        path /= "{}-[{},{},{}]-{}".format(
            params["label"], 
            *[ str(d) for d in params["direction"] ], 
            params["alpha"]
        )

        return path.resolve()

    def computeShape(self):
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
        shapeFile = self.casepath / "shape.step"
        timer = Timer()
        
        if shapeFile.exists() and shapeParams.shapeStatus == "done" and not self.config["overwrite"]:
            logger.info("Shape exists. Skipping ...")
            return
        
        shapeSelected = {
            "simple": Simple,
            "bodyCentered": BodyCentered,
            "faceCentered": FaceCentered
        }[shapeParams.label]
        
        shape = shapeSelected(
            direction = shapeParams.direction,
            alpha = shapeParams.alpha,
            r0 = shapeParams.r0,
            filletsEnabled = shapeParams.filletsEnabled
        )

        with ErrorHandler() as (eh, handle):
            handle(shape.build)()

        if not eh.returncode:
            self.casepath.mkdir(exist_ok = True)

            with ErrorHandler() as (eh, handle):
                handle(shape.write)(shapeFile)
        
        if not eh.returncode:
            shapeParams.shapeStatus = "done"
            shapeParams.volume = shape.shape.volume
            shapeParams.volumeCell = shape.cell.volume
            shapeParams.porosity = shapeParams.volume / shapeParams.volumeCell

        else:
            shapeParams.shapeStatus = "failed"
            logger.error(eh.error)

        shapeParams.shapeExecutionTime = timer.elapsed()
        self.database.csave(shapeParams)

    def computeMesh(self):
        err, returncode = "", 0
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
        meshFile = self.casepath / "mesh.mesh" 
        timer = Timer()

        if meshFile.exists() and meshParams.meshStatus == "done" and not self.config["overwrite"]:
            logger.info("Mesh exists. Skipping ...")
            return

        #   Shape
        shape = None
        shapeFile = self.casepath / "shape.step"

        if not shapeFile.exists() and not shapeFile.is_file():
            err = f"File not found: { shapeFile }"
            returncode = 2

        if not returncode:
            shape = Shape().read(shapeFile)

        #   Mesh
        if not returncode:
            mesh = Mesh(shape.shape)

            try:
                mesh.generate()

            except Exception as e:
                err = e
                returncode = 1

        if not returncode:
            self.casepath.mkdir(exist_ok = True)

            try:
                mesh.write(meshFile)
                mesh.write(self.casepath / "mesh.msh")
            
            except Exception as e:
                err = e
                returncode = 1

        if not returncode:
            meshParams.meshStatus = "done"
            meshParams.edges = len(self.mesh.edges)
            meshParams.faces = len(self.mesh.faces)
            meshParams.volumes = len(self.mesh.volumes)

        else:
            logger.error(err)
            meshParams.meshStatus = "failed"

        with self.database:
            meshParams.meshExecutionTime = timer.elapsed()
            meshParams.save()

    def computeFlow(self):
        params = self.config.params
        query = (
            params["label"],
            params["direction"],
            params["alpha"],
            self.exec_id
        )
        flowParams = self.database.getFlowOnephase(*query)

        logger.info("Computing flow for {} with direction = {} and alpha = {}".format(
            params["label"], params["direction"], params["alpha"]
        ))
        timer = Timer()

        flowParams.viscosityKinematic = flowParams.viscosity / flowParams.density

        with self.database:
            flowParams.save()            

        with self.database:
            flow = OnePhaseFlow(
                direction = params["direction"], 
                **self.database.getFlowOnephase(*query, to_dict = True),
                path = self.casepath
            )

        #   Shape
        shapeFile = self.casepath / "shape.step"

        if not shapeFile.exists() and not shapeFile.is_file():
            err = f"File not found: { shapeFile }"
            returncode = 2

        if not returncode:
            shape = Shape().read(shapeFile)

        #   Patches from occ to openfoam
        patches = shape.patches(group = True, shiftIndex = True, prefix = "patch")
        flow.createPatches(patches)
        flow.write()

        #   Build a flow
        try:
            out, err, returncode = flow.build()

        except Exception as e:
            # out, err, returncode = "", e, 1
            logger.error(e, exc_info = True)

        if returncode == 0:
            flowParams.flowStatus = "done"

        else:
            # logger.error(err)
            flowParams.flowStatus = "failed"

        with self.database:
            flowParams.flowExecutionTime = timer.elapsed()
            flowParams.save()

    def computePostProcess(self):
        params = self.config.params
        flowParams = self.database.getFlowOnephase(
            params["label"],
            params["direction"],
            params["alpha"],
            self.exec_id
        )

        logger.info("Computing post process for {} with direction = {} and alpha = {}".format(
            params["label"], params["direction"], params["alpha"]
        ))

        postProcess = PostProcess(self.casepath)

        if flowParams.flowStatus == "done":
            flowParams.flowRate = postProcess.flowRate("outlet")

        with self.database:
            flowParams.save()
        
        self.dispose()

    def pipeline(self, stage: str = None):
        stage = stage or self.config["stage"]

        if stage in ["shape", "all"]:
            self.computeShape()

        if stage in ["mesh", "all"]:
            self.computeMesh()

        if stage in ["flow", "all"]:
            self.computeFlow()

        if stage in ["postProcess", "all"]:
            self.computePostProcess()

    @staticmethod
    def subrunner(*args, **kwargs):
        runner = UltimateRunner(config = kwargs["config"], exec_id = kwargs["exec_id"], typo = "worker")
        runner.createRow()
        runner.pipeline()
