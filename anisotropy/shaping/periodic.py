# -*- coding: utf-8 -*-

import numpy as np

from . import Shape


class Periodic(Shape):
    def __init__(
        self,
        alpha: float = None,
        r0: float = 1,
        L: float = None,
        filletsEnabled: bool = True,
        gamma = None,
        **kwargs
    ):
        """A Periodic object contains periodic structure.
        
        :param alpha:
            Spheres overlap parameter.
        :param r0:
            Initial spheres radius.
        :param L:
            Side length of periodic cell. Depends on r0.
        :param gamma:
            Angle between lines that connect centers of spheres.
        :param filletsEnabled:
            If True, calculate fillets beetween spheres.
        """
        Shape.__init__(self)
        
        #   Parameters
        self.alpha = alpha
        self.r0 = r0
        self.L = L

        #   for lattice
        # self.theta = 0.5 * pi

        self.gamma = gamma or np.pi - 2 * (0.5 * 0.5 * np.pi)
        self.filletsEnabled = filletsEnabled
        self.filletsScale = 0.8
        
        #   scale parameters for precision boolean operations
        self.maximize = 1e+2
        self.minimize = 1e-2

    @property
    def radius(self) -> float:
        """Spheres radius

        :return:
            Radius.
        """
        return self.r0 / (1 - self.alpha)

    @property
    def fillets(self):
        """Fillets radius beetween spheres.

        :return:
            Radius.
        """
        analytical = self.r0 * np.sqrt(2) / np.sqrt(1 - np.cos(self.gamma)) - self.radius
        rTol = 3
        minRound = np.fix(10 ** rTol * analytical) * 10 ** -rTol

        return minRound * self.filletsScale
