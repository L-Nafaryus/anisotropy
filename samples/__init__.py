from collections import namedtuple
import os, sys
import logging
from pyquaternion import Quaternion
import math

ROOT = "/home/nafaryus/projects/anisotrope-cube"
sys.path.append(ROOT)

LOG = os.path.join(ROOT, "logs")

import salome

from simple import simpleCubic, simpleHexagonalPrism
from faceCentered import faceCenteredCubic, faceCenteredHexagonalPrism
from bodyCentered import bodyCenteredCubic, bodyCenteredHexagonalPrism

from src import geometry_utils
from src import mesh_utils

def genMesh(stype, theta, fillet, direction, saveto):

    logging.info("""genMesh: 
    structure type:\t{}
    coefficient:\t{}
    fillet:\t{}
    flow direction:\t{}
    export path:\t{}""".format(stype, theta, fillet, direction, saveto))

    params = (theta, fillet, direction)

    salome.salome_init()
    
    ###
    #   Structure and mesh configurations
    ##
    if stype == "simple":
        if direction in [[1, 0, 0], [0, 0, 1]]:
            structure = simpleCubic

        elif direction == [1, 1, 1]:
            structure = simpleHexagonalPrism

    elif stype == "faceCentered":
        if direction in [[1, 0, 0], [0, 0, 1]]:
            structure = faceCenteredCubic

        elif direction == [1, 1, 1]:
            structure = faceCenteredHexagonalPrism

    elif stype == "bodyCentered":
        if direction in [[1, 0, 0], [0, 0, 1]]:
            structure = bodyCenteredCubic

        elif direction == [1, 1, 1]:
            structure = bodyCenteredHexagonalPrism
    
    ###
    #   Shape
    ##
    geompy = geometry_utils.getGeom()
    shape, groups = structure(*params)
    [length, surfaceArea, volume] = geompy.BasicProperties(shape, theTolerance = 1e-06)

    logging.info("""shape:
    edges length:\t{}
    surface area:\t{}
    volume:\t{}""".format(length, surfaceArea, volume))
    
    ###
    #   Mesh
    ##
    fineness = 0
    parameters = mesh_utils.Parameters(
        minSize = 0.001,
        maxSize = 0.1,
        growthRate = 0.1,
        nbSegPerEdge = 5,
        nbSegPerRadius = 10,
        chordalErrorEnabled = False,
        chordalError = -1,
        secondOrder = False,
        optimize = True,
        quadAllowed = False,
        useSurfaceCurvature = True,
        fuseEdges = True,
        checkChartBoundary = False
    )
    
    facesToIgnore = []
    for group in groups:
        if group.GetName() in ["inlet", "outlet"]:
            facesToIgnore.append(group)

    viscousLayers = mesh_utils.ViscousLayers(
        thickness = 0.001,
        numberOfLayers = 3,
        stretchFactor = 1.2,
        isFacesToIgnore = True,
        facesToIgnore = facesToIgnore,
        extrusionMethod = mesh_utils.smeshBuilder.NODE_OFFSET
    )
    
    mesh = mesh_utils.meshCreate(shape, groups, fineness, parameters, viscousLayers)
    mesh_utils.meshCompute(mesh)

    mesh_utils.meshExport(mesh, saveto)

    salome.salome_close()


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

    genMesh(stype, theta, fillet, flowdirection, saveto)

