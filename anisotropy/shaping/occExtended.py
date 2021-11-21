# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from functools import wraps
from netgen import occ
import numpy


def add_method(cls):
    """Add method to existing class. Use it as decorator.
    """
    def decorator(func):
        @wraps(func) 
        def wrapper(self, *args, **kwargs): 
            return func(self, *args, **kwargs)

        setattr(cls, func.__name__, wrapper)
        
        return func
    return decorator


@add_method(occ.gp_Pnt)
def pos(self) -> numpy.array:
    return numpy.array([self.x, self.y, self.z])


# ISSUE: netgen.occ.Face.Extrude: the opposite face has the same name and normal vector as an initial face.
def reconstruct(shape):
    """Reconstruct shape with new objects. 

    Warning: not works with curved edges.
    """
    facesNew = []

    for face in shape.faces:
        edgesNew = []
        for edge in face.edges:
            v = edge.vertices
            edgesNew.append(occ.Segment(v[0].p, v[1].p))

        faceNew = occ.Face(occ.Wire(edgesNew))
        faceNew.name = face.name
        facesNew.append(faceNew)

    return numpy.array(facesNew).sum()


