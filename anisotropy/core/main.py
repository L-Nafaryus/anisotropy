# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import os, sys
import time
from datetime import timedelta, datetime
import shutil
import logging
from copy import deepcopy
from math import sqrt

import toml

from anisotropy import (
    __version__, env,
    openfoam
)
from anisotropy.core.utils import setupLogger, Timer
from anisotropy.core.database import Database
from anisotropy import salomepl
import anisotropy.salomepl.utils
import anisotropy.salomepl.geometry
import anisotropy.salomepl.mesh
from anisotropy.samples import Simple, FaceCentered, BodyCentered

logger = logging.getLogger(env["logger_name"])
#setupLogger(logger, logging.INFO, env["LOG"])

#peeweeLogger = logging.getLogger("peewee")
#peeweeLogger.setLevel(logging.INFO)


class Anisotropy(object):
    """Ultimate class that organizes whole working process"""

    def __init__(self):
        """Constructor method"""

        self.env = env
        self.db = None #Database(self.env["db_name"], self.env["db_path"])
        self.params = []


    def load(self, structure_type: str, structure_direction: list, structure_theta: float):
        """Shortcut for `Database.setup` and `Database.load`. 

        See :class:`anisotropy.core.database.Database` for more details.
        """
        self.db.setup()
        self.params = self.db.load(structure_type, structure_direction, structure_theta)

    def update(self, params: dict = None):
        """Shortcut for `Database.setup` and `Database.update`. 

        See :class:`anisotropy.core.database.Database` for more details.
        """
        self.db.setup()
        self.db.update(self.params if not params else params)


    @staticmethod
    def version():
        """Returns versions of all used main programs

        :return: 
            Versions joined by next line symbol
        """
        versions = {
            "anisotropy": __version__,
            "Python": sys.version.split(" ")[0],
            "Salome": "[missed]",
            "OpenFOAM": "[missed]"
        }

        try:
            versions["Salome"] = salomepl.utils.SalomeManager().version()
            versions["OpenFOAM"] = openfoam.version()

        except Exception:
            pass

        return "\n".join([ f"{ k }: { v }" for k, v in versions.items() ])

    
    def loadFromScratch(self, configpath: str = None) -> list:
        """Loads parameters from configuration file and expands special values

        :return: 
            List of dicts with parameters
        """
        config = configpath or self.env["CONFIG"]

        if not os.path.exists(config):
            logger.error("Missed configuration file")
            return

        else:
            logger.info(f"Configuration file: { config }")

        buf = toml.load(config).get("structures")
        paramsAll = []


        for entry in buf:
            #   Shortcuts
            _theta = entry["structure"]["theta"]
            thetaMin = int(_theta[0] / _theta[2])
            thetaMax = int(_theta[1] / _theta[2]) + 1
            thetaList = list(
                map(lambda n: n * _theta[2], range(thetaMin, thetaMax))
            )

            _thickness = entry["mesh"]["thickness"]
            count = len(thetaList)
            thicknessList = list(
                map(lambda n: _thickness[0] + n * (_thickness[1] - _thickness[0]) / (count - 1), range(0, count))
            )

            for direction in entry["structure"]["directions"]:
                for n, theta in enumerate(thetaList):
                    mesh = deepcopy(entry["mesh"])
                    mesh["thickness"] = thicknessList[n]

                    entryNew = {
                        "structure": dict(
                            type = entry["structure"]["type"],
                            theta = theta,
                            direction = [ float(num) for num in direction ],
                            filletsEnabled = entry["structure"]["filletsEnabled"]
                        ),
                        "mesh": mesh,
                        "submesh": deepcopy(entry["submesh"]),
                        "meshresult": dict(),
                        "flow": deepcopy(entry["flow"]),
                        "flowapproximation": deepcopy(entry["flowapproximation"]),
                        "flowresult": dict(),
                    }


                    
                    paramsAll.append(entryNew)

        return paramsAll

  

    def getCasePath(self, path: str = None) -> str:
        """Constructs case path from control parameters
        
        :return: Absolute path to case
        :rtype: str
        """
        structure = self.params.get("structure")

        if not structure:
            logger.error("Trying to use empty parameters")
            return

        if path:
            path = os.path.join(path, "build")
    
        else:
            path = self.env["BUILD"]

        return os.path.join(
            path, 
            structure["type"],
            "direction-{}".format(str(structure['direction']).replace(" ", "")),
            f"theta-{ structure['theta'] }"
        )


    def computeMesh(self, path):
        """Computes a mesh on shape via Salome

        :return: Process output, error messages and returncode
        :rtype: tuple(str, str, int)
        """
        p = self.params["structure"]
        scriptpath = os.path.join(self.env["ROOT"], "anisotropy/core/cli.py")
        salomeargs = [
            "computemesh",
            p["type"], 
            p["direction"], 
            p["theta"],
            path
        ]
        manager = salomepl.utils.SalomeManager()
        casepath = self.getCasePath(path)

        self.params["meshresult"]["meshStatus"] = "Computing"
        self.update()
        timer = Timer()

        out, err, returncode = manager.execute(
            scriptpath, 
            *salomeargs, 
            timeout = self.env["salome_timeout"],
            root = self.env["ROOT"],
            logpath = casepath
        )
        self.load(p["type"], p["direction"], p["theta"])

        if not returncode:
            self.params["meshresult"].update(
                meshStatus = "Done",
                meshCalculationTime = timer.elapsed()
            )

        else:
            self.params["meshresult"].update(
                meshStatus = "Failed"
            )

        self.update()

        return out, err, returncode


    def genmesh(self, path):
        """Computes a mesh on shape

        Warning: Working only inside Salome Environment
        """

        setupLogger(logger, logging.INFO, self.env["LOG"])
        p = self.params

        sGeometry, sMesh = dict(
            simple = (Simple, SimpleMesh),
            bodyCentered = (BodyCentered, BodyCenteredMesh),
            faceCentered = (FaceCentered, FaceCenteredMesh)
        )[p["structure"]["type"]]

        #   Shape
        logger.info("Constructing shape ...")
        geometry = sGeometry(**p["structure"])
        geometry.build()

        #   Mesh
        logger.info("Prepairing mesh ...")
        mesh = sMesh(geometry)
        mesh.build()
        
        logger.info("Computing mesh ...")
        out, err, returncode = mesh.compute()


        if not returncode:
            mesh.removePyramids()
            mesh.createGroups()

            casePath = self.getCasePath(path)
            os.makedirs(casePath, exist_ok = True)
            logger.info("Exporting mesh ...")
            out, err, returncode = mesh.export(os.path.join(casePath, "mesh.unv"))
    
            if returncode:
                logger.error(err)

        # NOTE: edit from here
            meshStats = mesh.stats()
            p["meshresult"].update(
                surfaceArea = surfaceArea,
                volume = volume,
                volumeCell = shapeGeometry.volumeCell,
                **meshStats
            )
            self.update()

        else:
            logger.error(err)

            p["meshresult"].update(
                surfaceArea = surfaceArea,
                volume = volume,
                volumeCell = shapeGeometry.volumeCell
            )
            self.update()


    def computeFlow(self, path):
        """Computes a flow on mesh via OpenFOAM

        :return: 
            Process output, error messages and returncode
        """
        ###
        #   Case preparation
        ##
        foamCase = [ "0", "constant", "system" ]
        #self.params["flowresult"] = dict()
        self.params["flowresult"]["flowStatus"] = "Computing"
        self.update()
        timer = Timer()

        flow = self.params["flow"]
        flowapproximation = self.params["flowapproximation"]

        # ISSUE: ideasUnvToFoam cannot import mesh with '-case' flag so 'os.chdir' for that
        casePath = self.getCasePath(path)

        if not os.path.exists(casePath):
            err = f"Cannot find case path { casePath }"
            self.params["flowresult"]["flowStatus"] = "Failed"
            self.update()

            return "", err, 1

        os.chdir(casePath)
        openfoam.foamClean()

        for d in foamCase:
            shutil.copytree(
                os.path.join(self.env["openfoam_template"], d), 
                os.path.join(casePath, d)
            )
        
        ###
        #   Mesh manipulations
        ##
        if not os.path.exists("mesh.unv"):
            os.chdir(path or self.env["ROOT"])

            err = f"Missed 'mesh.unv'"
            self.params["flowresult"]["flowStatus"] = "Failed"
            self.update()

            return "", err, 1

        out, err, returncode = openfoam.ideasUnvToFoam("mesh.unv")

        out, err, returncode = openfoam.checkMesh()
        
        if out: logger.warning(out)

        out, err, returncode = openfoam.simpleFoam()

        if not returncode:
            self.params["flowresult"]["flowCalculationTime"] = timer.elapsed()
            self.params["flowresult"]["flowStatus"] = "Done"

        else:
            self.params["flowresult"]["flowStatus"] = "Failed"

        self.update()
        os.chdir(path or self.env["ROOT"])
        
        return out, str(err, "utf-8"), returncode


    def flowRate(self):
        casePath = self.getCasePath()
        foamPostProcessing = "postProcessing/flowRatePatch(name=outlet)/0/surfaceFieldValue.dat"
        path = os.path.join(casePath, foamPostProcessing)

        if not os.path.exists(path):
            logger.warning(f"Unable to compute flow rate. Missed { path }")

            return

        with open(path, "r") as io:
            lastLine = io.readlines()[-1]
            flowRate = float(lastLine.replace(" ", "").replace("\n", "").split("\t")[1])

        self.params["flowresult"]["flowRate"] = flowRate
        self.update()

        return flowRate


    def porosity(self):
        mr = self.params["meshresult"] 
        fr = self.params["flowresult"]

        fr["porosity"] = mr["volume"] / mr["volumeCell"]
        self.update()

        return fr["porosity"]
