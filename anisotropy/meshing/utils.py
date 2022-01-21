from __future__ import annotations
from numpy import ndarray

import numpy as np
import netgen.meshing as ng_meshing
import meshio


topo_dim = meshio._mesh.topological_dimension
cell_nodes = meshio._common.num_nodes_per_cell


def cell_type(dimension: int, num_nodes: int) -> str | None:
    """Detect a cell topology type.

    :param dimension:
        Cell dimension.
    :param num_nodes:
        Number of nodes in the cell.
    :return:
        Cell type or None if cell type if not supported. 
    """
    for dim in topo_dim.keys():
        for num in cell_nodes.keys():
            if (
                topo_dim[dim] == dimension and 
                cell_nodes[num] == num_nodes and 
                dim == num
            ):
                return dim
    
    return None 


class CellBlock:
    def __init__(
        self, 
        cellType: str, 
        data: list | ndarray, 
        tags: list[str] = [],
        indices: list | ndarray = [],
        is_boundary: bool = False,
        names: list[str] = []
    ):
        """A CellBlock object contains cells information of the same type.

        :param cellType:
            Type of the cell.
        :param data:
            Array of cells.
        :param tags:
            Some cell tags.
        :param indices:
            Array of indices of cells. Must be the same length as data length.
            Usefull for detecting boundary faces, etc.
        :param is_boundary:
            Flag that cells are not internal.
        :param names:
            Array of names of cells. Must be the same length as data length.
            Usefull for detecting boundary faces, etc.
        """
        self.type = cellType
        self.data = data

        if cellType.startswith("polyhedron"):
            self.dim = 3
        
        else:
            self.data = np.asarray(self.data)
            self.dim = topo_dim[cellType]

        self.tags = tags
        self.indices = np.asarray(indices)
        self.is_boundary = is_boundary 
        self.names = names

    def __repr__(self):
        items = [
            "CellBlock",
            f"type: { self.type }",
            f"num cells: { len(self.data) }",
            f"tags: { self.tags }",
        ]
        return "<" + ", ".join(items) + ">"

    def __len__(self):
        return len(self.data)


def collect_cells(cells: list, dim: int, indices: list | ndarray = None, cellType: str = None) -> list[CellBlock]:
    """Collect cell blocks from a list of cells.

    :param cells:
        List of cells.
    :param dim:
        Cell dimension.
    :param indices:
        List of cell indices. Must be the same length as list of cells.
    :return:
        List of cell blocks.
    """ 
    cellBlocks = []

    if indices is not None:
        assert len(cells) == len(indices), "cells and indices arrays must be the same length"
    
    for n, cell in enumerate(cells):
        cellType = cellType or cell_type(dim, len(cell))
        index = indices[n] if indices else None
        is_added = False
        
        #   update cell block
        for cellBlock in cellBlocks:
            if cellBlock.type == cellType:
                cellBlock.data += [ cell ]

                if index:
                    cellBlock.indices.append(index)

                is_added = True

        #   or create new                
        if not is_added:
            cellBlock = CellBlock(cellType, [])
            cellBlock.data = [ cell ]

            if index:
                cellBlock.indices = [ index ]

            cellBlocks.append(cellBlock)

    #   convert arrays to numpy    
    for cellBlock in cellBlocks:
        cellBlock.data = np.asarray(cellBlock.data)
        cellBlock.indices = np.asarray(cellBlock.indices)

    return cellBlocks


def extract_netgen_points(mesh: ng_meshing.Mesh) -> ndarray:
    """Extract points from netgen mesh object.

    :param mesh:
        Netgen mesh object.
    :return:
        Array of points.
    """
    return np.array([ point.p for point in mesh.Points() ], dtype = float)


def extract_netgen_cells(mesh: ng_meshing.Mesh, dim: int) -> tuple[list, list]:
    """Extract cells from netgen mesh according to cell dimension.

    :param mesh:
        Netgen mesh object.
    :param dim:
        Cell dimension.
    :return:
        List of cells and list of indices.
    """
    cells = []
    indices = []
    elements = {
        0: mesh.Elements0D(),
        1: mesh.Elements1D(),
        2: mesh.Elements2D(),
        3: mesh.Elements3D()
    }[dim]

    if len(elements) > 0:
        for cell in elements:
            #   shift nodes values, they should start from zero
            nodes = np.array([ node.nr for node in cell.points ], dtype = int) - 1
            cells.append(nodes)
            indices.append(cell.index)        
    
    return cells, indices
 
