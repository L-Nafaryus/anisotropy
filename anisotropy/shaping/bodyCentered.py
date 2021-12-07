# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from netgen.occ import *
import numpy
from numpy import pi, sqrt, arccos

from .occExtended import *
from . import Periodic

class BodyCentered(Periodic):
    def __init__(
        self,
        direction: list = None,
        **kwargs
    ):
        Periodic.__init__(
            self,
            alpha = kwargs.get("alpha", 0.01),
            r0 = kwargs.get("r0", 1),
            filletsEnabled = kwargs.get("filletsEnabled", True),
            gamma = pi - 2 * arccos(sqrt(2 / 3))
        )

        #   Parameters
        self.direction = direction
        self.alphaMin = 0.01
        self.alphaMax = 0.18

        #   Objects
        self.lattice = None
        self.cell = None
        self.shape = None

    
    @property
    def L(self):
        return self.r0 * 4 / sqrt(3)


    def build(self):
        #   
        zero = Pnt(0, 0, 0)

        #   Lattice
        spheres = numpy.array([], dtype = object)

        for zn in range(3):
            z = zn * self.L
            z2 = z - 0.5 * self.L

            for yn in range(3):
                y = yn * self.L
                y2 = y - 0.5 * self.L

                for xn in range(3):
                    x = xn * self.L
                    x2 = x - 0.5 * self.L

                    spheres = numpy.append(spheres, Sphere(Pnt(x, y, z), self.radius))
                    # shifted
                    spheres = numpy.append(spheres, Sphere(Pnt(x2, y2, z2), self.radius))

        lattice = spheres.sum()
        lattice = lattice.Scale(zero, self.maximize)

        if self.filletsEnabled:
            lattice = lattice.MakeFillet(lattice.edges, self.fillets * self.maximize)

        self.lattice = lattice.Scale(zero, self.minimize)
        
        #   Inlet face
        if (self.direction == numpy.array([1., 0., 0.])).prod():
            length = 2 * self.r0
            width = self.L / 2
            diag = self.L * sqrt(2)
            height = self.L

            xl = sqrt(diag ** 2 + diag ** 2) * 0.5
            yw = xl
            zh = height

            vertices = numpy.array([
                (xl, 0, 0),
                (0, yw, 0),
                (0, yw, zh),
                (xl, 0, zh)
            ])
            extr = diag

        elif (self.direction == numpy.array([0., 0., 1.])).prod():
            length = 2 * self.r0
            width = self.L / 2
            diag = self.L * sqrt(2)
            height = self.L

            xl = sqrt(diag ** 2 + diag ** 2) * 0.5
            yw = xl
            zh = height

            vertices = numpy.array([
                (0, yw, 0),
                (xl, 0, 0),
                (2 * xl, yw, 0),
                (xl, 2 * yw, 0)
            ])
            extr = height

        elif (self.direction == numpy.array([1., 1., 1.])).prod():
            length = 2 * self.r0
            width = self.L / 2
            diag = self.L * sqrt(2)
            height = diag / 3

            xl = -self.L / 4
            yw = -self.L / 4
            zh = -self.L / 4

            vertices = numpy.array([
                (self.L / 3 + xl, self.L / 3 + yw, 4 * self.L / 3 + zh),
                (self.L + xl, 0 + yw, self.L + zh),
                (4 * self.L / 3 + xl, self.L / 3 + yw, self.L / 3 + zh),
                (self.L + xl, self.L + yw, 0 + zh),
                (self.L / 3 + xl, 4 * self.L / 3 + yw, self.L / 3 + zh),
                (0 + xl, self.L + yw, self.L + zh)
            ])
            extr = self.L * sqrt(3) 

        else:
            raise Exception(f"Direction { self.direction } is not implemented")

        #   Cell
        circuit = Wire([ Segment(Pnt(*v1), Pnt(*v2)) for v1, v2 in zip(vertices, numpy.roll(vertices, -1, axis = 0)) ])
        inletface = Face(circuit)
        inletface.name = "inlet"

        vecFlow = self.normal(inletface)
        # ISSUE: don't use face.Extrude(length), only face.Extrude(length, vector) 
        self.cell = inletface.Extrude(extr, Vec(*vecFlow))
        
        #   Boundaries
        symetryId = 0

        for face in self.cell.faces:
            fNorm = self.normal(face)
            fAngle = self.angle(vecFlow, fNorm)
            
            if fAngle == 0 or fAngle == numpy.pi:
                if (face.center.pos() == inletface.center.pos()).prod():
                    face.name = "inlet"

                else:
                    face.name = "outlet"

            else:
                face.name = f"symetry{ symetryId }"
                symetryId += 1

        #   Main shape
        self.shape = self.cell - self.lattice

        for face in self.shape.faces:
            if face.name not in ["inlet", "outlet", *[ f"symetry{ n }" for n in range(6) ]]:
                face.name = "wall"
