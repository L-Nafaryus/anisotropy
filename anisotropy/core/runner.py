# -*- coding: utf-8 -*-

from os import PathLike

from os import environ
from datetime import datetime
import pathlib
import logging
import numpy as np

from anisotropy.database import Database, tables
from anisotropy import shaping
from anisotropy import meshing
from anisotropy import solving
from anisotropy import openfoam

from . import config as core_config
from . import postprocess
from . import utils
from . import ParallelRunner


logger = logging.getLogger(__name__)


class UltimateRunner(object):
    def __init__(self, config = None, exec_id: int = None, _type: str = "master"):

        self.type = _type

        # Configuration file
        self.config = config or core_config.default_config()
        
        # Database preparation
        self.database = Database(self.config["database"])
        self.exec_id = None

        if exec_id is not None:
            if self.database.getExecution(int(exec_id)):
                self.exec_id = int(exec_id)
            
            else:
                logger.warning(f"Execution id '{ exec_id }' not found. Creating new.")

        if self.exec_id is None:
            with self.database:
                self.exec_id = tables.Execution.create(date = datetime.now()).exec_id

        if self.type == "master":
            logger.info(f"Current execution id: { self.exec_id }")

        # Parameters
        self.queue = []

    def _query_database(self, tableName: str, to_dict: bool = False):
        tableName = tableName.lower()
        get_row = {
            "shape": self.database.getShape,
            "mesh": self.database.getMesh,
            "flowonephase": self.database.getFlowOnephase
        }[tableName]
        #   query
        args = (
            self.config.params["label"],
            self.config.params["direction"],
            self.config.params["alpha"],
            self.exec_id,
            to_dict
        )

        return get_row(*args)

    def prepare_database(self):
        # create a row in each table for the current case
        #   shape
        with self.database:
            shape = self.database.getShape(execution = self.exec_id, **self.config.params)

        if not shape:
            shape = tables.Shape(exec_id = self.exec_id, **self.config.params)
            self.database.csave(shape)

        #   mesh
        with self.database:
            mesh = self.database.getMesh(execution = self.exec_id, **self.config.params)

        if not mesh:
            mesh = tables.Mesh(shape_id = shape.shape_id)
            self.database.csave(mesh)

        # onephase flow
        with self.database:
            flow = self.database.getFlowOnephase(execution = self.exec_id, **self.config.params)

        if not flow:
            flow = tables.FlowOnephase(mesh_id = mesh.mesh_id, **self.config.params)
            self.database.csave(flow)

    def prepare_queue(self):
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

        path = pathlib.Path(environ["AP_CWD"], environ["AP_BUILD_DIR"])
        path /= "execution-{}".format(self.exec_id)
        path /= "{}-[{},{},{}]-{}".format(
            params["label"], 
            *[ str(d) for d in params["direction"] ], 
            params["alpha"]
        )

        return path.resolve()

    @property
    def shapefile(self) -> PathLike:
        return self.casepath / self.config["shapefile"]
    
    @property
    def meshfile(self) -> PathLike:
        return self.casepath / self.config["meshfile"]

    def compute_shape(self):
        params = self.config.params
        shapeParams = self._query_database("shape")

        logger.info("Computing shape for {} with direction = {} and alpha = {}".format(
            params["label"], params["direction"], params["alpha"]
        ))
        timer = utils.Timer()
        
        #   check physical existence
        if self.shapefile.exists() and self.config["overwrite"] is not True:
            logger.info("Shape exists, skipping ...")
            return
        
        #
        generate_shape = {
            "simple": shaping.primitives.simple,
            "bodyCentered": shaping.primitives.body_centered,
            "faceCentered": shaping.primitives.face_centered
        }[shapeParams.label]

        try:
            #   generate shape
            shape = generate_shape(
                shapeParams.alpha,
                shapeParams.direction,
                r0 = shapeParams.r0,
                filletsEnabled = shapeParams.filletsEnabled
            )

            #   export
            self.casepath.mkdir(parents = True, exist_ok = True)

            shape.write(self.shapefile)
        
        except Exception as e:
            logger.error(e, exc_info = True)

            shapeParams.shapeStatus = "failed"

        else:
            shapeParams.shapeStatus = "done"
            shapeParams.volume = shape.shape.volume * np.prod(params["scale"])
            shapeParams.volumeCell = shape.cell.volume * np.prod(params["scale"])
            shapeParams.porosity = shapeParams.volume / shapeParams.volumeCell

        #   commit parameters
        shapeParams.shapeExecutionTime = timer.elapsed()
        self.database.csave(shapeParams)

    def compute_mesh(self):
        params = self.config.params
        meshParams = self._query_database("mesh")

        logger.info("Computing mesh for {} with direction = {} and alpha = {}".format(
            params["label"], params["direction"], params["alpha"]
        ))
        timer = utils.Timer()

        #   check physical existence
        if self.meshfile.exists() and self.config["overwrite"] is not True:
            logger.info("Mesh exists, skipping ...")
            return
        
        elif not self.shapefile.exists():
            logger.error("Cannot find shape file to build a mesh.")
            return

        #   Shape
        shape = None

        try:
            #   load shape
            shape = shaping.Shape().read(self.shapefile)

            #   generate mesh
            parameters = meshing.MeshingParameters()
            mesh = meshing.Mesh(shape)
            mesh.generate(parameters)

            #   export
            self.casepath.mkdir(parents = True, exist_ok = True)

            mesh.write(self.meshfile)
            mesh.write(self.casepath / "mesh.msh")

        except Exception as e:
            logger.error(e, exc_info = True)

            meshParams.meshStatus = "failed"

        else:
            meshParams.meshStatus = "done"
            meshParams.faces = len(mesh.faces)
            meshParams.volumes = len(mesh.volumes)

        #   commit parameters
        meshParams.meshExecutionTime = timer.elapsed()
        self.database.csave(meshParams)

    def compute_flow(self):
        params = self.config.params
        flowParams = self._query_database("flowonephase")

        logger.info("Computing flow for {} with direction = {} and alpha = {}".format(
            params["label"], params["direction"], params["alpha"]
        ))
        timer = utils.Timer()
        
        #   check physical existence
        if openfoam.FoamCase(path = self.casepath).is_converged() and not self.config["overwrite"]:
            logger.info("Solution exists. Skipping ...")
            return
        
        elif not self.shapefile.exists():
            logger.error("Cannot find shape file to compute a solution.")
            return
        
        elif not self.meshfile.exists():
            logger.error("Cannot find mesh file to compute a solution.")
            return       

        #   precalculate some parameters
        flowParams.viscosityKinematic = flowParams.viscosity / flowParams.density
        self.database.csave(flowParams)            

        #
        flowParamsDict = self._query_database("flowonephase", to_dict = True)

        try:
            #   load shape
            shape = shaping.Shape().read(self.shapefile)

            #
            flow = solving.FlowOnePhase(
                path = self.casepath,
                direction = params["direction"], 
                patches = shape.patches(group = True, shiftIndex = True, prefix = "patch"),
                scale = params["scale"],
                **flowParamsDict
            )

            #   generate solution
            flow.generate()

        except Exception as e:
            logger.error(e, exc_info = True)

            flowParams.flowStatus = "failed"

        else:
            flowParams.flowStatus = "done"

        #   commit parameters
        flowParams.flowExecutionTime = timer.elapsed()
        self.database.csave(flowParams)

    def compute_postprocess(self):
        params = self.config.params
        flowParams = self._query_database("flowonephase")

        logger.info("Computing post process for {} with direction = {} and alpha = {}".format(
            params["label"], params["direction"], params["alpha"]
        ))

        if flowParams.flowStatus == "done":
            if flowParams.flowRate is None and self.config["overwrite"] is not True:
                flowParams.flowRate = postprocess.flowRate("outlet", self.casepath)

        self.database.csave(flowParams)
        
    def pipeline(self, stage: str = None):
        stage = stage or self.config["stage"]
        stages = ["shape", "mesh", "flow", "postProcess", "all"]

        if stage not in stages:
            logger.error(f"Unknown stage '{ stage }'.")
            return
        
        for current in stages:
            if current == "shape":
                params = self._query_database("shape")

                #   check database entry
                if params.shapeStatus == "done" and self.config["overwrite"] is not True:
                    logger.info("Successful shape entry exists, skipping ...")
                    continue

                self.compute_shape()

            if current == "mesh":
                params = self._query_database("mesh")

                #   check database entry
                if params.meshStatus == "done" and self.config["overwrite"] is not True:
                    logger.info("Successful mesh entry exists, skipping ...")
                    continue

                self.compute_mesh()

            if current == "flow":
                params = self._query_database("flowonephase")

                #   check database entry
                if params.flowStatus == "done" and self.config["overwrite"] is not True:
                    logger.info("Successful flow entry exists, skipping ...")
                    continue

                self.compute_flow()

            if current == "postProcess":
                params = self._query_database("flowonephase")

                #   check database entry
                # if params.flowStatus == "done" and self.config["overwrite"] is not True:
                #    logger.info("Successful flow entry exists, skipping ...")
                #    continue

                self.compute_postprocess()
            
            if current == stage or current == "all":
                break

    @staticmethod
    def subrunner(*args, **kwargs):
        runner = UltimateRunner(
            config = kwargs["config"], 
            exec_id = kwargs["exec_id"],
            _type = "worker"
        )
        runner.prepare_database()
        runner.pipeline()
