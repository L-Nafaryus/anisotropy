from netgen.meshing import Mesh as netgenMesh
from meshio import Mesh as meshioMesh
from meshio._mesh import topological_dimension
from meshio._common import num_nodes_per_cell
from numpy import array

meshfile = "mesh.mesh"

mesh = netgenMesh()
mesh.Load(meshfile)

def detectTopology(dimension: dict, num_nodes: dict):
    for dim in topological_dimension.keys():
        for num in num_nodes_per_cell.keys():
            if topological_dimension[dim] == dimension and num_nodes_per_cell[num] == num_nodes and dim == num:
                return dim

def extractCells(dimension: int, elements):
    cellsNew = {}

    for cell in elements:
        cellTopo = detectTopology(dimension, len(cell.points))
        #   shift indicies, they should starts from zero
        cellNew = array([ pointId.nr for pointId in cell.points ], dtype = int) - 1

        if cellsNew.get(cellTopo):
            cellsNew[cellTopo].append(cellNew)

        else:
            cellsNew[cellTopo] = [ cellNew ] 
        
    return cellsNew

def extractPoints(points):
    return array([ point.p for point in mesh.Points() ], dtype = float)

points = extractPoints(mesh.Points())
cells1d = extractCells(1, mesh.Elements1D())   
cells2d = extractCells(2, mesh.Elements2D())   
cells3d = extractCells(3, mesh.Elements3D())   
cells = [
    *[ e for e in cells1d.items() ],
    *[ e for e in cells2d.items() ],
    *[ e for e in cells3d.items() ]
]

meshNew = meshioMesh(points, cells)