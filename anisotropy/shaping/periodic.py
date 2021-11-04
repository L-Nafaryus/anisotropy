# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from netgen.occ import *
from numpy import pi, sqrt, cos, arccos, fix 

from . import Shape


class Periodic(Shape):
    def __init__(
        self,
        alpha: float = None,
        r0: float = 1,
        #L: float = None,
        #radius: float = None,
        filletsEnabled: bool = True,
        #fillets: float = None,
        gamma = None,
        **kwargs
    ):
        """Constructor method.
        
        :param alpha:
            Spheres overlap parameter.
        
        :param r0:
            Initial spheres radius.
        
        :param filletsEnabled:
            Enable fillets beetween spheres.
        """
        Shape.__init__(self)
        
        #   Parameters
        self.alpha = alpha
        self.r0 = r0

        self.theta = 0.5 * pi

        self.gamma = gamma or pi - 2 * (0.5 * self.theta)
        self.filletsEnabled = filletsEnabled
        self.filletsScale = 0.8
        
        # scale parameters for precision boolean operations
        self.maximize = 1e+2
        self.minimize = 1e-2

    
    @property
    def L(self):
        """(Override) Parameter depending on the ``r0``.
        """
        pass

    @property
    def radius(self):
        """Spheres radius
        """
        return self.r0 / (1 - self.alpha)

    @property
    def fillets(self):
        analytical = self.r0 * sqrt(2) / sqrt(1 - cos(self.gamma)) - self.radius
        # ISSUE: MakeFilletAll : Fillet can't be computed on the given shape with the given radius.
        # Temporary solution: degrade the precision (minRound <= analytical).
        rTol = 3
        minRound = fix(10 ** rTol * analytical) * 10 ** -rTol

        return minRound * self.filletsScale

    def lattice(self, 
        theta = 0.5 * pi
    ):
        zero = Pnt(0, 0, 0)
        maximize = 1e+2
        minimize = 1e-2

        #   Lattice
        spheres = numpy.array([], dtype = object)

        for zn in range(3):
            z = zn * self.L
            for yn in range(3):
                y = yn * self.L
                for xn in range(3):
                    x = xn * self.L
                    spheres = numpy.append(spheres, Sphere(Pnt(x, y, z), self.radius))

        lattice = spheres.sum()
        lattice = lattice.Scale(zero, maximize)

        if self.filletsEnabled:
            lattice = lattice.MakeFillet(lattice.edges, self.fillets * maximize)

        self.lattice = lattice.Scale(zero, minimize)
