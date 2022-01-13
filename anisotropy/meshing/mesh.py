# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from netgen.occ import OCCGeometry
from netgen import meshing
from numpy import array
import os


class NoGeometrySpecified(Exception):
    def __init__(self, msg):
        super().__init__(self, msg)


class NotSupportedMeshFormat(Exception):
    def __init__(self, msg):
        super().__init__(self, msg)

class Mesh(object):
    def __init__(self, shape: OCCGeometry = None):
        self.geometry = OCCGeometry(shape) if shape else None
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
        if self.geometry:
            self.mesh = self.geometry.GenerateMesh(self.parameters)

        else:
            raise NoGeometrySpecified("Specify a geometry to build a mesh")

    formats = {
        "vol": "Netgen Format",
        "mesh": "Neutral Format",
        "msh": "Gmsh2 Format"
    }

    def load(self, filename: str):
        """Import a mesh.
        
        Use `Mesh.formats` to see supported formats.
        
        :param filename:
            Name of the file to store the given mesh in.
        """
        ext = os.path.splitext(filename)[1][1: ]

        if ext in self.formats.keys():
            self.mesh = meshing.Mesh()
            self.mesh.Load(filename)

        else:
            raise NotSupportedMeshFormat(f"Mesh format '{ ext }' is not supported")
        
        return self

    def export(self, filename: str):
        """Export a mesh.
        
        Use `Mesh.formats` to see supported formats.
        
        :param filename:
            Name of the file to store the given mesh in.
        
        :return:
            Output, error messages and returncode
        """
        out, err, returncode = "", "", 0
        ext = os.path.splitext(filename)[1][1: ]
        
        try:
            if ext == "vol":
                self.mesh.Save(filename)
            
            elif ext in self.formats.keys():
                self.mesh.Export(filename, self.formats[ext])

            else:
                raise NotSupportedMeshFormat(f"Mesh format '{ ext }' is not supported")
            
        except (NotSupportedMeshFormat, Exception) as e:
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
        
