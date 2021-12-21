# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import os
import shutil
from numpy import ndarray
#from .application import application

def version() -> str:
    return os.environ.get("WM_PROJECT_VERSION")


def foamCleanCustom(case: str = None):
    rmDirs = ["0", "constant", "system", "postProcessing", "logs"]
    rmDirs.extend([ "processor{}".format(n) for n in range(os.cpu_count()) ])
    path = case if case else ""

    for d in rmDirs:
        if os.path.exists(os.path.join(path, d)):
            shutil.rmtree(os.path.join(path, d))

#def foamClean(case: str = None):
#    rmDirs = ["0", "constant", "system"]
#    path = case if case else ""
#
#    for d in rmDirs:
#        if os.path.exists(os.path.join(path, d)):
#            shutil.rmtree(os.path.join(path, d))
#
#    application("foamCleanTutorials", useMPI = False, case = case, stderr = True)

def uniform(value) -> str:
    if type(value) == list or type(value) == tuple or type(value) == ndarray:
        return f"uniform ({ value[0] } { value[1] } { value[2] })"

    elif type(value) == int or type(value) == float:
        return f"uniform { value }"

    else:
        return ""

def datReader(filename: str):
    header = []
    content = []

    with open(filename, "r") as io:
        for line in io.readlines():
            if line.startswith("#"):
                header.append(line)

            else:
                content.append(line)

    columns = []

    if header[-1].find(":") < 0:
        for column in header[-1].replace("#", "").split("\t"):
            columns.append(column.strip())

        header.pop(-1)

    else:
        for column in range(len(content[0].split("\t"))):
            columns.append(str(column))

    output = {}

    for row in header:
        key, value = row.replace("#", "").split(":")

        try:
            value = float(value.strip())

        except:
            value = value.strip()

        output[key.strip()] = value

    for column in columns:
        output[column] = []

    for row in content:
        values = row.split("\t")

        for column, value in zip(columns, values):
            output[column].append(float(value))

    return output