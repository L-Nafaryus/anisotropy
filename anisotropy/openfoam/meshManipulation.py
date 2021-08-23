from .application import application

import re

def createPatch(dictfile: str = None, case: str = None):
    args = ["-overwrite"]

    if dictfile:
        args.extend(["-dict", dictfile])

    application("createPatch", *args, case = case, stderr = True)


def transformPoints(scale, case: str = None):
    _scale = f"({ scale[0] } { scale[1] } { scale[2] })"

    application("transformPoints", "-scale", _scale, case = case, stderr = True)


def checkMesh(case: str = None) -> str:
    application("checkMesh", "-allGeometry", "-allTopology", case = case, stderr = True)
    out = ""

    with open("checkMesh.log", "r") as io:
        warnings = []
        for line in io:
            if re.search("\*\*\*", line):
                warnings.append(line.replace("***", "").strip())

        if warnings:
            out = "checkMesh:\n\t{}".format("\n\t".join(warnings))

    return out


def renumberMesh(case: str = None):
    application("renumberMesh", "-overwrite", useMPI = False, case = case, stderr = True)

