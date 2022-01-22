# -*- coding: utf-8 -*-

from numpy import ndarray

import numpy as np
import netgen.occ as ng_occ


def pos(point: ng_occ.gp_Pnt) -> ndarray:
    """Extract coordinates from point.

    :param point:
        OCC point object
    :return:
        Array of coordinates.
    """
    return np.array([ point.x, point.y, point.z ])


def normal(face: ng_occ.Face) -> ndarray: 
    """Calculate normal vector from face.

    :param face:
        OCC face object.
    :return:
        Normal vector from face.
    """
    _, u, v = face.surf.D1(0, 0)

    return np.cross([u.x, u.y, u.z], [v.x, v.y, v.z]) 


def angle(vec1: ndarray, vec2: ndarray) -> float:
    """Angle between two vectors.

    :param vec1:
        Array of points that represents first vector.
    :param vec2:
        Array of points that represents second vector.
    :return:
        Angle between two vectors in radians.
    """
    inner = np.inner(vec1, vec2)
    norms = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    cos = inner / norms

    return np.arccos(np.clip(cos, -1.0, 1.0))
