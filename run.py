import os, sys
from collections import namedtuple
import time
import logging
from datetime import timedelta
import multiprocessing
import shutil

ROOT = os.getcwd()
sys.path.append(ROOT)

LOG = os.path.join(ROOT, "logs")
BUILD = os.path.join(ROOT, "build")

from src import utils
from src import salome_utils
from src import foam_utils

def createTasks():
    ###
    #   Control variables
    ##
    structures = [
        "simple", 
        #"bodyCentered", 
        #"faceCentered"
    ]
    directions = [
        [1, 0, 0],
        [0, 0, 1],
        [1, 1, 1]
    ]
    fillet = 1

    ###
    #   Tasks
    ##
    Task = namedtuple("Task", ["structure", "coeff", "fillet", "direction", "saveto"])
    tasks = []

    for structure in structures:
        if structure == "simple":
            theta = [c * 0.01 for c in range(1, 28 + 1)]
            #theta = [ 0.01, 0.28 ]

        elif structure == "faceCentered":
            #theta = [c * 0.01 for c in range(1, 13 + 1)]
            theta = [ 0.01, 0.13 ]

        elif structure == "bodyCentered":
            #theta = [c * 0.01 for c in range(1, 18 + 1)]
            theta = [ 0.01, 0.13, 0.14, 0.18 ]

        for coeff in theta:
            for direction in directions:
                saveto = os.path.join(BUILD, structure, "coeff-{}".format(coeff),
                    "direction-{}{}{}".format(direction[0], direction[1], direction[2]))

                if not os.path.exists(saveto):
                    os.makedirs(saveto)
                
                t = Task(structure, coeff, fillet, direction, saveto)
                tasks.append(t)

    return tasks


def createMesh(tasks):
    scriptpath = os.path.join(ROOT, "samples/__init__.py")
    port = 2810
    errors = 0

    for task in tasks:
        logging.info("-" * 80)
        logging.info("""createMesh:
        task:\t{} / {}""".format(tasks.index(task) + 1, len(tasks)))
        start_time = time.monotonic()

        returncode = salome_utils.runExecute(port, scriptpath, task.structure, task.coeff, task.fillet, "".join([str(coord) for coord in task.direction]), os.path.join(task.saveto, "mesh.unv"))
        
        end_time = time.monotonic()
        logging.info("createMesh: elapsed time: {}".format(timedelta(seconds=end_time - start_time)))
        logging.info("salome: return code:\t{}".format(returncode))

        if returncode == 1:
            #break
            errors += 1
            pass

    return errors
    

def calculate(tasks):
    foamCase = [ "0", "constant", "system" ]
    rmDirs = ["0", "constant", "system", "postProcessing", "logs"] + [ "processor{}".format(n) for n in range(4)]
    #fancyline = "--------------------------------------------------------------------------------"

    for task in tasks:
        
        for d in rmDirs:
            if os.path.exists(os.path.join(task.saveto, d)):
                shutil.rmtree(os.path.join(task.saveto, d))

        for d in foamCase:
            if not os.path.exists(os.path.join(task.saveto, d)):
                shutil.copytree(os.path.join(ROOT, "src/cubicFoam", d), 
                    os.path.join(task.saveto, d))
    
        os.chdir(task.saveto)
        casepath = "."
        
        logging.info("-" * 80)
        logging.info("""calculate: 
        task:\t{} / {}
        structure type:\t{}
        coefficient:\t{}
        flow direction:\t{}
        path:\t{}\n""".format(tasks.index(task) + 1, len(tasks) , task.structure, task.coeff, task.direction, task.saveto))

        foam_utils.ideasUnvToFoam(casepath, "mesh.unv")
        
        #if not task.direction == [1, 1, 1]:
        shutil.copy(os.path.join(task.saveto, "system/createPatchDict.symetry"),
            os.path.join(task.saveto, "system/createPatchDict"))
        logging.info("""createPatch:
        file:\tcreatePatchDict.symetry""")

        #else:
        #    shutil.copy(os.path.join(task.saveto, "system/createPatchDict.cyclic"),
        #        os.path.join(task.saveto, "system/createPatchDict"))
        #    logging.info("""createPatch:
        #    file:\tcreatePatchDict.cyclic""")

        foam_utils.createPatch(casepath)
        
        foam_utils.checkMesh(casepath)

        scale = (1e-5, 1e-5, 1e-5)
        foam_utils.transformPoints(casepath, "{}".format(scale).replace(",", ""))
        logging.info("""transformPoints:
        scale:\t{}""".format(scale))
        
        foam_utils.decomposePar(casepath)
        
        foam_utils.potentialFoam(casepath)
        
        for n in range(4):
            foam_utils.foamDictionarySet(casepath, "processor{}/0/U".format(n), 
                "boundaryField.inlet.type", "pressureInletVelocity")
            foam_utils.foamDictionarySet(casepath, "processor{}/0/U".format(n), 
                "boundaryField.inlet.value", "uniform (0 0 0)")
        
        foam_utils.simpleFoam(casepath)

        os.chdir(ROOT)

        #logging.info(fancyline)
    

def postprocessing(tasks):
    
    surfaceFieldValue = []
    dat = [ line.strip().split() for line in open("surfaceFieldValue.dat", "r").readlines() ]


if __name__ == "__main__":
    
    if not os.path.exists(LOG):
        os.makedirs(LOG)

    if not os.path.exists(BUILD):
        os.makedirs(BUILD)

    logging.basicConfig(
        level=logging.INFO, 
        format="%(levelname)s: %(message)s",
        handlers = [
            logging.StreamHandler(),
            logging.FileHandler("{}/cubic.log".format(LOG))
        ])
    
    # TODO: add force arg
    Args = namedtuple("Args", ["mesh", "calc"])

    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == "mesh":
            args = Args(True, False)

        elif action == "calc":
            args = Args(False, True)

        elif action == "all":
            args = Args(True, True)

    else:
        args = Args(True, True)

    tasks = createTasks()    
    logging.info("Tasks: {}".format(len(tasks)))
    
    if args.mesh:
        start_time = time.monotonic()
        #logging.info("Started at {}".format(timedelta(seconds=start_time)))

        errors = createMesh(tasks)
        
        end_time = time.monotonic()
        logging.info("-" * 80)
        logging.info("Elapsed time:\t{}".format(timedelta(seconds=end_time - start_time)))
        logging.info("Errors:\t{}".format(errors))
    
    if args.calc:
        start_time = time.monotonic()
        #logging.info("Started at {}".format(timedelta(seconds=start_time)))

        calculate(tasks)
        
        end_time = time.monotonic()
        logging.info("-" * 80)
        logging.info("Elapsed time: {}".format(timedelta(seconds=end_time - start_time)))
         
    

