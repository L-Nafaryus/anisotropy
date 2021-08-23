# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from .application import application

def decomposePar(case: str = None):
    application("decomposePar", case = case, stderr = True)

