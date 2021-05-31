import os, sys
import time
from datetime import timedelta
import shutil

sys.path.append(os.path.abspath("../"))

from utils import struct, checkEnv
import toml
import logging

CONFIG = os.path.abspath("../conf/config.toml")
config = struct(toml.load(CONFIG))

def main():

    #CONFIG = os.path.abspath("../conf/config.toml")
    #config = struct(toml.load(CONFIG))
    
    LOG = os.path.abspath("../logs")
    if not os.path.exists(LOG):
        os.makedirs(LOG)

    BUILD = os.path.abspath("../build")
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

    if checkEnv():
        return

    tasks = createTasks()

    for task in tasks:
        logger.info("-" * 80)
        logger.info(f"""main:
        task:\t{tasks.index(task) + 1} / {len(tasks)}
        cpu count:\t{os.cpu_count()}
        structure:\t{task.structure}
        direction:\t{task.direction}
        theta:\t{task.theta}
        fillet:\t{task.fillet}
        export:\t{task.export}""")

        if not os.path.exists(task.export):
            os.makedirs(task.export)
       
        createMesh(task)

        if os.path.exists(os.path.join(task.export, "mesh.unv")):
            task.mesh = True

        returncode = calculate(task)

        if not returncode:
            task.flow = True

        with open(os.path.join(config.LOG, "tasks.log"), "a") as io:
            idx = tasks.index(task)
            io.write(f"""Task {idx}:
    structure:\t{task.structure}
    direction:\t{task.direction}
    theta:\t{task.theta}
    mesh:\t{task.mesh}
    flow:\t{task.flow}\n""")


    logger.info(f"Warnings: {logger.warnings}\tErrors: {logger.errors}")


def createTasks():
    tasks = []

    for structure in config.base.__dict__.keys():
        if getattr(config.base, structure):
            for direction in getattr(config, structure).geometry.directions:
                for theta in getattr(config, structure).theta:
                    task = struct(
                        structure = structure, 
                        theta = theta, 
                        fillet = getattr(config, structure).geometry.fillet, 
                        direction = direction, 
                        export = os.path.abspath(f"../build/{ structure }/direction-{ direction[0] }{ direction [1] }{ direction [2] }/theta-{ theta }"),
                        mesh = False,
                        flow = False
                    )

                    tasks.append(task)

    return tasks

from salomepl.utils import runExecute

def createMesh(task):
    scriptpath = os.path.abspath("../salomepl/genmesh.py")
    port = 2810
    stime = time.monotonic()

    args = (
        task.structure, 
        task.theta, 
        int(task.fillet), 
        "".join([str(coord) for coord in task.direction]), 
        os.path.join(task.export, "mesh.unv"),
        os.path.abspath("../")
    )
    returncode = runExecute(port, scriptpath, *args)
    
    etime = time.monotonic()
    logger.info("createMesh: elapsed time: {}".format(timedelta(seconds = etime - stime)))


from openfoam import openfoam

def calculate(task):
    foamCase = [ "0", "constant", "system" ]

    os.chdir(task.export)
    openfoam.foamClean()

    for d in foamCase:
        shutil.copytree(
            os.path.abspath("../openfoam/template", d), 
            os.path.join(task.export, d)
        )
    
    stime = time.monotonic()

    if not os.path.exists("mesh.unv"):
        logger.critical(f"calculate: missed 'mesh.unv'")
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

    os.chdir(config.ROOT)
    
    etime = time.monotonic()
    logger.info("calculate: elapsed time: {}".format(timedelta(seconds = etime - stime)))

    return returncode



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

