###
#   This file executes inside salome environment
#
#   salome starts at user home directory
##
import os, sys
import math

import salome

# get project path from args
ROOT = sys.argv[6]
sys.path.append(ROOT)
# site-packages from virtual env
sys.path.append(os.path.join(ROOT, "env/lib/python3.9/site-packages"))

import toml
import logging
from anisotropy.utils import struct

CONFIG = os.path.join(ROOT, "conf/config.toml")
config = struct(toml.load(CONFIG))

LOG = os.path.join(ROOT, "logs")

logging.basicConfig(
    level = logging.INFO,
    format = config.logger.format,
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(f"{ LOG }/{ config.logger.name }.log")
    ]
)
logger = logging.getLogger(config.logger.name)

from salomepl.simple import simple 
from salomepl.faceCentered import faceCentered 
from salomepl.bodyCentered import bodyCentered 

from salomepl.geometry import getGeom 
from salomepl.mesh import smeshBuilder, meshCreate, meshCompute, meshStats, meshExport


def main():

    stype = str(sys.argv[1])
    theta = float(sys.argv[2])
    fillet = int(sys.argv[3])
    flowdirection = [int(coord) for coord in sys.argv[4]]
    export = str(sys.argv[5])

    genmesh(stype, theta, fillet, flowdirection, export)


def genmesh(stype, theta, fillet, direction, export):

    logger.info("""genMesh: 
    structure type:\t{}
    coefficient:\t{}
    fillet:\t{}
    flow direction:\t{}
    export path:\t{}""".format(stype, theta, fillet, direction, export))

    salome.salome_init()
    
    ###
    #   Shape
    ##
    geompy = getGeom()
    structure = globals().get(stype)
    shape, groups = structure(theta, fillet, direction)
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

    meshParameters = getattr(config, stype).mesh
    meshParameters.facesToIgnore = facesToIgnore
    meshParameters.extrusionMethod = smeshBuilder.SURF_OFFSET_SMOOTH
    
    mesh = meshCreate(shape, groups, meshParameters) #fineness, parameters, viscousLayers)
    meshCompute(mesh)

    meshStats(mesh)
    meshExport(mesh, export)
    
    salome.salome_close()


if __name__ == "__main__":
    main()

    
