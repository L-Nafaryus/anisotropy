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

from salomepl.simple import simple 
from salomepl.faceCentered import faceCentered 
from salomepl.bodyCentered import bodyCentered 

from salomepl.geometry import getGeom 
from salomepl.mesh import Mesh, Fineness, ExtrusionMethod, defaultParameters 


def genmesh(config):
    
    logger.info(f"""genmesh: 
    structure type:\t{ config.structure }
    coefficient:\t{ config.geometry.theta }
    fillet:\t{ config.geometry.fillet }
    flow direction:\t{ config.geometry.direction }""")

    salome.salome_init()
    
    ###
    #   Shape
    ##
    geompy = getGeom()
    structure = globals().get(config.structure)
    shape, groups = structure(config.geometry.theta, config.geometry.fillet, config.geometry.direction)
    [length, surfaceArea, volume] = geompy.BasicProperties(shape, theTolerance = 1e-06)

    logger.info(f"""shape:
    edges length:\t{ length }
    surface area:\t{ surfaceArea }
    volume:\t{ volume }""")
    
    ###
    #   Mesh
    ##
    config = dict(config)

    mconfig = defaultParameters(**config["mesh"])

    lengths = [ geompy.BasicProperties(edge)[0] for edge in geompy.SubShapeAll(shape, geompy.ShapeType["EDGE"]) ]
    meanSize = sum(lengths) / len(lengths)
    mconfig["maxSize"] = meanSize
    mconfig["minSize"] = meanSize * 1e-1
    mconfig["chordalError"] = mconfig["maxSize"] / 2

    faces = []
    for group in groups:
        if group.GetName() in mconfig["facesToIgnore"]:
            faces.append(group)

    mconfig["faces"] = faces

    mesh = Mesh(shape)
    mesh.Tetrahedron(**mconfig)

    if mconfig["viscousLayers"]:
        mesh.ViscousLayers(**mconfig)
    
    config["mesh"].update(mconfig)
    smconfigs = config["mesh"]["submesh"]

    for name in smconfigs.keys():
        for group in groups:
            if group.GetName() == name:
                subshape = group
        
        smconfig = defaultParameters(**smconfigs[name])
        smconfig["maxSize"] = meanSize * 1e-1
        smconfig["minSize"] = meanSize * 1e-3
        smconfig["chordalError"] = smconfig["minSize"] * 1e+1
        
        mesh.Triangle(subshape, **smconfig)
        config["mesh"]["submesh"][name].update(smconfig)


    returncode, errors = mesh.compute()

    if not returncode:
        config["status"]["mesh"] = True
        
    else:
        logger.error(errors)

    with open(CONFIG, "w") as io:
        toml.dump(config, io)

    mesh.removePyramids()
    mesh.assignGroups()

    mesh.exportUNV(os.path.join(CASE, "mesh.unv"))

    stats = ""
    for k, v in mesh.stats().items():
        stats += f"{ k }:\t\t{ v }\n"

    logger.info(f"mesh stats:\n{ stats[ :-1] }")

    salome.salome_close()


if __name__ == "__main__":
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

    genmesh(config)

    
