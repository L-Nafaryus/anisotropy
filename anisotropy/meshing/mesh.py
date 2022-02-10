# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from __future__ import annotations
from numpy import ndarray
from os import PathLike

import numpy as np
import netgen.occ as ng_occ
import netgen.meshing as ng_meshing
import meshio
import pathlib

from . import utils
from . import metrics
from . import conversion


class NoGeometrySpecified(Exception):
    pass


class NotSupportedMeshFormat(Exception):
    """Exception for not supported mesh format IO operations.
    """
    pass


class MeshingParameters:
    def __init__(self, **kwargs):
        """A MeshingParameters object contains parameters for netgen mesher.
        """
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
        self.__dict__.update(kwargs)
        
        self.maxh = kwargs.get("maxh", 0.2)
        self.curvaturesafety = kwargs.get("curvaturesafety", [1, 1.5, 2, 3, 5][key])
        self.segmentsperedge = kwargs.get("segmentsperedge", [0.3, 0.5, 1, 2, 3][key])
        self.grading = kwargs.get("grading", [0.7, 0.5, 0.3, 0.2, 0.1][key])
        self.chartdistfac = kwargs.get("chartdistfac", [0.8, 1, 1.5, 2, 5][key])
        self.linelengthfac = kwargs.get("linelengthfac", [0.2, 0.35, 0.5, 1.5, 3][key])
        self.closeedgefac = kwargs.get("closeedgefac", [0.5, 1, 2, 3.5, 5][key])
        self.minedgelen = kwargs.get("minedgelen", [0.002, 0.02, 0.2, 1.0, 2.0][key])
        self.surfmeshcurvfac = kwargs.get("surfmeshcurvfac", [1, 1.5, 2, 3, 5.0][key])
        self.optsteps2d = kwargs.get("optsteps2d", 5)
        self.optsteps3d = kwargs.get("optsetps3d", 5)

        return self

    def get(self) -> ng_meshing.MeshingParameters:
        return ng_meshing.MeshingParameters(**self.__dict__)
    
    def __repr__(self):
        items = [ f"{ key }: { val }" for key, val in self.__dict__.items() ]

        return "<MeshingParameters, " + ", ".join(items) + ">"


class Mesh:
    def __init__(self, shape = None):
        """A Mesh object contains a mesh

        :param shape:
            OCC shape.
        """
        self.shape = shape
        self.mesh = None

        self.points = []
        self.cells = []

        self._dim = None

    @property
    def dim(self) -> float | None:
        """Mesh dimension.

        :return:
            float or None if mesh contains no points.
        """
        return None if len(self.points) == 0 else self.points[0].size

    @property
    def geometry(self) -> ng_occ.OCCGeometry | None:
        """Netgen OCCGeometry object.

        :return:
            OCCGeometry object that can be used for meshing
            or None if shape is not defined.
        """
        if self.shape is not None:
            if hasattr(self.shape, "geometry"):
                return self.shape.geometry
            
            else:
                return ng_occ.OCCGeometry(self.shape)

        return None

    def generate(
        self, 
        parameters: ng_meshing.MeshingParameters = None, 
        refineSteps: int = 0, 
        refineOptimize: bool = True,
        scale: float = 0
    ):
        """Generate mesh using netgen mesher on occ geometry.

        :param parameters:
            Meshing parameters object.
        :param refineSteps:
            Refine mesh after main meshing.
        :param refineOptimize:
            If True, optimize surface and volume mesh after each refine step.
        :param scale:
            Scale mesh after all operations.
        """
        if not self.geometry:
            raise NoGeometrySpecified("Cannot build mesh without geometry")
    
        parameters = parameters or MeshingParameters()
        #   generate volume mesh
        mesh = self.geometry.GenerateMesh(parameters.get())

        if refineSteps > 0:
            for n in range(refineSteps):
                mesh.Refine()
            
            #   optimize surface and volume mesh
            if refineOptimize:
                mesh.OptimizeMesh2d(parameters.get())
                mesh.OptimizeVolumeMesh(parameters.get())
        
        if scale > 0:
            mesh.Scale(scale)
        
        self.points = utils.extract_netgen_points(mesh)
        self.cells = []

        if mesh.dim == 3:
            volume_cells, volume_indices = utils.extract_netgen_cells(mesh, 3)
            self.cells += utils.collect_cells(volume_cells, 3, volume_indices)

            surface_cells, surface_indices = utils.extract_netgen_cells(mesh, 2)
            cell_blocks = utils.collect_cells(surface_cells, 2, surface_indices)

            for cellBlock in cell_blocks:
                cellBlock.is_boundary = True
            
            self.cells += cell_blocks
        
        # TODO: dim == 2

        return self

    def read(self, filename: str):
        """Import a mesh from the file.
        
        :param filename:
            Path of the file.
        """        
        path = pathlib.Path(filename).resolve()
        ext = path.suffix[1: ]

        #   Force netgen neutral format
        if ext == "mesh":
            self.points, self.cells = conversion.read_neutral(path)

        else:
            mesh = meshio.read(path)
            self.points = mesh.points
            self.cells = mesh.cells
        
        return self

    def write(self, filename: PathLike):
        """Export mesh to the file.
        
        :param filename:
            Path of the file to store the given mesh in.
        """     
        path = pathlib.Path(filename).resolve()
        ext = path.suffix[1: ]
        
        #   Force netgen neutral format
        if ext == "mesh":
            conversion.write_neutral(self.points, self.cells, self.dim, path)

        else:
            mesh = meshio.Mesh(self.points, self.cells)
            mesh.write(path)

    @property
    def volumes(self) -> list[ndarray]: 
        """Volumes.

        :return:
            List of points.
        """
        points = []

        for cellBlock in self.cells:
            if cellBlock.dim == 3:
                points += [ *self.points[cellBlock.data] ]

        return points

    @property
    def volume(self) -> float:
        """Volume of whole mesh.
        
        :return:
            Volume.
        """
        return np.sum([ metrics.volume(cell) for cell in self.volumes ]) 

    @property
    def faces(self) -> list[ndarray]: 
        """Boundary faces.

        :return:
            List of boundary faces.
        """
        points = []

        for cellBlock in self.cells:
            if cellBlock.dim == 2 and cellBlock.is_boundary:
                points += [ *self.points[cellBlock.data] ]

        return points 
