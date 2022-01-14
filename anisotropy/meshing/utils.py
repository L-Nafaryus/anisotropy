from meshio._mesh import topological_dimension
from meshio._common import num_nodes_per_cell
from numpy import array


def detectTopology(dimension: dict, num_nodes: dict):
    for dim in topological_dimension.keys():
        for num in num_nodes_per_cell.keys():
            if topological_dimension[dim] == dimension and num_nodes_per_cell[num] == num_nodes and dim == num:
                return dim


def extractPoints(points):
    return array([ point.p for point in points ], dtype = float)


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
