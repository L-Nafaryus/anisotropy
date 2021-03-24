from .simpleCubic import simpleCubic
from .faceCenteredCubic import faceCenteredCubic
from .bodyCenteredCubic import bodyCenteredCubic

from src import geometry_utils
from src import mesh_utils

import salome
from collections import namedtuple
import os

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

        path = os.path.join(saveto, 
                         stype, 
                         "theta-%s" % theta, 
                         "direction-{}{}{}".format(flowdirection[0], flowdirection[1], flowdirection[2]))

        if not os.path.exists(path):
            logging.info("Creating directory: {}".format(path))
            os.makedirs(path)

        mesh_utils.meshExport(mesh, os.path.join(path, "mesh.unv"))

        salome.salome_close()

    else:
        raise Exception("Unknown sample function")
