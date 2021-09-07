# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import os
import shutil
from .application import application

def version() -> str:
    return os.environ["WM_PROJECT_VERSION"]


def foamCleanCustom(case: str = None):
    rmDirs = ["0", "constant", "system", "postProcessing", "logs"]
    rmDirs.extend([ "processor{}".format(n) for n in range(os.cpu_count()) ])
    path = case if case else ""

    for d in rmDirs:
        if os.path.exists(os.path.join(path, d)):
            shutil.rmtree(os.path.join(path, d))

def foamClean(case: str = None):
    rmDirs = ["0", "constant", "system"]
    path = case if case else ""

    for d in rmDirs:
        if os.path.exists(os.path.join(path, d)):
            shutil.rmtree(os.path.join(path, d))

    application("foamCleanTutorials", useMPI = False, case = case, stderr = True)

def uniform(value) -> str:
    if type(value) == list or type(value) == tuple:
        return f"uniform ({ value[0] } { value[1] } { value[2] })"

    elif type(value) == int or type(value) == float:
        return f"uniform { value }"

    else:
        return ""
