# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from netgen.occ import *
import numpy
from numpy import pi, sqrt

from . import Periodic

class FaceCentered(Periodic):
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
            gamma = 2 / 3 * pi
        )

        #   Parameters
        self.direction = direction
        self.alphaMin = 0.01
        self.alphaMax = 0.13

        #   Objects
        self.lattice = None
        self.cell = None
        self.shape = None


    @property
    def L(self):
        return self.r0 * 4 / sqrt(2)
        

    def build(self):
        #   
        zero = Pnt(0, 0, 0)

        #   Lattice
        spheres = numpy.array([], dtype = object)
        x0 = 0#-0.5 * self.L * (3 - 1)
        x20 = 0#-0.5 * self.L * 3
        z0 = -0.5 * self.L * (3 - 2)
        z20 = -0.5 * self.L * (3 - 1)

        for zn in range(3):
            z = z0 + zn * self.L 
            z2 = z20 + zn * self.L 

            for yn in range(3):
                y = yn * 2 * self.r0
                y2 = yn * 2 * self.r0 + self.r0

                for xn in range(3):
                    x = x0 + xn * 2 * self.r0
                    x2 = x20 + xn * 2 * self.r0 + self.r0

                    # TODO: fix rotations (arcs intersection -> incorrect boolean operations
                    spheres = numpy.append(spheres, Sphere(Pnt(x, y, z), self.radius).Rotate(Axis(Pnt(x, y, z), X), 45).Rotate(Axis(Pnt(x, y, z), Z), 45))
                    # shifted
                    spheres = numpy.append(spheres, Sphere(Pnt(x2, y2, z2), self.radius).Rotate(Axis(Pnt(x2, y2, z2), X), 45).Rotate(Axis(Pnt(x2, y2, z2), Z), 45))


        lattice = spheres.sum()
        lattice = lattice.Move(Vec(-self.r0 * 2, -self.r0 * 2, 0)).Rotate(Axis(zero, Z), 45)
        lattice = lattice.Scale(zero, self.maximize)

        if self.filletsEnabled:
            lattice = lattice.MakeFillet(lattice.edges, self.fillets * self.maximize)

        self.lattice = lattice.Scale(zero, self.minimize)

        #   Inlet face
        if (self.direction == numpy.array([1., 0., 0.])).prod():
            length = 2 * self.r0
            width = self.L / 2
            diag = self.L * sqrt(3)
            height = diag / 3

            xl = sqrt(length ** 2 + length ** 2) * 0.5
            yw = xl
            zh = width

            vertices = numpy.array([
                (0, 0, -zh),
                (-xl, yw, -zh),
                (-xl, yw, zh),
                (0, 0, zh)
            ])
            extr = length

        elif (self.direction == numpy.array([0., 0., 1.])).prod():
            length = 2 * self.r0
            width = self.L / 2
            diag = self.L * sqrt(3)
            height = diag / 3

            xl = sqrt(length ** 2 + length ** 2) * 0.5
            yw = xl
            zh = width

            vertices = numpy.array([
                (0, 0, -zh),
                (xl, yw, -zh),
                (0, 2 * yw, -zh),
                (-xl, yw, -zh)
            ])
            extr = 2 * width

        elif (self.direction == numpy.array([1., 1., 1.])).prod():
            length = 2 * self.r0
            width = self.L / 2
            diag = self.L * sqrt(3)
            height = diag / 3

            xl = -(3 - 2) * self.L / 3
            yw = -(3 - 2) * self.L / 3
            zh = -(3 - 2) * self.L / 3

            vertices = numpy.array([
                (-2 * width / 3 + xl, -2 * width / 3 + yw, width / 3 + zh),
                (0 + xl, -width + yw, 0 + zh),
                (width / 3 + xl, -2 * width / 3 + yw, -2 * width / 3 + zh),
                (0 + xl, 0 + yw, -width + zh),
                (-2 * width / 3 + xl, width / 3 + yw, -2 * width / 3 + zh),
                (-width + xl, 0 + yw, 0 + zh)
            ])
            extr = sqrt(3) * self.L
            
        else:
            raise Exception(f"Direction { self.direction } is not implemented")
        
        #   Cell
        circuit = Wire([ Segment(Pnt(*v1), Pnt(*v2)) for v1, v2 in zip(vertices, numpy.roll(vertices, -1, axis = 0)) ])
        inletface = Face(circuit)
        inletface.name = "inlet"

        vecFlow = self.normal(inletface)
        self.cell = inletface.Extrude(extr)

        #   Boundaries
        symetryId = 0

        # ISSUE: inlet and outlet faces have the same name and normal vector after extrusion
        for face in self.cell.faces:
            fNorm = self.normal(face)
            fAngle = self.angle(vecFlow, fNorm)

            if fAngle == 0 and not face.center == inletface.center:
                face.name = "outlet"

            else:
                face.name = f"symetry{ symetryId }"
                symetryId += 1

        #   Main shape
        self.shape = self.cell - self.lattice

        for face in self.shape.faces:
            if face.name not in ["inlet", "outlet", *[ f"symetry{ n }" for n in range(6) ]]:
                face.name = "wall"


