# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from datetime import datetime

from anisotropy.core.config import DefaultConfig
from anisotropy.database import *
from anisotropy.salomepl.runner import SalomeRunner
import anisotropy.samples as samples

class UltimateRunner(object):
    def __init__(self, config = None, exec_id = False):
        
        self.config = config or DefaultConfig()

        self.database = Database(self.config["database"])
        self.datebase.setup()

        if exec_id:
            self._exec_id = Execution(date = datetime.now())
            self._exec_id.save()

    def casePath(self):
        case = self.config.cases[0]

        return os.path.join(
            self.config["build"], 
            case["label"], 
            "direction-{}".format(str(case["direction"]).replace(" ", "")), 
            "theta-{}".format(case["theta"])
        )

    def computeMesh(self):

        case = self.config.cases[0]
        runner = SalomeRunner()
        cliArgs = [
            "computemesh",
            case["label"],
            case["direction"],
            case["theta"],
            path
        ]

        out, err, returncode = runner.execute(
            env["CLI"],
            *cliArgs,
            timeout = self.config["salome_timeout"],
            root = env["ROOT"],
            logpath = self.casePath()
        )

        return out, err, returncode


    def _computeMesh(self):
        """Function for Salome

        Resolution pipeline:
        cli(UR -> computeMesh) -> salomeRunner(salome -> cli) -> computemesh(UR -> _computeMesh)
        """
        
        # TODO: add logger configuration here 
        sample = samples.__dict__[..]

        #   Build a shape
        shape = sample.geometry(..)
        shape.build()
        shape.export(..)

        #   Build a mesh
        mesh = sample.mesh(shape)
        mesh.build()
        mesh.export(..)

        #   Fill database

        
    def computeFlow(self):

        sample = samples.__dict__[..]

        #   Build a flow
        flow = sample.onephaseflow(..)
        flow.build()


    def pipeline(self, stage: str = None):
        stage = stage or config["stage"]

        match stage:
            case "mesh" | "all":
                with self.database.atomic():
                    Shape.create(self._exec_id, **self.config.cases[0])
                    Mesh.create(self._exec_id)

                self.computeMesh(..)

            case "flow" | "all":
                with self.database.atomic():
                    Flow.create(self._exec_id)

                self.computeFlow(..)

            case "postProcess" | "all":
                self.postProcess(..)


    
    def parallel(queue: list, nprocs = None):
        nprocs = nprocs or config["nprocs"]

        parallel(nprocs, [()] * len(queue), [ runner.pipeline for runner in queue ])

