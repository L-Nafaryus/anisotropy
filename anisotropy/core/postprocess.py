# -*- coding: utf-8 -*-

import pathlib

import anisotropy.openfoam as of


def flowRate(patch: str, path: str = None):
    func = f"patchFlowRate(patch={ patch })"

    path = pathlib.Path(path or "").resolve()
    outfile = path / "postProcessing" / func / "0/surfaceFieldValue.dat"

    of.commands.postProcess(func, cwd = path, logpath = path / "patchFlowRate.log")
    surfaceFieldValue = of.conversion.read_dat(outfile)["sum(phi)"][-1]

    return surfaceFieldValue
