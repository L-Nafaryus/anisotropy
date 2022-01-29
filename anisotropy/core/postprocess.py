# -*- coding: utf-8 -*-

from os import path
import logging

logger = logging.getLogger(__name__)

from anisotropy.openfoam import commands 
from anisotropy.openfoam import conversion


class PostProcess(object):
    def __init__(self, dirpath):
        self.path = path.abspath(dirpath)

    def flowRate(self, patch: str):
        func = "patchFlowRate(patch={})".format(patch)
        filepath = path.join(self.path, "postProcessing", func, "0", "surfaceFieldValue.dat")
        commands.postProcess(func, cwd = self.path, logpath = path.join(self.path, "patchFlowRate.log"))
        surfaceFieldValue = conversion.datReader(filepath)

        return surfaceFieldValue["sum(phi)"][-1]
