# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import numpy as np
from numpy import ndarray

from . import utils


def volume(points: ndarray) -> ndarray:
    """Volume of the cell.

    :param points:
        Array of points that represents volumetric cell.
    :return:
        Volume.
    """
    cellType = utils.cell_type(3, len(points))

    if cellType == "tetra":
        return 1 / 6 * np.linalg.det(np.append(points.transpose(), np.array([[1, 1, 1, 1]]), axis = 0))
    
    else:
        raise Exception(f"Not supported cell type '{ cellType }'")


def area(points: ndarray) -> ndarray:
    """Area of the cell.

    :param points:
        Array of points that represents surface cell.
    :return:
        Area.
    """
    cellType = utils.cell_type(2, len(points))
    vecs = np.roll(points, shift = -1, axis = 0) - points

    if cellType == "triangle":
        return 0.5 * np.abs(np.cross(*vecs[ :-1]))

    else:
        raise Exception(f"Not supported cell type '{ cellType }'")
