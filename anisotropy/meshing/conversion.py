
from numpy import ndarray
from os import PathLike

import numpy as np
from pathlib import Path

from . import utils


def write_neutral(
    points: ndarray, 
    cells: list[utils.CellBlock], 
    dim: int, 
    filename: PathLike
):
    """Write mesh to the netgen file (Neutral format [.mesh]).

    :param points:
        Array of points.
    :param cells:
        List of cell blocks.
    :param dim:
        Dimension of the mesh.
    :param filename:
        Path of the file.
    """
    precision = "6f"
    floatValue = "{value:>{width}." + precision + "}"
    intValue = "{value:>{width}}"
    outfile = open(Path(filename).resolve(), "w")

    #   write points
    outfile.write(str(len(points)) + "\n")

    for n in range(len(points)):
        point = points[n]

        outfile.write(floatValue.format(value = point[0], width = 10) + " ")
        outfile.write(floatValue.format(value = point[1], width = 9) + " ")

        if dim == 3:
            outfile.write(floatValue.format(value = point[2], width = 9) + " ")

        outfile.write("\n")
    
    #   write volume cells
    if dim == 3:
        count = sum([ len(cell.data) for cell in cells if cell.dim == 3])
        outfile.write(str(count) + "\n")

        for cellBlock in cells:
            if cellBlock.dim == 3:
                for cell in cellBlock.data:
                    outfile.write(intValue.format(value = 1, width = 4))

                    for pointId in cell:
                        outfile.write(" ")
                        #   shift id up, in netgen it starts from one
                        outfile.write(intValue.format(value = pointId + 1, width = 8))
                    
                    outfile.write("\n")
    
    #   write faces
    count = sum([ len(cell.data) for cell in cells if cell.dim == 2])
    outfile.write(str(count) + "\n")

    for cellBlock in cells:
        if cellBlock.dim == 2:
            for index, cell in zip(cellBlock.indices, cellBlock.data):
                outfile.write(intValue.format(value = index, width = 4) + "    ")

                for pointId in cell:
                    outfile.write(" ")
                    #   shift id up, in netgen it starts from one
                    outfile.write(intValue.format(value = pointId + 1, width = 8))

                outfile.write("\n")

    #   write segments
    #   important?


def read_neutral(filename: PathLike) -> tuple[list, list]:
    """Read mesh from netgen file (Neutral format [.mesh]).

    :param filename:
        Path of the file.
    :return:
        List of points and list of cell blocks.
    """
    infile = open(Path(filename).resolve(), "r")

    #   read points from file, starts with single integer
    npoints = int(infile.readline())
    points = [] 

    for n in range(npoints):
        points.append(np.fromstring(infile.readline(), dtype = float, sep = " "))

    #   dimension
    dim = None if len(points) == 0 else points[0].size

    #   read volume cells
    nvolumes = int(infile.readline())
    volume_indices = []
    volumes = []

    for n in range(nvolumes):
        data = np.fromstring(infile.readline(), dtype = int, sep = " ")
        volume_indices.append(data[0])
        #   shift node indices down, in netgen it starts from one, need from zero
        volumes.append(data[1: ] - 1)
    
    #   read surface cells
    nsurfaces = int(infile.readline())
    surface_indices = []
    surfaces = []

    for n in range(nsurfaces):
        data = np.fromstring(infile.readline(), dtype = int, sep = " ")
        surface_indices.append(data[0])
        #   shift node indices down, in netgen it starts from one, need from zero
        surfaces.append(data[1: ] - 1)
    
    #   read segment cells
    #   important?

    #   write data to object
    points = np.asarray(points)
    cells = []

    if len(volumes) > 0:
        cells += utils.collect_cells(volumes, 3, volume_indices)

    if len(surfaces) > 0:
        cellBlocks = utils.collect_cells(surfaces, 2, surface_indices)

        if dim == 3:
            for cellBlock in cellBlocks:
                cellBlock.is_boundary = True
        
        cells += cellBlocks

    return points, cells 
