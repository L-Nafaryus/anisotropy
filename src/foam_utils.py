import os, sys, shutil
import subprocess
import logging
import time
from datetime import timedelta

def application(name, case, log=False, args=[], parallel=False):
    

    #if log:
    #    logfile = open("{}/{}.log".format(case, name), "a")
    
    mpirun = []
    if parallel:
        mpirun = ["mpirun", "-np", "4", "--oversubscribe"]
    
    cmd = mpirun + [name, "-case", case] + args
    logging.info("Running '{}'".format(" ".join(cmd)))
   
    with subprocess.Popen(cmd, 
        #shell = True,
        stdout = subprocess.PIPE, 
        stderr = subprocess.PIPE) as p, \
        open("{}/{}.log".format(case, name), "wb") as logfile:
        
        for line in p.stdout:
            #sys.stdout.buffer.write(line) 
            logfile.write(line)

        #for line in p.stderr:
        #    logfile.write(line)

        out, err = p.communicate()

        if err:
            logging.error("""{}:
            {}""".format(name, str(err, "utf-8")))

    return p.returncode


def ideasUnvToFoam(case, mesh):
    application("ideasUnvToFoam", case, True, [mesh])

def createPatch(case):
    application("createPatch", case, True, ["-overwrite"])

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


