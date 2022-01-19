# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import numpy
from numpy import ndarray
from numpy import linalg
from .utils import detectCellType


def volume(points: ndarray) -> ndarray:
    cellType = detectCellType(3, len(points))

    if cellType == "tetra":
        return 1 / 6 * linalg.det(numpy.append(points.transpose(), numpy.array([[1, 1, 1, 1]]), axis = 0))
    
    else:
        raise Exception(f"Not supported cell type '{ cellType }'")

