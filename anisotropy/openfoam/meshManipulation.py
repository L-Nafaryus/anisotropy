# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

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
    _, err, returncode = application("checkMesh", "-allGeometry", "-allTopology", case = case, stderr = True)
    out = ""

    with open("checkMesh.log", "r") as io:
        warnings = []
        for line in io:
            if re.search(r"***", line):
                warnings.append(line.replace("***", "").strip())

        if warnings:
            out = "checkMesh:\n\t{}".format("\n\t".join(warnings))

    return out, err, returncode


def renumberMesh(case: str = None):
    application("renumberMesh", "-overwrite", useMPI = False, case = case, stderr = True)

