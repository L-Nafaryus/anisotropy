# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from datetime import datetime

import anisotropy.samples as samples

class UltimateRunner(object):
    def __init__(self):
        
        self.database = Database(..)
        self.datebase.setup()

        self._exec = Execution(date = datetime.now())
        self._exec.save()

    def computeMesh(self):
        pass

    def _computeMesh(self):
        """Function for Salome"""
        
        sample = samples.__dict__[..]

        #   Build a shape
        shape = sample.geometry(..)
        shape.build()
        shape.export(..)

        #   Build a mesh
        mesh = sample.mesh(shape)
        mesh.build()
        mesh.export(..)

        #   Fill database

        
    def computeFlow(self):

        sample = samples.__dict__[..]

        #   Build a flow
        flow = sample.onephaseflow(..)
        flow.build()

