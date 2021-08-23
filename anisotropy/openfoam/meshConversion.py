# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from .application import application

def ideasUnvToFoam(mesh: str, case: str = None) -> (str, int):
    return application("ideasUnvToFoam", mesh, case = case, stderr = True)

