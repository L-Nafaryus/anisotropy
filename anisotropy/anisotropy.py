import os, sys
import time
from datetime import timedelta
import shutil

ROOT = "/".join(__file__.split("/")[:-2])
sys.path.append(os.path.abspath(ROOT))

from utils import struct
import toml
import logging

CONFIG = os.path.join(ROOT, "conf/config.toml")
config = struct(toml.load(CONFIG))

LOG = os.path.join(ROOT, "logs")
if not os.path.exists(LOG):
    os.makedirs(LOG)

BUILD = os.path.join(ROOT, "build")
if not os.path.exists(BUILD):
    os.makedirs(BUILD)

logging.basicConfig(
    level = logging.INFO,
    format = config.logger.format,
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(f"{ LOG }/{ config.logger.name }.log")
    ]
)
logger = logging.getLogger(config.logger.name)


def main():
    if checkEnv():
        return

    tasks = createTasks()

    for n, case in enumerate(tasks):
        logger.info("-" * 80)
        logger.info(f"""main:
        task:\t{ n + 1 } / { len(tasks) }
        cpu count:\t{ os.cpu_count() }
        case:\t{ case }""")
        
        ###
        #   Compute mesh
        ##
        computeMesh(case)
        
        task = struct(toml.load(os.path.join(case, "task.toml")))
        
        if not task.status.mesh:
            logger.critical("mesh not computed: Skipping flow computation")
            continue

        ###
        #   Compute flow
        ##
        computeFlow(case)
    

def createTasks():
    tasks = []

    for structure in config.base.__dict__.keys():
        ###
        #   Special values
        ##
        _theta = getattr(config, structure).parameters.theta
        getattr(config, structure).parameters.theta = [ n * _theta[2] for n in range(int(_theta[0] / _theta[2]), int(_theta[1] / _theta[2]) + 1) ]

        _thickness = getattr(config, structure).mesh.thickness
        _count = len(getattr(config, structure).parameters.theta)
        getattr(config, structure).mesh.thickness = [ _thickness[0] + n * (_thickness[1] - _thickness[0]) / (_count - 1) for n in range(0, _count) ]

    ###
    #   structure type / flow direction / coefficient theta
    ##
    for structure in config.base.__dict__.keys():
        if getattr(config.base, structure):
            for direction in getattr(config, structure).geometry.directions:
                for n, theta in enumerate(getattr(config, structure).parameters.theta):
                    case = os.path.join(
                        f"{ BUILD }",
                        f"{ structure }",
                        f"direction-{ direction[0] }{ direction [1] }{ direction [2] }", 
                        f"theta-{ theta }"
                    )

                    if not os.path.exists(case):
                        os.makedirs(case)

                    task = {
                        "logger": config.logger.__dict__,
                        "structure": structure,
                        "status": {
                            "mesh": False,
                            "flow": False
                        },
                        "parameters": {
                            "theta": theta
                        },
                        "geometry": {
                            "direction": direction,
                            "fillet": getattr(config, structure).geometry.fillet
                        },
                        "mesh": getattr(config, structure).mesh.__dict__ 
                    }

                    #task["mesh"]["thickness"] = task["mesh"]["thickness"][int(n)]
       
                    with open(os.path.join(case, "task.toml"), "w") as io:
                        toml.dump(task, io)

                    
                    tasks.append(case)

    return tasks


from salomepl.utils import runExecute, salomeVersion

def computeMesh(case):
    scriptpath = os.path.join(ROOT, "salomepl/genmesh.py")
    port = 2810
    stime = time.monotonic()

    returncode = runExecute(port, scriptpath, ROOT, case)
    
    etime = time.monotonic()
    logger.info("computeMesh: elapsed time: {}".format(timedelta(seconds = etime - stime)))


import openfoam

def computeFlow(case):
    foamCase = [ "0", "constant", "system" ]

    os.chdir(case)
    task = struct(toml.load(os.path.join(case, "task.toml")))
    openfoam.foamClean()

    for d in foamCase:
        shutil.copytree(
            os.path.join(ROOT, "openfoam/template", d), 
            os.path.join(case, d)
        )
    
    stime = time.monotonic()

    if not os.path.exists("mesh.unv"):
        logger.critical(f"computeFlow: missed 'mesh.unv'")
        return

    _, returncode = openfoam.ideasUnvToFoam("mesh.unv")

    if returncode:
        os.chdir(config.ROOT)

        return returncode
    
    openfoam.createPatch(dictfile = "system/createPatchDict.symetry")

    openfoam.foamDictionary("constant/polyMesh/boundary", "entry0.defaultFaces.type", "wall")
    openfoam.foamDictionary("constant/polyMesh/boundary", "entry0.defaultFaces.inGroups", "1 (wall)")
    
    openfoam.checkMesh()

    scale = (1e-5, 1e-5, 1e-5)
    openfoam.transformPoints(scale)
    
    openfoam.decomposePar()

    openfoam.renumberMesh()
    
    openfoam.potentialFoam()
    
    for n in range(os.cpu_count()):
        openfoam.foamDictionary(f"processor{n}/0/U", "boundaryField.inlet.type", "pressureInletVelocity")
        openfoam.foamDictionary(f"processor{n}/0/U", "boundaryField.inlet.value", "uniform (0 0 0)")
    
    returncode, out = openfoam.simpleFoam()
    if out:
        logger.info(out)

    if returncode == 0:
        task.status.flow = True

        with open(os.path.join(case, "task.toml"), "w") as io:
            toml.dump({
                "structure": task.structure,
                "logger": task.logger.__dict__,
                "status": task.status.__dict__,
                "parameters": task.parameters.__dict__,
                "geometry": task.geometry.__dict__,
                "mesh": task.mesh.__dict__
            }, io)

    os.chdir(ROOT)
    
    etime = time.monotonic()
    logger.info("computeFlow: elapsed time: {}".format(timedelta(seconds = etime - stime)))

    return returncode

def checkEnv():
    missed = False
    
    try:
        pythonVersion = "Python {}".format(sys.version.split(" ")[0])
        salomeplVersion = salomeVersion()
        openfoamVersion = openfoam.foamVersion()

    except Exception as e:
        logger.critical("Missed environment %s", e)
        missed = True

    else:
        logger.info(f"environment:\n\t{pythonVersion}\n\t{salomeplVersion}\n\t{openfoamVersion}")

    finally:
        return missed


def postprocessing(tasks):

    surfaceFieldValue = {}
    porosity = {}

    for task in tasks:
        direction = "direction-{}{}{}".format(task.direction[0], task.direction[1], task.direction[2]) 
        path = os.path.join(BUILD, task.structure, "postProcessing", direction)
        surfaceFieldValuePath = os.path.join(task.export, "postProcessing", "")

        if not os.path.exists(path):
            os.makedirs(path)
            
        surfaceFieldValues = [ line.strip().split() for line in open(surfaceFieldValuePath, "r").readlines() ]

        with open(os.path.join(path, "porosity.dat")) as io:
            io.write("{}\t{}".format(task.coeff, surfaceFieldValues[-1][1]))


###
#   Main entry
##
if __name__ == "__main__":
    main()

