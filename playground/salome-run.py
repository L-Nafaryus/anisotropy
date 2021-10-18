# -*- coding: utf-8 -*-

import sys; path = "/home/nafaryus/projects/anisotropy"; sys.path.extend([path, path + "/env/lib/python3.10/site-packages"])
from anisotropy.samples import Simple, FaceCentered, BodyCentered
s = Simple([1, 0, 0], 0.28, filletsEnabled = True)
