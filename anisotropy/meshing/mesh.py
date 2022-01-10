# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from netgen.occ import OCCGeometry
from netgen import meshing
from numpy import array
import os

class Mesh(object):
    def __init__(self, shape):
        self.geometry = OCCGeometry(shape)
        self.mesh = None

        #   Parameters
        self.maxh = 0.2
        self.curvaturesafety = 5
        self.segmentsperedge = 3
        self.grading = 0.1
        self.chartdistfac = 5
        self.linelengthfac = 3
        self.closeedgefac = 5
        self.minedgelen = 2.0
        self.surfmeshcurvfac = 5.0
        self.optsteps2d = 5
        self.optsteps3d = 5


    @property
    def parameters(self):
        return meshing.MeshingParameters(
            maxh = self.maxh,
            curvaturesafety = self.curvaturesafety,
            segmentsperedge = self.segmentsperedge,
            grading = self.grading,
            chartdistfac = self.chartdistfac,
            linelengthfac = self.linelengthfac,
            closeedgefac = self.closeedgefac,
            minedgelen = self.minedgelen,
            surfmeshcurvfac = self.surfmeshcurvfac,
            optsteps2d = self.optsteps2d,
            optsteps3d = self.optsteps3d
        )

    def build(self):
        self.mesh = self.geometry.GenerateMesh(self.parameters)

    def export(self, filename: str):
        """Export a shape.
        
        Supported formats: vol, mesh.
        
        :param filename:
            Name of the file to store the given shape in.
        
        :return:
            Output, error messages and returncode
        """
        out, err, returncode = "", "", 0
        ext = os.path.splitext(filename)[1][1: ]
        
        try:
            if ext == "vol":
                self.mesh.Save(filename)
            
            elif ext == "mesh":
                self.mesh.Export(filename, "Neutral Format")

            else:
                raise NotImplementedError(f"Mesh format '{ ext }' is not supported")
            
        except NotImplementedError as e:
            err = e
            returncode = 1
        
        except Exception as e:
            err = e
            returncode = 1
        
        return out, err, returncode

    def doubleExport(self):
        pass

    @property
    def volumes(self) -> array:
        return array(self.mesh.Elements3D())

    @property
    def faces(self) -> array:
        return array(self.mesh.Elements2D())

    @property
    def edges(self) -> array:
        # NOTE: returns zero elements for imported mesh 
        return array(self.mesh.Elements1D())


# tetras = numpy.array([ [ [ vertex for vertex in mesh[index] ] for index in element.vertices ] for element in self.mesh.Elements3D() ])
# volumes = numpy.array([ 1 / 6 * linalg.det(numpy.append(tetra.transpose(), numpy.array([[1, 1, 1, 1]]), axis = 0)) for tetra in tetras ])
        
