# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from netgen.occ import OCCGeometry
from netgen import meshing
import numpy
from numpy import array, ndarray, linalg
import os
from .utils import extractNetgenPoints, extractNetgenCells
from . import metrics
import meshio


class NoGeometrySpecified(Exception):
    def __init__(self, msg):
        super().__init__(self, msg)


class NotSupportedMeshFormat(Exception):
    def __init__(self, msg):
        super().__init__(self, msg)


class MeshingParameters(object):
    def __init__(self, **kwargs):
        self.preset(2, **kwargs)
       
    def preset(self, key: int, **kwargs):
        """Apply predefined parameters.

        :param key:
            0: very_coarse
            1: coarse
            2: moderate
            3: fine
            4: very_fine
        """
        self.maxh =             kwargs.get("maxh", 0.2)
        self.curvaturesafety =  kwargs.get("curvaturesafety", [1, 1.5, 2, 3, 5][key])
        self.segmentsperedge =  kwargs.get("segmentsperedge", [0.3, 0.5, 1, 2, 3][key])
        self.grading =          kwargs.get("grading", [0.7, 0.5, 0.3, 0.2, 0.1][key])
        self.chartdistfac =     kwargs.get("chartdistfac", [0.8, 1, 1.5, 2, 5][key])
        self.linelengthfac =    kwargs.get("linelengthfac", [0.2, 0.35, 0.5, 1.5, 3][key])
        self.closeedgefac =     kwargs.get("closeedgefac", [0.5, 1, 2, 3.5, 5][key])
        self.minedgelen =       kwargs.get("minedgelen", [0.002, 0.02, 0.2, 1.0, 2.0][key])
        self.surfmeshcurvfac =  kwargs.get("surfmeshcurvfac", [1, 1.5, 2, 3, 5.0][key])
        self.optsteps2d =       kwargs.get("optsteps2d", 5)
        self.optsteps3d =       kwargs.get("optsetps3d", 5)

        return self

    def get(self) -> meshing.MeshingParameters:
        return meshing.MeshingParameters(**self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)


class Mesh(object):
    def __init__(self, shape = None):
        self.shape = shape
        self.mesh = None

        self.points = []
        self.cells = []
        self.boundary = []

    @property
    def geometry(self):
        return OCCGeometry(self.shape)

    def generate(self, parameters: MeshingParameters = None, refineSteps: int = 0, scale: float = 0):
        if not self.geometry:
            raise NoGeometrySpecified("Cannot build mesh without geometry")
    
        parameters = parameters or MeshingParameters()
        mesh = self.geometry.GenerateMesh(parameters.get())

        if refineSteps > 0:
            for n in range(refineSteps):
                mesh.Refine()
            
            mesh.OptimizeMesh2d(parameters)
            mesh.OptimizeVolumeMesh(parameters)
        
        if scale > 0:
            mesh.Scale(scale)
        
        self.points = extractNetgenPoints(mesh)
        self.cells = []

        for dim in range(4):
            self.cells.extend(extractNetgenCells(dim, mesh))

        return self


    def read(self, filename: str):
        """Import a mesh.
        
        :param filename:
            Name of the mesh file.
        """
        mesh = meshio.read(filename)

        self.points = mesh.points
        self.cells = mesh.cells
        
        return self

    def write(self, filename: str):
        """Export a mesh.
        
        :param filename:
            Name of the file to store the given mesh in.
        """
        mesh = meshio.Mesh(self.points, self.cells)
        mesh.write(filename)


    @property
    def volumes(self) -> list[ndarray]:
        points = []

        for cellBlock in self.cells:
            if cellBlock.dim == 3:
                points.extend([ *self.points[cellBlock.data] ])

        return points

    @property
    def volume(self) -> float:
        """Volume of whole mesh.
        
        :return:
            Volume.
        """
        return sum([ metrics.volume(cell) for cell in self.volumes ]) 

    @property
    def faces(self) -> list[ndarray]:
        points = []

        for cellBlock in self.cells:
            if cellBlock.dim == 2:
                points.extend([ *self.points[cellBlock.data] ]) 

        return points 

