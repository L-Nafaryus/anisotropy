# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from netgen.occ import *
import numpy
from numpy import linalg
import os


class ShapeError(Exception):
    pass


class Shape(object):
    def __init__(self):
        self.groups = {}
        self.shape = None

    def export(self, filename: str):
        """Export a shape.
        
        Supported formats: step.
        
        :param filename:
            Name of the file to store the given shape in.
        
        :return:
            Output, error messages and returncode
        """
        out, err, returncode = "", "", 0
        ext = os.path.splitext(filename)[1][1: ]
        
        try:
            if ext == "step":
                self.shape.WriteStep(filename)
            
            else:
                raise NotImplementedError(f"{ ext } is not supported")
            
        except NotImplementedError as e:
            err = e
            returncode = 1
        
        except Exception as e:
            err = e
            returncode = 1
        
        return out, err, returncode

    def load(self, filename: str):
        ext = os.path.splitext(filename)[1][1:]

        if ext in ["step", "iges", "brep"]:
            self.shape = OCCGeometry(filename).shape

        else:
            raise NotImplementedError(f"Shape format '{ext}' is not supported")
        
        return self

    def patches(self, group: bool = False, shiftIndex: bool = False, prefix: str = None):
        """Get patches indices with their names.

        :param group:
            Group indices together with the same patches names.

        :param shiftIndex:
            Start numerating with one instead of zero.

        :param prefix:
            Add string prefix to the index.

        :return:
            List if group = False else dictionary.
        """
        if group:
            patches_ = {}

            for idn, face in enumerate(self.shape.faces):
                if shiftIndex:
                    idn += 1

                item = idn if not prefix else prefix + str(idn)
                
                if patches_.get(face.name):
                    patches_[face.name].append(item)

                else:
                    patches_[face.name] = [ item ]

        else:
            patches_ = []

            for idn, face in enumerate(self.shape.faces):
                if shiftIndex:
                    idn += 1
                
                item = idn if not prefix else prefix + str(idn)

                patches_.append((item, face.name))

        return patches_ 

    def normal(self, face: FACE) -> numpy.array:
        """
        :return:
            Normal vector to face.
        """
        _, u, v = face.surf.D1(0, 0)

        return numpy.cross([u.x, u.y, u.z], [v.x, v.y, v.z]) 


    def angle(self, vec1: numpy.array, vec2: numpy.array) -> float:
        """
        :return:
            Angle between two vectors in radians.
        """
        inner = numpy.inner(vec1, vec2)
        norms = linalg.norm(vec1) * linalg.norm(vec2)
        cos = inner / norms

        return numpy.arccos(numpy.clip(cos, -1.0, 1.0))
