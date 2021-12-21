# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from os import path
import logging

logger = logging.getLogger(__name__)

from anisotropy.openfoam.runnerPresets import postProcess
from anisotropy.openfoam import datReader


class PostProcess(object):
    def __init__(self, dirpath):
        self.path = path.abspath(dirpath)

    def flowRate(self, patch: str):
        func = "patchFlowRate(patch={})".format(patch)
        filepath = path.join(self.path, "postProcessing", func, "0", "surfaceFieldValue.dat")
        postProcess(func, cwd = self.path)
        surfaceFieldValue = datReader(filepath)

        return surfaceFieldValue["sum(phi)"][-1]

