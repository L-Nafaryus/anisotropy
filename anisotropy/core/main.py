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
setupLogger(logger, logging.INFO, env["LOG"])

peeweeLogger = logging.getLogger("peewee")
peeweeLogger.setLevel(logging.INFO)


class Anisotropy(object):
    """Ultimate class that organize whole working process"""

    def __init__(self):
        """Constructor method"""

        self.env = env
        self.db = Database("anisotropy", env["db_path"])
        self.params = []


    def load(self, structure_type: str, structure_direction: list, structure_theta: float):
        self.db.setup()
        self.params = self.db.load(structure_type, structure_direction, structure_theta)

    def update(self, params: dict = None):
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
            versions["Salome"] = salomepl.utils.version()
            versions["OpenFOAM"] = openfoam.version()

        except Exception:
            pass

        return "\n".join([ f"{ k }: { v }" for k, v in versions.items() ])

    
    def loadFromScratch(self) -> list:
        """Loads parameters from configuration file and expands special values

        :return: List of dicts with parameters
        :rtype: list
        """

        if not os.path.exists(self.env["CONFIG"]):
            logger.error("Missed default configuration file")
            return

        buf = toml.load(self.env["CONFIG"]).get("structures")
        paramsAll = []

        # TODO: custom config and merge
        
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
                        "flowapprox": deepcopy(entry["flowapprox"])
                    }

                    # For type = fixedValue only
                    _velocity = entryNew["flowapprox"]["velocity"]["boundaryField"]["inlet"]["value"]
                    entryNew["flowapprox"]["velocity"]["boundaryField"]["inlet"]["value"] = [ 
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
            #**structure,
            L = L,
            r0 = r0,
            radius = radius,
            fillets = fillets 
        )

    def getCasePath(self) -> str:
        """Constructs case path from main control parameters
        
        :return: Absolute path to case
        :rtype: str
        """
        structure = self.params.get("structure")

        if not structure:
            logger.error("Trying to use empty parameters")
            return

        return os.path.join(
            self.env["BUILD"], 
            structure["type"],
            "direction-{}".format(str(structure['direction']).replace(" ", "")),
            f"theta-{ structure['theta'] }"
        )


    @timer
    def computeMesh(self, type, direction, theta):
        scriptpath = os.path.join(self.env["ROOT"], "anisotropy/core/cli.py")
        port = 2900

        return salomepl.utils.runSalome(
            self.env["salome_port"], 
            scriptpath, 
            self.env["ROOT"],
            "computemesh", type, direction, theta,
            logpath = os.path.join(self.env["LOG"], "salome.log")
        )

    def genmesh(self):
        # ISSUE: double logger output

        import salome 

        p = self.params

        logger.info("\n".join([
            "genmesh:",
            f"structure type:\t{ p['structure']['type'] }",
            f"coefficient:\t{ p['structure']['theta'] }",
            f"fillet:\t{ p['structure']['fillets'] }",
            f"flow direction:\t{ p['structure']['direction'] }"
        ]))

        salome.salome_init()


        ###
        #   Shape
        ##
        geompy = salomepl.geometry.getGeom()
        structure = dict(
            simple = Simple,
            bodyCentered = BodyCentered,
            faceCentered = FaceCentered
        )[p["structure"]["type"]]
        shape, groups = structure(**p["structure"]).build()

        [length, surfaceArea, volume] = geompy.BasicProperties(shape, theTolerance = 1e-06)

        logger.info("\n".join([
            "shape:",
            f"edges length:\t{ length }",
            f"surface area:\t{ surfaceArea }",
            f"volume:\t{ volume }"
        ]))


        ###
        #   Mesh
        ##
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
        returncode, errors = mesh.compute()

        if not returncode:
            mesh.removePyramids()
            mesh.assignGroups()

            casePath = self.getCasePath()
            os.makedirs(casePath, exist_ok = True)
            mesh.exportUNV(os.path.join(casePath, "mesh.unv"))

            meshStats = mesh.stats()
            p["meshresult"] = dict(
                surfaceArea = surfaceArea,
                volume = volume,
                **meshStats
            )
            self.update()

            logger.info("mesh stats:\n{}".format(
                "\n".join(map(lambda v: f"{ v[0] }:\t{ v[1] }", meshStats.items()))
            ))

        else:
            logger.error(errors)

            p["meshresult"] = dict(
                surfaceArea = surfaceArea,
                volume = volume
            )
            self.update()

        salome.salome_close()

    @timer
    def computeFlow(self, type, direction, theta):
        ###
        #   Case preparation
        ##
        foamCase = [ "0", "constant", "system" ]

        flow = self.params["flow"]
        flowapprox = self.params["flowapprox"]

        # ISSUE: ideasUnvToFoam cannot import mesh with '-case' flag so 'os.chdir' for that
        casePath = self.getCasePath()
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
            os.chdir(self.env["ROOT"])
            return 1

        out, err, returncode = openfoam.ideasUnvToFoam("mesh.unv")

        if returncode:
            os.chdir(self.env["ROOT"])
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

        pressureBF = flowapprox["pressure"]["boundaryField"]
        velocityBF = flowapprox["velocity"]["boundaryField"]

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
        if out:
            logger.info(out)

        ###
        #   Check results
        ##

        if returncode == 0:
            postProcessing = "postProcessing/flowRatePatch(name=outlet)/0/surfaceFieldValue.dat"

            with open(os.path.join(casePath, postProcessing), "r") as io:
                lastLine = io.readlines()[-1]
                flowRate = float(lastLine.replace(" ", "").replace("\n", "").split("\t")[1])
                
            self.params["flowresult"] = dict(
                flowRate = flowRate
            )

        self.update()

        os.chdir(self.env["ROOT"])
        
        return out, err, returncode

    
    def _queue(self):
        pass

    def computeAll(self):
        pass


