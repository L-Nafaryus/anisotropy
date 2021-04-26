import os, sys
from collections import namedtuple
import time
import logging
from datetime import timedelta
import multiprocessing
import shutil

import config
from config import logger
#from src import applogger
from src import utils
from src import salome_utils
from src import foam_utils


def main():
    if not os.path.exists(config.LOG):
        os.makedirs(config.LOG)

    if not os.path.exists(config.BUILD):
        os.makedirs(config.BUILD)

    #global logger 
    #logger = applogger.Logger()

    check = checkEnv()

    if check:
        return

    tasks = createTasks()

    for task in tasks:
        logger.fancyline()
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


def checkEnv():
    missed = False
    
    try:
        pythonVersion = "Python {}".format(sys.version.split(" ")[0])
        salomeVersion = salome_utils.salomeVersion()
        foamVersion = foam_utils.foamVersion()

    except Exception:
        logger.critical("Missed environment")
        missed = True

    else:
        logger.info(f"environment:\n\t{pythonVersion}\n\t{salomeVersion}\n\t{foamVersion}")

    finally:
        return missed


class Task:
    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)


def createTasks():
    #Task = namedtuple("Task", ["structure", "theta", "fillet", "direction", "export"])
    tasks = []
    structures = [ getattr(config, s)() for s in config.structures ]

    for structure in structures:
        for direction in structure.directions:
            for theta in structure.theta:
                name = type(structure).__name__
                export = os.path.join(
                    config.BUILD, 
                    name,
                    "direction-{}{}{}".format(*direction),
                    "theta-{}".format(theta)
                )

                task = Task(
                    structure = name, 
                    theta = theta, 
                    fillet = structure.fillet, 
                    direction = direction, 
                    export = export,
                    mesh = False,
                    flow = False
                )

                tasks.append(task)

    return tasks


def createMesh(task):
    scriptpath = os.path.join(config.ROOT, "samples/__init__.py")
    port = 2810
    stime = time.monotonic()

    args = (
        task.structure, 
        task.theta, 
        int(task.fillet), 
        "".join([str(coord) for coord in task.direction]), 
        os.path.join(task.export, "mesh.unv"),
        config.ROOT
    )
    returncode = salome_utils.runExecute(port, scriptpath, *args)
    
    etime = time.monotonic()
    logger.info("createMesh: elapsed time: {}".format(timedelta(seconds = etime - stime)))


def calculate(task):
    foamCase = [ "0", "constant", "system" ]

    os.chdir(task.export)
    foam_utils.foamClean()

    for d in foamCase:
        shutil.copytree(
            os.path.join(config.ROOT, "src/cubicFoam", d), 
            os.path.join(task.export, d)
        )
    
    stime = time.monotonic()

    if not os.path.exists("mesh.unv"):
        logger.critical(f"calculate: missed 'mesh.unv'")
        return

    foam_utils.ideasUnvToFoam("mesh.unv")
    
    foam_utils.createPatch(dictfile = "system/createPatchDict.symetry")
    
    foam_utils.checkMesh()

    scale = (1e-5, 1e-5, 1e-5)
    foam_utils.transformPoints(scale)
    
    foam_utils.decomposePar()

    foam_utils.renumberMesh()
    
    foam_utils.potentialFoam()
    
    for n in range(os.cpu_count()):
        foam_utils.foamDictionary(f"processor{n}/0/U", "boundaryField.inlet.type", "pressureInletVelocity")
        foam_utils.foamDictionary(f"processor{n}/0/U", "boundaryField.inlet.value", "uniform (0 0 0)")
    
    returncode = foam_utils.simpleFoam()

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


