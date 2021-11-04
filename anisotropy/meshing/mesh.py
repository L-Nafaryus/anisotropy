# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from netgen.occ import OCCGeometry
from netgen import meshing
import numpy

class Mesh(object):
    def __init__(self, shape):
        self.geometry = OCCGeometry(shape)
        self.mesh = None

    @property
    def parameters(self):
        return meshing.MeshingParameters(
            maxh = 0.2,
            curvaturesafety = 5,
            segmentsperedge = 3,
            grading = 0.1,
            chartdistfac = 5,
            linelengthfac = 3,
            closeedgefac = 5,
            minedgelen = 2.0,
            surfmeshcurvfac = 5.0,
            optsteps2d = 5,
            optsteps3d = 5
        )

    def build(self):
        self.mesh = self.geometry.GenerateMesh(self.parameters)

    def doubleExport(self):
        pass

    def volumes(self) -> numpy.array:
        #   TODO: check each polyhedron
        tetras = numpy.array([ [ [ vertex for vertex in mesh[index] ] for index in element.vertices ] for element in mesh.Elements3D() ])
        volumes = numpy.array([ 1 / 6 * linalg.det(numpy.append(tetra.transpose(), numpy.array([[1, 1, 1, 1]]), axis = 0)) for tetra in tetras ])
        
        return volumes
