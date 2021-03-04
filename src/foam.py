#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, shutil
import subprocess
import logging
import time
from datetime import timedelta

def application(name, case, log=False, args=[], parallel=False):
    logging.info("Running '{}'.".format(name))

    if log:
        logfile = open("{}/{}.log".format(case, name), "a")
    
    mpirun = []
    if parallel:
        mpirun = ["mpirun", "-np", "4", "--oversubscribe"]

    subprocess.run(mpirun + [name, "-case", case] + args, 
        stdout=logfile if log else subprocess.STDOUT,
        stderr=logfile if log else subprocess.STDOUT)

    if log:
        logfile.close()

def ideasUnvToFoam(case, mesh):
    application("ideasUnvToFoam", case, True, [mesh])

def transformPoints(case, vector):
    application("transformPoints", case, True, ["-scale", vector])

def checkMesh(case):
    application("checkMesh", case, True, ["-allGeometry", "-allTopology"])

def foamDictionaryGet(case, foamFile, entry):
    application("foamDictionary", case, True, [foamFile, "-entry", entry])

def foamDictionarySet(case, foamFile, entry, value):
    application("foamDictionary", case, True, [foamFile, "-entry", entry, "-set", value])

def decomposePar(case):
    application("decomposePar", case, True)

def potentialFoam(case):
    application("potentialFoam", case, True, ["-parallel"], True)

def simpleFoam(case):
    application("simpleFoam", case, True, ["-parallel"], True)

if __name__ == "__main__":
    # Get main paths
    project = os.getcwd()
    src = os.path.join(project, "src")
    build = os.path.join(project, "build")
    
    if not os.path.exists(build):
        os.makedirs(build) 

    # Logger
    logging.basicConfig(
        level=logging.INFO, 
        format="%(levelname)s: %(message)s",
        handlers = [
            logging.StreamHandler(),
            logging.FileHandler("{}/foam.log".format(build))
        ])
    start_time = time.monotonic()
    
    # Main entry
    structures = ["simpleCubic"] #, "bc-cubic", "fc-cubic"]
    directions = ["001", "100"]
    coefficients = [ alpha * 0.01 for alpha in range(1, 13 + 1) ]

    for structure in structures:
        for direction in directions:
            for coefficient in coefficients:
                foamCase = [ "0", "constant", "system" ]
                src_path = os.path.join(src, "baseFOAM")
                build_path = os.path.join(build, 
                    structure, 
                    "direction-{}".format(direction), 
                    "alpha-{}".format(coefficient))
                
                
                logging.info("Entry with parameters: {}, direction = {}, alpha = {}".format(structure, direction, coefficient))

                logging.info("Copying baseFOAM case ...")
                for d in foamCase:
                    if not os.path.exists(os.path.join(build_path, d)):
                        shutil.copytree(os.path.join(src_path, d), 
                            os.path.join(build_path, d))
                
                os.chdir(build_path)
                case_path = "."

                logging.info("Importing mesh to foam ...")
                ideasUnvToFoam(case_path, "{}-{}-{}.unv".format(structure, direction, coefficient))
                
                logging.info("Scaling mesh ...")
                transformPoints(case_path, "(1e-5 1e-5 1e-5)")
                
                logging.info("Checking mesh ...")
                checkMesh(case_path)
                
                logging.info("Changing mesh boundaries types ...")
                foamDictionarySet(case_path, "constant/polyMesh/boundary", "entry0.wall.type", "wall")
                foamDictionarySet(case_path, "constant/polyMesh/boundary", "entry0.symetryPlane.type", "symetryPlane")

                logging.info("Decomposing case ...")
                decomposePar(case_path)
                
                logging.info("Evaluating initial approximation via potentialFoam ...")
                potentialFoam(case_path)
                
                logging.info("Preparing boundaryFields for simpleFoam ...")
                for n in range(4):
                    foamDictionarySet(case_path, "processor{}/0/U".format(n), 
                        "boundaryField.inlet.type", "pressureInletVelocity")
                    foamDictionarySet(case_path, "processor{}/0/U", 
                        "boundaryField.inlet.value", "uniform (0 0 0)")
                
                logging.info("Calculating ...")
                simpleFoam(case_path)

                os.chdir(project)

    end_time = time.monotonic()
    logging.info("Elapsed time: {}".format(timedelta(seconds=end_time - start_time)))

