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

