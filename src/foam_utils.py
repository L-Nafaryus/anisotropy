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


