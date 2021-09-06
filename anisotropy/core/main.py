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
from anisotropy.core.utils import setupLogger, timer
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
        self.db = Database(self.env["db_name"], self.env["db_path"])
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

        :return: Versions joined by next line symbol
        :rtype: str
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

        :return: List of dicts with parameters
        :rtype: list
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
                        "flow": deepcopy(entry["flow"]),
                        "flowapproximation": deepcopy(entry["flowapproximation"])
                    }

                    # For `type = fixedValue` only
                    _velocity = entryNew["flowapproximation"]["velocity"]["boundaryField"]["inlet"]["value"]
                    entryNew["flowapproximation"]["velocity"]["boundaryField"]["inlet"]["value"] = [ 
                        val * _velocity for val in entryNew["structure"]["direction"] 
                    ]

                    _velocity = entryNew["flow"]["velocity"]["boundaryField"]["inlet"]["value"]
                    entryNew["flow"]["velocity"]["boundaryField"]["inlet"]["value"] = [ 
                        val * _velocity for val in entryNew["structure"]["direction"] 
                    ]

                    
                    paramsAll.append(entryNew)

        return paramsAll

    
    def evalParams(self):
        """Evals specific geometry(structure) parameters"""

        structure = self.params.get("structure")

        if not structure:
            logger.error("Trying to eval empty parameters")
            return
        
        if structure["type"] == "simple":
            thetaMin = 0.01
            thetaMax = 0.28

            r0 = 1
            L = 2 * r0
            radius = r0 / (1 - structure["theta"])

            C1, C2 = 0.8, 0.5
            Cf = C1 + (C2 - C1) / (thetaMax - thetaMin) * (structure["theta"] - thetaMin)
            delta = 0.2
            fillets = delta - Cf * (radius - r0)

        elif structure["type"] == "faceCentered":
            thetaMin = 0.01
            thetaMax = 0.13

            L = 1.0
            r0 = L * sqrt(2) / 4
            radius = r0 / (1 - structure["theta"])

            C1, C2 = 0.3, 0.2
            Cf = C1 + (C2 - C1) / (thetaMax - thetaMin) * (structure["theta"] - thetaMin)
            delta = 0.012
            fillets = delta - Cf * (radius - r0)

        elif structure["type"] == "bodyCentered":
            thetaMin = 0.01
            thetaMax = 0.18
    
            L = 1.0
            r0 = L * sqrt(3) / 4
            radius = r0 / (1 - structure["theta"])

            C1, C2 = 0.3, 0.2
            Cf = C1 + (C2 - C1) / (thetaMax - thetaMin) * (structure["theta"] - thetaMin)
            delta = 0.02
            fillets = delta - Cf * (radius - r0)

        self.params["structure"].update(
            L = L,
            r0 = r0,
            radius = radius,
            fillets = fillets 
        )

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

        return manager.execute(
            scriptpath, 
            *salomeargs, 
            timeout = self.env["salome_timeout"],
            root = self.env["ROOT"],
            logpath = casepath
        )


    def genmesh(self, path):
        """Computes a mesh on shape

        Warning: Working only inside Salome Environment
        """

        setupLogger(logger, logging.INFO, self.env["LOG"])
        p = self.params

        ###
        #   Shape
        ##
        logger.info("Constructing shape ...")

        geompy = salomepl.geometry.getGeom()
        structure = dict(
            simple = Simple,
            bodyCentered = BodyCentered,
            faceCentered = FaceCentered
        )[p["structure"]["type"]]
        shape, groups = structure(**p["structure"]).build()

        [length, surfaceArea, volume] = geompy.BasicProperties(shape, theTolerance = 1e-06)


        ###
        #   Mesh
        ##
        logger.info("Prepairing mesh ...")

        mp = p["mesh"]

        lengths = [
            geompy.BasicProperties(edge)[0] for edge in geompy.SubShapeAll(shape, geompy.ShapeType["EDGE"]) 
        ]
        meanSize = sum(lengths) / len(lengths)
        mp["maxSize"] = meanSize
        mp["minSize"] = meanSize * 1e-1
        mp["chordalError"] = mp["maxSize"] / 2

        faces = []
        for group in groups:
            if group.GetName() in mp["facesToIgnore"]:
                faces.append(group)


        mesh = salomepl.mesh.Mesh(shape)
        mesh.Tetrahedron(**mp)

        if mp["viscousLayers"]:
            mesh.ViscousLayers(**mp, faces = faces)

        smp = p["submesh"]

        for submesh in smp:
            for group in groups:
                if submesh["name"] == group.GetName():
                    subshape = group

                    submesh["maxSize"] = meanSize * 1e-1
                    submesh["minSize"] = meanSize * 1e-3
                    submesh["chordalError"] = submesh["minSize"] * 1e+1

                    mesh.Triangle(subshape, **submesh)


        self.update()
        logger.info("Computing mesh ...")
        out, err, returncode = mesh.compute()

        ###
        #   Results
        ##
        p["meshresult"] = dict()

        if not returncode:
            mesh.removePyramids()
            mesh.assignGroups()

            casePath = self.getCasePath(path)
            os.makedirs(casePath, exist_ok = True)
            logger.info("Exporting mesh ...")
            returncode, err = mesh.exportUNV(os.path.join(casePath, "mesh.unv"))
    
            if returncode:
                logger.error(err)

            meshStats = mesh.stats()
            p["meshresult"].update(
                status = "Done",
                surfaceArea = surfaceArea,
                volume = volume,
                **meshStats
            )
            self.update()

        else:
            logger.error(err)

            p["meshresult"].update(
                status = "Failed",
                surfaceArea = surfaceArea,
                volume = volume
            )
            self.update()


    def computeFlow(self, path):
        """Computes a flow on mesh via OpenFOAM

        :return: Process output, error messages and returncode
        :rtype: tuple(str, str, int)
        """
        ###
        #   Case preparation
        ##
        foamCase = [ "0", "constant", "system" ]

        flow = self.params["flow"]
        flowapproximation = self.params["flowapproximation"]

        # ISSUE: ideasUnvToFoam cannot import mesh with '-case' flag so 'os.chdir' for that
        casePath = self.getCasePath()

        if not os.path.exists(casePath):
            logger.warning(f"Cannot find case path. Skipping computation ...\n\t{ casePath }")
            return "", "", 1

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
            logger.error(f"missed 'mesh.unv'")
            os.chdir(path or self.env["ROOT"])
            return "", "", 1

        out, err, returncode = openfoam.ideasUnvToFoam("mesh.unv")

        if returncode:
            os.chdir(path or self.env["ROOT"])
            return out, err, returncode
        
        openfoam.createPatch(dictfile = "system/createPatchDict")

        openfoam.foamDictionary(
            "constant/polyMesh/boundary", 
            "entry0.defaultFaces.type", 
            "wall"
        )
        openfoam.foamDictionary(
            "constant/polyMesh/boundary", 
            "entry0.defaultFaces.inGroups", 
            "1 (wall)"
        )
        
        out = openfoam.checkMesh()
        
        if out:
            logger.info(out)
        
        openfoam.transformPoints(flow["scale"])
        
        ###
        #   Decomposition and initial approximation
        #
        #   NOTE: Temporary without decomposition
        ##
        openfoam.foamDictionary(
            "constant/transportProperties",
            "nu",
            str(flow["transportProperties"]["nu"])
        )

        #openfoam.decomposePar()

        openfoam.renumberMesh()

        pressureBF = flowapproximation["pressure"]["boundaryField"]
        velocityBF = flowapproximation["velocity"]["boundaryField"]

        openfoam.foamDictionary(
            "0/p", 
            "boundaryField.inlet.value", 
            openfoam.uniform(pressureBF["inlet"]["value"])
        )
        openfoam.foamDictionary(
            "0/p", 
            "boundaryField.outlet.value", 
            openfoam.uniform(pressureBF["outlet"]["value"])
        )
        
        openfoam.foamDictionary(
            "0/U", 
            "boundaryField.inlet.value", 
            openfoam.uniform(velocityBF["inlet"]["value"])
        )
        
        openfoam.potentialFoam()
        
        ###
        #   Main computation
        ##
        pressureBF = flow["pressure"]["boundaryField"]
        velocityBF = flow["velocity"]["boundaryField"]

        openfoam.foamDictionary(
            "0/U",
            "boundaryField.inlet.type",
            velocityBF["inlet"]["type"] 
        )
        openfoam.foamDictionary(
            "0/U",
            "boundaryField.inlet.value",
            openfoam.uniform(velocityBF["inlet"]["value"])
        )

        #for n in range(os.cpu_count()):
        #    openfoam.foamDictionary(
        #        f"processor{n}/0/U", 
        #        "boundaryField.inlet.type", 
        #        velocityBF.inlet.type
        #    )
        #    openfoam.foamDictionary(
        #        f"processor{n}/0/U", 
        #        "boundaryField.inlet.value", 
        #        openfoam.uniform(velocityBF.inlet.value[direction])
        #    )
        
        out, err, returncode = openfoam.simpleFoam()

        ###
        #   Results
        ##
        self.params["flowresult"] = dict()

        if not returncode:
            postProcessing = "postProcessing/flowRatePatch(name=outlet)/0/surfaceFieldValue.dat"

            with open(os.path.join(casePath, postProcessing), "r") as io:
                lastLine = io.readlines()[-1]
                flowRate = float(lastLine.replace(" ", "").replace("\n", "").split("\t")[1])
                
            self.params["flowresult"].update(
                status = "Done",
                flowRate = flowRate
            )

        else:
            self.params["flowresult"].update(
                status = "Failed"
            )


        self.update()

        os.chdir(self.env["ROOT"])
        
        return out, str(err, "utf-8"), returncode

    
