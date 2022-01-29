# -*- coding: utf-8 -*-

from . import FoamRunner


###
#   meshConversion
##

def netgenNeutralToFoam(meshfile: str, run: bool = True, **kwargs) -> FoamRunner:
    command = "netgenNeutralToFoam"
    kwargs.update(logpath = kwargs.get("logpath", f"{ command }.log"))
    kwargs.update(exit = True)
    args = [ meshfile ]

    runner = FoamRunner(command, args = args, **kwargs)

    if run:
        runner.run()

    return runner


def ideasUnvToFoam(meshfile: str, run: bool = True, **kwargs) -> FoamRunner:
    command = "ideasUnvToFoam"
    kwargs.update(logpath = kwargs.get("logpath", f"{ command }.log"))
    kwargs.update(exit = True)
    args = [ meshfile ]

    runner = FoamRunner(command, args = args, **kwargs)

    if run:
        runner.run()

    return runner


###
#   meshManipulation
##

def createPatch(dictfile: str = None, overwrite: bool = True, run: bool = True, **kwargs) -> FoamRunner:
    command = "createPatch"
    kwargs.update(logpath = kwargs.get("logpath", f"{ command }.log"))
    kwargs.update(exit = True)
    args = []

    if dictfile:
        args.extend(["-dict", dictfile])

    if overwrite:
        args.append("-overwrite")

    runner = FoamRunner(command, args = args, **kwargs)

    if run:
        runner.run()

    return runner


def transformPoints(transformations: dict, run: bool = True, **kwargs) -> FoamRunner:
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

    runner = FoamRunner(command, args = args, **kwargs)

    if run:
        runner.run()

    return runner


def checkMesh(allGeometry: bool = True, allTopology: bool = True, run: bool = True, **kwargs) -> FoamRunner:
    command = "checkMesh"
    kwargs.update(logpath = kwargs.get("logpath", f"{ command }.log"))
    kwargs.update(exit = True)
    args = []

    if allGeometry:
        args.append("-allGeometry")

    if allTopology:
        args.append("-allTopology")

    runner = FoamRunner(command, args = args, **kwargs)

    if run:
        runner.run()

    return runner


def renumberMesh(overwrite: bool = True, run: bool = True, **kwargs) -> FoamRunner:
    command = "renumberMesh"
    kwargs.update(logpath = kwargs.get("logpath", f"{ command }.log"))
    kwargs.update(exit = True)
    args = []

    if overwrite:
        args.append("-overwrite")

    runner = FoamRunner(command, args = args, **kwargs)

    if run:
        runner.run()

    return runner


###
#   miscellaneous
##

# def foamDictionary()


###
#   parallelProcessing
##

def decomposePar(run: bool = True, **kwargs) -> FoamRunner:
    command = "decomposePar"
    kwargs.update(logpath = kwargs.get("logpath", f"{command}.log"))
    kwargs.update(exit = True)
    args = []

    runner = FoamRunner(command, args = args, **kwargs)

    if run:
        runner.run()

    return runner


###
#   solvers
##

def potentialFoam(parallel: bool = False, run: bool = True, **kwargs) -> FoamRunner:
    command = "potentialFoam"
    kwargs.update(logpath = kwargs.get("logpath", f"{command}.log"))
    kwargs.update(exit = True)
    args = []

    if parallel:
        args.append("-parallel")
        kwargs.update(mpi = True)

    runner = FoamRunner(command, args = args, **kwargs)

    if run:
        runner.run()

    return runner


def simpleFoam(parallel: bool = False, run: bool = True, **kwargs) -> FoamRunner:
    command = "simpleFoam"
    kwargs.update(logpath = kwargs.get("logpath", f"{command}.log"))
    kwargs.update(exit = True)
    args = []

    if parallel:
        args.append("-parallel")
        kwargs.update(mpi = True)

    runner = FoamRunner(command, args = args, **kwargs)

    if run:
        runner.run()

    return runner


###
#   postProcessing
##

def postProcess(func: str = None, latestTime: bool = False, run: bool = True, **kwargs) -> FoamRunner:
    command = "postProcess"
    kwargs.update(logpath=kwargs.get("logpath", f"{command}.log"))
    kwargs.update(exit = True)
    args = []

    if func:
        args.extend(["-func", func])

    if latestTime:
        args.append("-latestTime")

    runner = FoamRunner(command, args = args, **kwargs)

    if run:
        runner.run()

    return runner
