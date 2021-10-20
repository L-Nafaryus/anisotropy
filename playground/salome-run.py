# -*- coding: utf-8 -*-

import sys; path = "/home/nafaryus/projects/anisotropy"; sys.path.extend([path, path + "/env/lib/python3.10/site-packages"])
from anisotropy.samples.faceCentered import FaceCentered, FaceCenteredMesh
fc = FaceCentered([1, 0, 0], 0.12, filletsEnabled = True)
fc.build()
fcm = FaceCenteredMesh(fc)
fcm.build()
