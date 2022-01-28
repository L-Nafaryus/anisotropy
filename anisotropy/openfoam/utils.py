# -*- coding: utf-8 -*-

from __future__ import annotations
from numpy.typing import ArrayLike
from numpy import ndarray

import os


def version() -> str | None:
    """Version of the current OpenFOAM installation.

    :return:
        Version string or None if installation is not found.
    """
    return os.environ.get("WM_PROJECT_VERSION")


def template(header: dict, content: dict) -> str:
    """Render FoamFile with current template.

    :param header:
        Header block with the FoamFile metadata.
    :param content:
        Content block of the FoamFile.
    :return:
        Generated string of the whole FoamFile.
    """
    limit = 78
    desc = [
        "/*--------------------------------*- C++ -*----------------------------------*\\",
        "| =========                 |                                                 |",
        "| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |",
        "|  \\\\    /   O peration     |",
        "|   \\\\  /    A nd           |                                                 |",
        "|    \\\\/     M anipulation  |                                                 |",
        "\\*---------------------------------------------------------------------------*/"
    ]
    desc[3] += " Version: {}".format(version() or "missed")
    desc[3] += " " * (limit - len(desc[3])) + "|"
    afterheader = "// " + 37 * "* " + "//"
    endfile = "// " + 73 * "*" + " //"

    return "\n".join([*desc, header, afterheader, content, endfile])


def uniform(value: ArrayLike | float | int) -> str:
    """Convert value to the OpenFOAM uniform representation.

    :param value:
        Vector or scalar value.
    :return:
        Uniform string representation.
    """
    if type(value) in [list, tuple, ndarray]:
        return f"uniform ({ value[0] } { value[1] } { value[2] })"

    elif type(value) in [int, float]:
        return f"uniform { value }"

    else:
        return ""
