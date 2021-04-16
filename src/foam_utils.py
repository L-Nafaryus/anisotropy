import os, sys, shutil
import subprocess
import logging
import time
import re
from datetime import timedelta
from config import logger

def application(name: str, *args: str, case: str = None, stderr: bool = True, useMPI: bool = False) -> int:
    
    cmd = []

    if useMPI:
        nprocs = os.cpu_count()
        cmd.extend(["mpirun", "-np", str(nprocs), "--oversubscribe"])
    
    cmd.append(name)

    if case:
        cmd.extend(["-case", case])

    if args:
        cmd.extend([*args])
        
    logger.info("{}: {}".format(name, [*args]))
    logpath = os.path.join(case if case else "", "{}.log".format(name))
   
    with subprocess.Popen(cmd, 
        stdout = subprocess.PIPE, 
        stderr = subprocess.PIPE) as p, \
        open(logpath, "wb") as logfile:
        
        for line in p.stdout:
            #sys.stdout.buffer.write(line) 
            logfile.write(line)

        #for line in p.stderr:
        #    logfile.write(line)

        out, err = p.communicate()
        logfile.write(err)

        if err and stderr:
            logger.error("""{}:
            {}""".format(name, str(err, "utf-8")))

    return out, p.returncode


def foamVersion() -> str:
    return "OpenFOAM-{}".format(os.environ["WM_PROJECT_VERSION"])


def foamClean(case: str = None):
    rmDirs = ["0", "constant", "system", "postProcessing", "logs"]
    rmDirs.extend([ "processor{}".format(n) for n in range(os.cpu_count()) ])
    path = case if case else ""

    for d in rmDirs:
        if os.path.exists(os.path.join(path, d)):
            shutil.rmtree(os.path.join(path, d))


def ideasUnvToFoam(mesh: str, case: str = None):
    application("ideasUnvToFoam", mesh, case = case, stderr = True)


def createPatch(dictfile: str = None, case: str = None):
    args = ["-overwrite"]

    if dictfile:
        args.extend(["-dict", dictfile])

    application("createPatch", *args, case = case, stderr = True)


def transformPoints(scale: tuple, case: str = None):
    scale_ = "{}".format(scale).replace(",", "")

    application("transformPoints", "-scale", scale_, case = case, stderr = True)


def checkMesh(case: str = None):
    application("checkMesh", "-allGeometry", "-allTopology", case = case, stderr = True)

    with open("checkMesh.log", "r") as io:
        warnings = []
        for line in io:
            if re.search("\*\*\*", line):
                warnings.append(line.replace("***", "").strip())

        if warnings:
            logger.warning("checkMesh:\n\t{}".format("\n\t".join(warnings)))

def foamDictionary(filepath: str, entry: str, value: str = None, case: str = None):
    args = [filepath, "-entry", entry]

    if value:
        args.extend(["-set", value])

    application("foamDictionary", *args, case = case, stderr = False)


def decomposePar(case: str = None):
    application("decomposePar", case = case, stderr = True)


def renumberMesh(case: str = None):
    application("renumberMesh", "-parallel", "-overwrite", useMPI = True, case = case, stderr = True)


def potentialFoam(case: str = None):
    application("potentialFoam", "-parallel", useMPI = True, case = case, stderr = True)


def simpleFoam(case: str = None):
    _, returncode = application("simpleFoam", "-parallel", useMPI = True, case = case, stderr = True)

    with open("simpleFoam.log", "r") as io:
        for line in io:
            if re.search("solution converged", line):
                logger.info("simpleFoam:\n\t{}".format(line.strip()))

    return returncode


