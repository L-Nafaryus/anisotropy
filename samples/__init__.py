from collections import namedtuple
import os, sys
import logging
from pyquaternion import Quaternion
import math

ROOT = "/home/nafaryus/projects/anisotrope-cube"
sys.path.append(ROOT)

LOG = os.path.join(ROOT, "logs")

import salome

from simpleCubic import simpleCubic
from faceCenteredCubic import faceCenteredCubic
from bodyCenteredCubic import bodyCenteredCubic

from src import geometry_utils
from src import mesh_utils

def genMesh(stype, theta, fillet, flowdirection, saveto):
    _G = globals()

    structure = _G.get(stype)

    if structure:
        salome.salome_init()

        grains, geometry1, geometry2 = structure(theta, fillet)
        geometry = geometry1
        
        if flowdirection == [1, 1, 1]:
            geometry = geometry2
            norm = [-1, 1, 0]
            bcount = 6

            # initial angle
            angle = math.pi / 6
            v1 = Quaternion(axis = norm, angle = math.pi / 2).rotate(flowdirection)
            normvec = Quaternion(axis = flowdirection, angle = angle).rotate(v1)
            direction = [1, 1, 1]

        if flowdirection == [1, 0, 0]:
            normvec = [0, 0, 1]
            bcount = 4
            direction = [1, 1, 0]

        if flowdirection == [0, 0, 1]:
            normvec = [1, 1, 0]
            bcount = 4
            direction = [0, 0, 1]
        
        #
        geometry = geometry_utils.geompy.RemoveExtraEdges(geometry, False) 

        #
        boundary = geometry_utils.createBoundary(geometry, bcount, direction, normvec, grains)

        fineness = 1
        viscousLayers = {
            "thickness": 0.0001,
            "number": 3,
            "stretch": 1.2
        }
        mesh = mesh_utils.meshCreate(geometry, boundary, fineness, viscousLayers)
        mesh_utils.meshCompute(mesh)

        mesh_utils.meshExport(mesh, saveto)

        salome.salome_close()

    else:
        raise Exception("Unknown sample function")


if __name__ == "__main__":
    
    logging.basicConfig(
        level=logging.INFO, 
        format="%(levelname)s: %(message)s",
        handlers = [
            logging.StreamHandler(),
            logging.FileHandler("{}/cubic.log".format(LOG))
        ])
    
    stype = str(sys.argv[1])
    theta = float(sys.argv[2])
    fillet = True if int(sys.argv[3]) == 1 else False
    flowdirection = [int(coord) for coord in sys.argv[4]]
    saveto = str(sys.argv[5])

    logging.info("""genMesh: 
    structure type:\t{}
    coefficient:\t{}
    fillet:\t{}
    flow direction:\t{}
    export path:\t{}""".format(stype, theta, fillet, flowdirection, saveto))

    genMesh(stype, theta, fillet, flowdirection, saveto)

