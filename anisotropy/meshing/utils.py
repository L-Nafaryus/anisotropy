from __future__ import annotations
from netgen import meshing
from meshio._mesh import topological_dimension
from meshio._common import num_nodes_per_cell
from numpy import array, asarray, ndarray

def detectCellType(dimension: int, num_nodes: int):
    for dim in topological_dimension.keys():
        for num in num_nodes_per_cell.keys():
            if topological_dimension[dim] == dimension and num_nodes_per_cell[num] == num_nodes and dim == num:
                return dim

class CellBlock:
    def __init__(self, cellType: str, data: list | ndarray, tags: list[str] | None = None):
        self.type = cellType
        self.data = data

        if cellType.startswith("polyhedron"):
            self.dim = 3
        
        else:
            self.data = asarray(self.data)
            self.dim = topological_dimension[cellType]

        self.tags = [] if tags is None else tags

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

def extractNetgenPoints(mesh: meshing.Mesh) -> ndarray:
    return array([ point.p for point in mesh.Points() ], dtype = float)


def extractNetgenCells(dim: int, mesh: meshing.Mesh) -> list[CellBlock]:
    cellsDict = {}
    elements = {
        0: mesh.Elements0D(),
        1: mesh.Elements1D(),
        2: mesh.Elements2D(),
        3: mesh.Elements3D()
    }[dim]

    if len(elements) == 0:
        return []

    for cell in elements:
        cellType = detectCellType(dim, len(cell.points))
        #   shift indicies, they should start from zero
        cellNew = array([ pointId.nr for pointId in cell.points ], dtype = int) - 1

        if cellsDict.get(cellType):
            cellsDict[cellType].append(cellNew)

        else:
            cellsDict[cellType] = [ cellNew ] 

    cells = [ CellBlock(key, value) for key, value in cellsDict.items() ]        

    return cells 
