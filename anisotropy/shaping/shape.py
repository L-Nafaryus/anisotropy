# -*- coding: utf-8 -*-

from __future__ import annotations
from numpy import ndarray
from os import PathLike

import numpy as np
import netgen.occ as ng_occ
import pathlib

from . import utils


class Shape(object):
    def __init__(self):
        """A Shape object contains OCC shape.
        """
        self.groups = {}
        self.shape = None

    @property
    def geometry(self) -> ng_occ.OCCGeometry:
        """Shape as OCCGeometry object.
        """
        return ng_occ.OCCGeometry(self.shape)
    
    @property
    def type(self) -> ng_occ.TopAbs_ShapeEnum:
        """Type of the shape. (shortcut)
        """
        return self.shape.type
    
    @property
    def volume(self) -> float:
        """Volume of the shape. (shortcut)
        """
        return self.shape.volume

    @property
    def center(self) -> ndarray:
        """Center of the shape.
        """
        return np.array(utils.pos(self.shape.center))

    def write(self, filename: PathLike):
        """Export a shape to the file.
        Supported formats: step.
        
        :param filename:
            Path of the file.
        """
        path = pathlib.Path(filename).resolve()
        ext = path.suffix[1: ]
        
        if ext == "step":
            self.shape.WriteStep(str(path))
        
        else:
            raise NotImplementedError(f"Shape format '{ ext }' is not supported")
            
    def read(self, filename: PathLike):
        """Import a shape from the file.
        Supported formats: step, iges, brep.

        :param filename:
            Path of the file.
        """        
        path = pathlib.Path(filename).resolve()
        ext = path.suffix[1: ]

        if ext in ["step", "iges", "brep"]:
            self.shape = ng_occ.OCCGeometry(str(path)).shape

        else:
            raise NotImplementedError(f"Shape format '{ext}' is not supported")
        
        return self

    def patches(
        self, 
        group: bool = False, 
        shiftIndex: bool = False, 
        prefix: str = None
    ) -> list | dict:
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
