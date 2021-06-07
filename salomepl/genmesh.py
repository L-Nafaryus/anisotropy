###
#   This file executes inside salome environment
#
#   salome starts at user home directory
#
#   sys.argv = [ .., ROOT, case ]
##
import os, sys
import math

import salome

# get project path from args
ROOT = sys.argv[1]
CASE = sys.argv[2]

sys.path.append(ROOT)
# site-packages from virtual env
sys.path.append(os.path.join(ROOT, "env/lib/python3.9/site-packages"))

import toml
import logging
from anisotropy.utils import struct

CONFIG = os.path.join(CASE, "task.toml")
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


def genmesh():

    logger.info(f"""genmesh: 
    structure type:\t{ config.structure }
    coefficient:\t{ config.parameters.theta }
    fillet:\t{ config.geometry.fillet }
    flow direction:\t{ config.geometry.direction }""")

    salome.salome_init()
    
    ###
    #   Shape
    ##
    geompy = getGeom()
    structure = globals().get(config.structure)
    shape, groups = structure(config.parameters.theta, config.geometry.fillet, config.geometry.direction)
    [length, surfaceArea, volume] = geompy.BasicProperties(shape, theTolerance = 1e-06)

    logger.info(f"""shape:
    edges length:\t{ length }
    surface area:\t{ surfaceArea }
    volume:\t{ volume }""")
    
    ###
    #   Mesh
    ##
    facesToIgnore = []
    for group in groups:
        if group.GetName() in ["inlet", "outlet"]:
            facesToIgnore.append(group)

    meshParameters = config.mesh
    meshParameters.facesToIgnore = facesToIgnore
    meshParameters.extrusionMethod = smeshBuilder.SURF_OFFSET_SMOOTH
    
    mesh = meshCreate(shape, groups, meshParameters)
    returncode = meshCompute(mesh)

    if returncode == 0:
        config.status.mesh = True

        with open(CONFIG, "w") as io:
            toml.dump(dict(config), io)

    meshStats(mesh)
    meshExport(mesh, os.path.join(CASE, "mesh.unv"))
    
    salome.salome_close()


if __name__ == "__main__":
    genmesh()

    
