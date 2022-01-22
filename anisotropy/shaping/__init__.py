# -*- coding: utf-8 -*-
"""
Shaping is a library for using OCC shapes, provides more convient
functionality with power NumPy and Python OOP and contains interesing
primitives.
"""

from . import utils

from .shape import Shape
from .periodic import Periodic

from . import primitives


__all__ = [
    "utils",
    "primitives",
    "Shape",
    "Periodic"
]
