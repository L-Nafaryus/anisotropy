# -*- coding: utf-8 -*-

from os import PathLike

from os import environ
from datetime import datetime
import pathlib
import logging

from anisotropy.database import Database, tables
from anisotropy import shaping
from anisotropy import meshing
from anisotropy import solving

from . import config
from . import postprocess
from . import utils
from . import ParallelRunner


logger = logging.getLogger(__name__)


class UltimateRunner(object):
    def __init__(self, conf = None, exec_id: int = None, typo: str = "master"):

        # Configuration file
        self.config = conf or config.DefaultConfig()

        # Database preparation
        self.database = Database(self.config["database"])
        self.exec_id = None

        if exec_id:
            if self.database.getExecution(exec_id):
                self.exec_id = exec_id
            
            else:
                logger.warning(f"Execution id '{ exec_id }' not found. Creating new.")

        if not self.exec_id:
            with self.database:
                self.exec_id = tables.Execution.create(date = datetime.now())

        # Parameters
        self.queue = []

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
            self.database.csave(mesh)

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

    def compute_shape(self):
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
        shapefile = self.casepath / "shape.step"
        timer = utils.Timer()
        
        if (
            shapefile.exists() and 
            shapeParams.shapeStatus == "done" and 
            not self.config["overwrite"]
        ):
            logger.info("Shape exists. Skipping ...")
            return
        
        generate_shape = {
            "simple": shaping.primitives.simple,
            "bodyCentered": shaping.primitives.bodyCentered,
            "faceCentered": shaping.primitives.faceCentered
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
            self.casepath.mkdir(exist_ok = True)

            shape.write(shapefile)
        
        except Exception as e:
            logger.error(e)

            shapeParams.shapeStatus = "failed"

        else:
            shapeParams.shapeStatus = "done"
            shapeParams.volume = shape.shape.volume
            shapeParams.volumeCell = shape.cell.volume
            shapeParams.porosity = shapeParams.volume / shapeParams.volumeCell

        #   commit parameters
        shapeParams.shapeExecutionTime = timer.elapsed()
        self.database.csave(shapeParams)

    def compute_mesh(self):
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
        meshfile = self.casepath / "mesh.mesh" 
        timer = utils.Timer()

        if (
            meshfile.exists() and 
            meshParams.meshStatus == "done" and 
            not self.config["overwrite"]
        ):
            logger.info("Mesh exists. Skipping ...")
            return

        #   Shape
        shape = None

        try:
            #   load shape
            shapefile = self.casepath / "shape.step"
            shape = shaping.Shape().read(shapefile)

            #   generate mesh
            parameters = meshing.MeshingParameters()
            mesh = meshing.Mesh(shape)
            mesh.generate(parameters)

            #   export
            self.casepath.mkdir(exist_ok = True)

            mesh.write(meshfile)
            mesh.write(self.casepath / "mesh.msh")

        except Exception as e:
            logger.error(e)

            meshParams.meshStatus = "failed"

        else:
            meshParams.meshStatus = "done"
            meshParams.edges = len(self.mesh.edges)
            meshParams.faces = len(self.mesh.faces)
            meshParams.volumes = len(self.mesh.volumes)

        #   commit parameters
        meshParams.meshExecutionTime = timer.elapsed()
        self.database.csave(meshParams)

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
        timer = utils.Timer()

        #   precalculate some parameters
        flowParams.viscosityKinematic = flowParams.viscosity / flowParams.density
        self.database.csave(flowParams)            

        #
        flowParamsDict = self.database.getFlowOnephase(*query, to_dict = True)

        flow = solving.FlowOnephase(
            direction = params["direction"], 
            **flowParamsDict,
            path = self.casepath
        )

        try:
            #   load shape
            shapefile = self.casepath / "shape.step"
            shape = shaping.Shape().read(shapefile)

            patches = shape.patches(group = True, shiftIndex = True, prefix = "patch")

            #   generate solution
            flow.createPatches(patches)
            flow.build()

        except Exception as e:
            logger.error(e)

            flowParams.flowStatus = "failed"

        else:
            flowParams.flowStatus = "done"

        #   commit parameters
        flowParams.flowExecutionTime = timer.elapsed()
        self.database.csave(flowParams)

    def compute_postprocess(self):
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

        postProcess = postprocess.PostProcess(self.casepath)

        if flowParams.flowStatus == "done":
            flowParams.flowRate = postProcess.flowRate("outlet")

        self.database.csave(flowParams)
        
    def pipeline(self, stage: str = None):
        stage = stage or self.config["stage"]

        if stage in ["shape", "all"]:
            self.compute_shape()

        if stage in ["mesh", "all"]:
            self.compute_mesh()

        if stage in ["flow", "all"]:
            self.compute_flow()

        if stage in ["postProcess", "all"]:
            self.compute_postprocess()

    @staticmethod
    def subrunner(*args, **kwargs):
        runner = UltimateRunner(config = kwargs["config"], exec_id = kwargs["exec_id"])
        runner.prepare_database()
        runner.pipeline()
