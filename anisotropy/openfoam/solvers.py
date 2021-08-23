# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from .application import application

import re 

def potentialFoam(case: str = None, useMPI: bool = False):
    if useMPI:
        application("potentialFoam", "-parallel", useMPI = True, case = case, stderr = True)

    else:
        application("potentialFoam", case = case, stderr = True)


def simpleFoam(case: str = None, useMPI: bool = False):
    if useMPI:
        out, err, returncode = application("simpleFoam", "-parallel", useMPI = True, case = case, stderr = True)

    else:
        out, err, returncode = application("simpleFoam", case = case, stderr = True)

    out = ""

    with open("simpleFoam.log", "r") as io:
        for line in io:
            if re.search("solution converged", line):
                out = "simpleFoam:\n\t{}".format(line.strip())

    return out, err, returncode 

