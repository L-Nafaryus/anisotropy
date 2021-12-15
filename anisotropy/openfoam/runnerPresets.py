# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from typing import List
from .runner import FoamRunner

###
#   meshConversion
##

def netgenNeutralToFoam(meshfile: str, **kwargs) -> tuple[str, str, int]:
    command = "netgenNeutralToFoam"
    kwargs.update(logpath = kwargs.get("logpath", f"{ command }.log"))
    kwargs.update(exit = True)
    args = [ meshfile ]

    return FoamRunner(command, args = args, **kwargs).run()


def ideasUnvToFoam(meshfile: str, **kwargs) -> tuple[str, str, int]:
    command = "ideasUnvToFoam"
    kwargs.update(logpath = kwargs.get("logpath", f"{ command }.log"))
    kwargs.update(exit = True)
    args = [ meshfile ]

    return FoamRunner(command, args = args, **kwargs).run()


###
#   meshManipulation
##

def createPatch(dictfile: str = None, overwrite: bool = True, **kwargs) -> tuple[str, str, int]:
    command = "createPatch"
    kwargs.update(logpath = kwargs.get("logpath", f"{ command }.log"))
    kwargs.update(exit = True)
    args = []

    if dictfile:
        args.extend(["-dict", dictfile])

    if overwrite:
        args.append("-overwrite")

    return FoamRunner(command, args = args, **kwargs).run()


def transformPoints(transformations: dict, **kwargs) -> tuple[str, str, int]:
    command = "transformPoints"
    kwargs.update(logpath = kwargs.get("logpath", f"{ command }.log"))
    kwargs.update(exit = True)
    args = []
    arg = []

    for k, v in transformations.items():
        if type(v) == int or type(v) == float:
            value = str(v)

        elif type(v) == tuple or type(v) == list:
            value = "({} {} {})".format(*v)

        arg.append("{}={}".format(k, value))

    args.append(", ".join(arg))

    return FoamRunner(command, args = args, **kwargs).run()


def checkMesh(allGeometry: bool = True, allTopology: bool = True, **kwargs) -> tuple[str, str, int]:
    command = "checkMesh"
    kwargs.update(logpath = kwargs.get("logpath", f"{ command }.log"))
    kwargs.update(exit = True)
    args = []

    if allGeometry:
        args.append("-allGeometry")

    if allTopology:
        args.append("-allTopology")

    return FoamRunner(command, args = args, **kwargs).run()


def renumberMesh(overwrite: bool = True, **kwargs) -> tuple[str, str, int]:
    command = "renumberMesh"
    kwargs.update(logpath = kwargs.get("logpath", f"{ command }.log"))
    kwargs.update(exit = True)
    args = []

    if overwrite:
        args.append("-overwrite")

    return FoamRunner(command, args = args, **kwargs).run()


###
#   miscellaneous
##

# def foamDictionary()


###
#   parallelProcessing
##

def decomposePar(**kwargs) -> tuple[str, str, int]:
    command = "decomposePar"
    kwargs.update(logpath = kwargs.get("logpath", f"{command}.log"))
    kwargs.update(exit = True)
    args = []

    return FoamRunner(command, args = args, **kwargs).run()


###
#   solvers
##

def potentialFoam(parallel: bool = False, **kwargs) -> tuple[str, str, int]:
    command = "potentialFoam"
    kwargs.update(logpath = kwargs.get("logpath", f"{command}.log"))
    kwargs.update(exit = True)
    args = []

    if parallel:
        args.append("-parallel")
        kwargs.update(mpi = True)

    return FoamRunner(command, args = args, **kwargs).run()


def simpleFoam(parallel: bool = False, **kwargs) -> tuple[str, str, int]:
    command = "simpleFoam"
    kwargs.update(logpath = kwargs.get("logpath", f"{command}.log"))
    kwargs.update(exit = True)
    args = []

    if parallel:
        args.append("-parallel")
        kwargs.update(mpi = True)

    return FoamRunner(command, args = args, **kwargs).run()
