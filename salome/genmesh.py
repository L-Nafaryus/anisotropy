###
#   This file executes inside salome environment
##
from collections import namedtuple
import os, sys
import logging
from pyquaternion import Quaternion
import math

import salome

sys.path.append(sys.argv[6])

import config
from config import logger
#from src import applogger
from simple import simpleCubic, simpleHexagonalPrism
from faceCentered import faceCenteredCubic, faceCenteredHexagonalPrism
from bodyCentered import bodyCenteredCubic, bodyCenteredHexagonalPrism

from src import geometry_utils
from src import mesh_utils


def main():

    stype = str(sys.argv[1])
    theta = float(sys.argv[2])
    fillet = int(sys.argv[3])
    flowdirection = [int(coord) for coord in sys.argv[4]]
    export = str(sys.argv[5])

    genMesh(stype, theta, fillet, flowdirection, export)


def genMesh(stype, theta, fillet, direction, export):

    logger.info("""genMesh: 
    structure type:\t{}
    coefficient:\t{}
    fillet:\t{}
    flow direction:\t{}
    export path:\t{}""".format(stype, theta, fillet, direction, export))

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

        fineness = config.simple.fineness
        parameters = config.simple.parameters
        viscousLayers = config.simple.viscousLayers

    elif stype == "faceCentered":
        if direction in [[1, 0, 0], [0, 0, 1]]:
            structure = faceCenteredCubic

        elif direction == [1, 1, 1]:
            structure = faceCenteredHexagonalPrism

        fineness = config.faceCentered.fineness
        parameters = config.faceCentered.parameters
        viscousLayers = config.faceCentered.viscousLayers

    elif stype == "bodyCentered":
        if direction in [[1, 0, 0], [0, 0, 1]]:
            structure = bodyCenteredCubic

        elif direction == [1, 1, 1]:
            structure = bodyCenteredHexagonalPrism
    
        fineness = config.bodyCentered.fineness
        parameters = config.bodyCentered.parameters
        viscousLayers = config.bodyCentered.viscousLayers

    ###
    #   Shape
    ##
    geompy = geometry_utils.getGeom()
    shape, groups = structure(*params)
    [length, surfaceArea, volume] = geompy.BasicProperties(shape, theTolerance = 1e-06)

    logger.info("""shape:
    edges length:\t{}
    surface area:\t{}
    volume:\t{}""".format(length, surfaceArea, volume))
    
    ###
    #   Mesh
    ##
    facesToIgnore = []
    for group in groups:
        if group.GetName() in ["inlet", "outlet"]:
            facesToIgnore.append(group)

    viscousLayers.facesToIgnore = facesToIgnore
    viscousLayers.extrusionMethod = mesh_utils.smeshBuilder.SURF_OFFSET_SMOOTH
    
    mesh = mesh_utils.meshCreate(shape, groups, fineness, parameters, viscousLayers)
    mesh_utils.meshCompute(mesh)

    mesh_utils.meshStats(mesh)
    mesh_utils.meshExport(mesh, export)
    
    salome.salome_close()


if __name__ == "__main__":
    main()

    
