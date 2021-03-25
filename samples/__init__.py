from collections import namedtuple
import os, sys
import logging

ROOT = "/home/nafaryus/projects/anisotrope-cube"
sys.path.append(ROOT)

LOG = os.path.join(ROOT, "logs")

import salome

from simpleCubic import simpleCubic
from faceCenteredCubic import faceCenteredCubic
from bodyCenteredCubic import bodyCenteredCubic

from src import geometry_utils
from src import mesh_utils

def genMesh(stype, theta, flowdirection, saveto):
    _G = globals()

    structure = _G.get(stype)

    if structure:
        salome.salome_init()

        grains, cubic, rhombohedron = structure(theta)
        fd = namedtuple("fd", ["x", "y", "z"])
        geometry = cubic
        
        if flowdirection == [1, 1, 1]:
            geometry = rhombohedron
            direction = fd([1, 1, 1], [1, -1, 1], [1, -1, -1])
        
        else:
            geometry = cubic

        if flowdirection == [1, 0, 0]:
            direction = fd([1, 1, 0], [1, -1, 0], [0, 0, 1])

        if flowdirection == [0, 0, 1]:
            direction = fd([0, 0, 1], [1, -1, 0], [1, 1, 0])
        
        boundary = geometry_utils.boundaryCreate(geometry, direction, grains)

        fineness = 3
        mesh = mesh_utils.meshCreate(geometry, boundary, fineness)
        mesh_utils.meshCompute(mesh)

        #path = os.path.join(saveto, 
        #                 stype, 
        #                 "theta-%s" % theta, 
        #                 "direction-{}{}{}".format(flowdirection[0], flowdirection[1], flowdirection[2]))

        #if not os.path.exists(path):
        #    logging.info("Creating directory: {}".format(path))
        #    os.makedirs(path)

        mesh_utils.meshExport(mesh, saveto) # os.path.join(path, "mesh.unv"))

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
    
    fancyline = "--------------------------------------------------------------------------------"
    logging.info(fancyline)

    stype = str(sys.argv[1])
    theta = float(sys.argv[2])

    #ignore = "[], "
    flowdirection = [int(coord) for coord in sys.argv[3]]

    #for sym in str(sys.argv[3]):
    #   if sym not in list(ignore):
    #       flowdirection.append(int(sym))

    saveto = str(sys.argv[4])

    logging.info("""Args: 
    structure type:\t{}
    coefficient:\t{}
    flow direction:\t{}
    export path:\t{}\n""".format(stype, theta, flowdirection, saveto))

    #print(flowdirection)

    genMesh(stype, theta, flowdirection, saveto)

    logging.info(fancyline)
